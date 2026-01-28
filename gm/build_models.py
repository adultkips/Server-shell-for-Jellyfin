import html
from urllib.parse import quote
from .config import JELLYFIN_URL, SERVER_ID
from .get_persons import get_persons
from .person_movie_count import person_movie_count
from .person_tags import person_tags
from .tag_bar import tag_bar
def build_models(session, user_id):
    persons = get_persons(session, JELLYFIN_URL, user_id)
    seen_ids = set()
    dupe_rows = []
    orphans = []
    items = []
    tags_cache = {}
    models_img_map = {}
    X_ICON = "1337xicon.png"
    FPV_ICON = "fpvicon.ico"
    for p in persons:
        name = (p.get("Name") or "").strip()
        pid = p.get("Id")
        if not name or not pid:
            continue
        if pid in seen_ids:
            dupe_rows.append((name, pid))
            continue
        seen_ids.add(pid)
        count = person_movie_count(session, JELLYFIN_URL, user_id, pid)
        if count == 0:
            orphans.append((name, pid))
            continue
        if pid not in tags_cache:
            tags_cache[pid] = person_tags(session, JELLYFIN_URL, user_id, pid)
        items.append((name, pid, count, tags_cache[pid]))
        k = name.strip().lower()
        if k and k not in models_img_map:
            models_img_map[k] = pid
    if dupe_rows:
        print(f"INFO: Models: removed {len(dupe_rows)} duplicates (same Person ID).")
    if orphans:
        print(f"INFO: Models: filtered {len(orphans)} orphans (0 movies).")
    items.sort(key=lambda x: x[0].lower())
    tag_set = {}
    for _, __, ___, tags in items:
        for t in tags:
            tag_set[t.lower()] = t
    all_tags = [tag_set[k] for k in sorted(tag_set.keys())]
    lis = []
    for name, pid, count, tags in items:
        details_url = f"films.html?model={html.escape(name)}"
        jf_url = f"{JELLYFIN_URL}/web/index.html#/details?id={pid}&serverId={SERVER_ID}"
        img_url = f"{JELLYFIN_URL}/Items/{pid}/Images/Primary"
        q_1337x = f"{name} 1080p"
        x_url = f"https://1337x.to/sort-search/{quote(q_1337x)}/time/desc/1/"
        fpv_name = "-".join([p for p in name.split() if p])
        fpv_url = f"https://www.freepornvideos.xxx/models/{quote(fpv_name)}/"
        tags_norm = [t.lower() for t in tags]
        data_tags = "|" + "|".join(tags_norm) + "|" if tags_norm else ""
        tag_badges = ""
        if tags:
            tag_badges = "<div class='cardTags'>" + "".join(
                f"<button class='tagMini' type='button' data-tag='{html.escape(t.lower())}'>"
                f"{html.escape(t)}</button>"
                for t in tags
            ) + "</div>"
        lis.append(
            f"<li class='card' data-name='{html.escape(name).lower()}' data-count='{count}' "
            f"data-display='{html.escape(name)}' data-tags='{html.escape(data_tags)}'>"
            f"<a class='xBtn' href='{html.escape(x_url)}' target='_blank' rel='noopener' "
            f"title='Search on 1337x (1080p)' aria-label='Search on 1337x (1080p)' "
            f"style=\"background-image:url('{html.escape(X_ICON)}')\"></a>"
            f"<a class='fpvBtn' href='{html.escape(fpv_url)}' target='_blank' rel='noopener' "
            f"title='Search on FreePornVideos' aria-label='Search on FreePornVideos' "
            f"style=\"background-image:url('{html.escape(FPV_ICON)}')\"></a>"
            f"<a class='jfBtn' href='{jf_url}' target='_blank' rel='noopener' title='Open in Jellyfin'></a>"
            f"<a class='cardLink' href='{details_url}'>"
            f"<img class='thumb' src='{img_url}' onerror=\"this.style.display='none'\">"
            "<div class='cardBody'>"
            f"<div class='name'>{html.escape(name)} <span class='count'>({count})</span></div>"
            f"{tag_badges}"
            "</div>"
            "</a>"
            "</li>"
        )
    extra = tag_bar(all_tags)
    return "\n".join(lis), len(items), extra, models_img_map
