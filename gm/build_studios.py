import html
from .config import JELLYFIN_URL, SERVER_ID
from .get_studios import get_studios
from .studio_movie_count import studio_movie_count
def build_studios(session, user_id):
    studios = get_studios(session, JELLYFIN_URL, user_id)
    seen_ids = set()
    dupe_rows = []
    orphans = []
    items = []
    studios_img_map = {}
    for st in studios:
        name = (st.get("Name") or "").strip()
        sid = st.get("Id")
        if not name or not sid:
            continue
        if sid in seen_ids:
            dupe_rows.append((name, sid))
            continue
        seen_ids.add(sid)
        count = studio_movie_count(session, JELLYFIN_URL, user_id, sid)
        if count == 0:
            orphans.append((name, sid))
            continue
        items.append((name, sid, count))
        k = name.strip().lower()
        if k and k not in studios_img_map:
            studios_img_map[k] = sid
    if dupe_rows:
        print(f"INFO: Studios: removed {len(dupe_rows)} duplicates (same Studio ID).")
    if orphans:
        print(f"INFO: Studios: filtered {len(orphans)} orphans (0 movies).")
    items.sort(key=lambda x: x[0].lower())
    lis = []
    for name, sid, count in items:
        details_url = f"films.html?studio={html.escape(name)}"
        jf_url = f"{JELLYFIN_URL}/web/index.html#/details?id={sid}&serverId={SERVER_ID}"
        img_url = f"{JELLYFIN_URL}/Items/{sid}/Images/Primary"
        lis.append(
            f"<li class='card' data-name='{html.escape(name).lower()}' "
            f"data-count='{count}' data-display='{html.escape(name)}'>"
            f"<a class='jfBtn' href='{jf_url}' target='_blank' rel='noopener' title='Open in Jellyfin'></a>"
            f"<a class='cardLink' href='{details_url}'>"
            f"<img class='thumb' src='{img_url}' onerror=\"this.style.display='none'\">"
            "<div class='cardBody'>"
            f"<div class='name'>{html.escape(name)} <span class='count'>({count})</span></div>"
            "</div>"
            "</a>"
            "</li>"
        )
    return "\n".join(lis), len(items), studios_img_map
