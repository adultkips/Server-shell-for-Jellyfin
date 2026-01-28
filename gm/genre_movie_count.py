def genre_movie_count(session, base_url, user_id, genre_id) -> int:
    r = session.get(
        f"{base_url}/Items",
        params={
            "UserId": user_id,
            "IncludeItemTypes": "Movie",
            "Recursive": "true",
            "GenreIds": genre_id,
            "Limit": 0
        },
        timeout=20
    )
    r.raise_for_status()
    return (r.json().get("TotalRecordCount") or 0)
