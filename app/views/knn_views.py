from django.shortcuts import render
from app.utils.neo4j_connection import Neo4jConnection

def rekomendasi_paper_detail(request, paper_id):
    conn = Neo4jConnection()
    driver = conn.get_driver()

    with driver.session() as session:
        # Drop graph kalau ada
        session.run("CALL gds.graph.drop('detailGraph', false) YIELD graphName")

        # Project graph GDS
        session.run("""
            MATCH (p:Paper)
            RETURN gds.graph.project(
                'detailGraph',
                p,
                null,
                {
                    sourceNodeProperties: p { .embedding },
                    targetNodeProperties: {}
                }
             )
        """)

        node_id_result = session.run("""
            MATCH (p:Paper {paperId: $paper_id})
            RETURN id(p) AS nodeId, p.title AS title, p.paperId AS paperId, p.abstract AS abstract
        """, {"paper_id": paper_id})

        record = node_id_result.single()

        selected_node_id = record["nodeId"]
        selected_paper = {
            "paperId": record["paperId"],
            "title": record["title"],
            "abstract": record["abstract"]
        }


        # Query Degree Centrality
        result = session.run("""
            CALL gds.knn.stream('detailGraph', {
                topK: 5,
                nodeProperties: ['embedding'],
                randomSeed: 1337,
                concurrency: 1,
                sampleRate: 1.0,
                deltaThreshold: 0.0
            })
            YIELD node1, node2, similarity
            WHERE node1 = $selected_node_id
            RETURN gds.util.asNode(node2).paperId AS paperId,
                   gds.util.asNode(node2).title AS title,
                   similarity
            ORDER BY similarity DESC
        """, {"selected_node_id": selected_node_id})

        similar_papers = [
            {
                "paperId": record["paperId"],
                "title": record["title"],
                "similarity": record["similarity"]
            }
            for record in result
        ]

    conn.close()  # tutup koneksi setelah selesai
    return render(request, "knn_rekomendasi.html", {"paper": selected_paper, "similar_papers": similar_papers})
