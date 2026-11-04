from football_chatbot.db import get_connection

with get_connection() as conn:
    print(conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0], "articles")
    rows = conn.execute(
        """
        SELECT a.published_at, a.title, a.url
        FROM articles_fts JOIN articles a ON a.id = articles_fts.rowid
        WHERE articles_fts MATCH ?
        ORDER BY articles_fts.rank
        LIMIT 5
        """,
        ("Barcelona high line",),
    ).fetchall()
    for r in rows:
        print(r["published_at"], "|", r["title"])
    total = conn.execute("SELECT SUM(LENGTH(body)) FROM articles").fetchone()[0]
    print(f"{total / 1_000_000:.1f} MB of article text")