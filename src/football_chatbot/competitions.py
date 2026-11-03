COMPETITIONS = {
    "PD": ["la liga", "laliga", "primera division", "spanish league"],
    "PL": ["premier league", "epl", "english premier league"],
    "BL1": ["bundesliga", "german league"],
    "SA": ["serie a", "italian league"],
    "FL1": ["ligue 1", "french league"],
    "DED": ["eredivisie", "dutch league"],
    "PPL": ["primeira liga", "portuguese league"],
    "ELC": ["championship", "english championship"],
    "BSA": ["brasileirao", "serie a brazil", "brazilian league"],
    "CL": ["champions league", "ucl", "uefa champions league"],
    "WC": ["world cup", "fifa world cup"],
    "EC": ["euros", "euro", "european championship"],
}


def resolve_competition(text: str) -> str | None:
    t = text.strip().lower()
    for code, names in COMPETITIONS.items():
        if t == code.lower() or t in names:
            return code
    return None