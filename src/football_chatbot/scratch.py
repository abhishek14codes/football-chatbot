from football_chatbot.queries import get_team_results
from football_chatbot.teams import resolve_team

for n in ["Man United", "Man Utd", "Man City", "Arsenal"]:
    print(n, "->", resolve_team(n))

print()
for row in get_team_results("Man United", limit=3):
    print(row)