from django.shortcuts import render
from app.utils.neo4j_connection import Neo4jConnection

def rekomendasi_paper_berpengaruh(request):
    conn = Neo4jConnection()
    driver = conn.get_driver()

    with driver.session() as session:
        # Drop graph kalau ada
        session.run("CALL gds.graph.drop('pageGraph', false) YIELD graphName")

        # Project graph GDS
        session.run("""
            MATCH (source:Paper)-[r:CITES]->(target:Paper)
                RETURN gds.graph.project(
                'pageGraph',
                source,
                target
                )
        """)

        # Query Degree Centrality
        result = session.run("""
            CALL gds.pageRank.stream('pageGraph')
            YIELD nodeId, score
            RETURN gds.util.asNode(nodeId).title AS title, gds.util.asNode(nodeId).paperId AS paperId, score
            ORDER BY score DESC, title ASC
            LIMIT 10                    
        """)

        papers = [
            {
                "id": record["paperId"],
                "title": record["title"],
                "score": record["score"]
            }
            for record in result
        ]

    conn.close()  # tutup koneksi setelah selesai
    return render(request, "pagerank_rekomendasi.html", {"papers": papers})
