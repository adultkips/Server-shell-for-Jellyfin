def get_studios(session, base_url, user_id):
    endpoints = [
        (f"{base_url}/Studios", {
            "UserId": user_id,
            "SortBy": "SortName",
            "SortOrder": "Ascending",
            "Limit": 20000
        }),
        (f"{base_url}/Items", {
            "IncludeItemTypes": "Studio",
            "Recursive": "true",
            "UserId": user_id,
            "SortBy": "SortName",
            "SortOrder": "Ascending",
            "Limit": 20000
        }),
    ]
    for url, params in endpoints:
        r = session.get(url, params=params, timeout=30)
        if r.ok:
            data = r.json()
            return data["Items"] if isinstance(data, dict) else data
    raise RuntimeError("Could not fetch studios")
