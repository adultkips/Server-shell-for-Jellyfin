def get_movies(session, base_url, user_id):
    r = session.get(
        f"{base_url}/Items",
        params={
            "UserId": user_id,
            "IncludeItemTypes": "Movie",
            "Recursive": "true",
            "SortBy": "SortName",
            "SortOrder": "Ascending",
            "Limit": 20000,
            "Fields": "DateCreated,Genres,Studios,People,ProductionYear,UserData",
        },
        timeout=60,
    )
    r.raise_for_status()
    data = r.json()
    return data.get("Items") or []
