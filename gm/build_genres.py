import html
from .config import JELLYFIN_URL, SERVER_ID
from .get_genres import get_genres
from .genre_movie_count import genre_movie_count
def build_genres(session, user_id):
    genres = get_genres(session, JELLYFIN_URL, user_id)
    seen_ids = set()
    dupe_rows = []
    orphans = []
    items = []
    genres_img_map = {}
    for g in genres:
        name = (g.get("Name") or "").strip()
        gid = g.get("Id")
        if not name or not gid:
            continue
        if gid in seen_ids:
            dupe_rows.append((name, gid))
            continue
        seen_ids.add(gid)
        count = genre_movie_count(session, JELLYFIN_URL, user_id, gid)
        if count == 0:
            orphans.append((name, gid))
            continue
        items.append((name, gid, count))
        k = name.strip().lower()
        if k and k not in genres_img_map:
            genres_img_map[k] = gid
    if dupe_rows:
        print(f"INFO: Genres: removed {len(dupe_rows)} duplicates (same Genre ID).")
    if orphans:
        print(f"INFO: Genres: filtered {len(orphans)} orphans (0 movies).")
    items.sort(key=lambda x: x[0].lower())
    lis = []
    for name, gid, count in items:
        details_url = f"films.html?genre={html.escape(name)}"
        jf_url = f"{JELLYFIN_URL}/web/index.html#/details?id={gid}&serverId={SERVER_ID}"
        img_url = f"{JELLYFIN_URL}/Items/{gid}/Images/Primary"
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
    return "\n".join(lis), len(items), genres_img_map
