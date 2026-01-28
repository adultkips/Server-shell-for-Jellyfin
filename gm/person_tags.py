def person_tags(session, base_url, user_id, person_id):
    r = session.get(
        f"{base_url}/Users/{user_id}/Items/{person_id}",
        timeout=20
    )
    r.raise_for_status()
    data = r.json()
    tags = data.get("Tags") or []
    cleaned = []
    seen = set()
    for t in tags:
        tt = (t or "").strip()
        if not tt:
            continue
        key = tt.lower()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(tt)
    return cleaned
