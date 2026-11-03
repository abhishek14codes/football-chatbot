from football_chatbot.db import get_connection

with get_connection() as conn:
    for r in conn.execute(
        "SELECT competition, COUNT(*) AS n, "
        "MAX(CASE WHEN status='FINISHED' THEN utc_date END) AS last_played "
        "FROM matches GROUP BY competition ORDER BY n DESC"
    ):
        print(dict(r))