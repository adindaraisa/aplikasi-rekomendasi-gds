from django.shortcuts import render
from app.utils.neo4j_connection import Neo4jConnection

def rekomendasi_paper_populer(request):
    conn = Neo4jConnection()
    driver = conn.get_driver()

    with driver.session() as session:
        # Drop graph kalau ada
        session.run("CALL gds.graph.drop('myGraph', false) YIELD graphName")

        # Project graph GDS
        session.run("""
            MATCH (source:User)-[r:READ]->(target:Paper)
                RETURN gds.graph.project(
                'myGraph',
                target,
                source
                )
        """)

        # Query Degree Centrality
        result = session.run("""
            CALL gds.degree.stream('myGraph')
            YIELD nodeId, score
            WITH gds.util.asNode(nodeId) AS node, score
            WHERE node:Paper
            RETURN node.id AS paperId, node.title AS paperTitle, score AS readCount
            ORDER BY readCount DESC
            LIMIT 10
        """)

        papers = [
            {
                "id": record["paperId"],
                "title": record["paperTitle"],
                "readCount": int(record["readCount"])
            }
            for record in result
        ]

    conn.close()  # tutup koneksi setelah selesai
    return render(request, "degree_rekomendasi.html", {"papers": papers})
