import html
from datetime import datetime, timezone
from .config import JELLYFIN_URL, SERVER_ID
from .get_movies import get_movies
def _clean_list_str(values, limit=None):
    out = []
    for v in values or []:
        if isinstance(v, str):
            t = v.strip()
            if t:
                out.append(t)
    return out[:limit] if limit else out
def _extract_studios(studios_raw, limit=None):
    out = []
    for s in studios_raw or []:
        if isinstance(s, dict):
            n = (s.get("Name") or "").strip()
            if n:
                out.append(n)
        elif isinstance(s, str):
            n = s.strip()
            if n:
                out.append(n)
    return out[:limit] if limit else out
def _extract_people(people_raw, max_directors=1, max_actors=6):
    directors = []
    actors = []
    for p in people_raw or []:
        if not isinstance(p, dict):
            continue
        name = (p.get("Name") or "").strip()
        if not name:
            continue
        ptype = (p.get("Type") or "").strip().lower()
        if ptype == "director":
            directors.append(name)
        elif ptype == "actor":
            actors.append(name)
    def dedupe(seq):
        seen = set()
        out = []
        for x in seq:
            k = x.lower()
            if k in seen:
                continue
            seen.add(k)
            out.append(x)
        return out
    directors = dedupe(directors)[:max_directors]
    actors = dedupe(actors)[:max_actors]
    return directors, actors
def _pipewrap_lower(values):
    seen = set()
    clean = []
    for v in values or []:
        k = (v or "").strip().lower()
        if not k or k in seen:
            continue
        seen.add(k)
        clean.append(k)
    return "|" + "|".join(clean) + "|" if clean else ""
def _parse_datecreated(date_str: str):
    if not date_str:
        return "", 0
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        ts = int(dt.timestamp())
        disp = dt.astimezone(timezone.utc).strftime("%d/%m/%Y")
        return disp, ts
    except Exception:
        return "", 0
def _filter_buttons(items, kind, extra_cls="", display_prefix=""):
    out = []
    for s in items or []:
        raw = (s or "").strip()
        if not raw:
            continue
        val = raw.lower()
        label = f"{display_prefix}{raw}"
        out.append(
            "<button type='button' "
            f"class='metaChip {extra_cls} filterChip' "
            f"data-kind='{html.escape(kind)}' "
            f"data-value='{html.escape(val)}'>"
            f"{html.escape(label)}"
            "</button>"
        )
    return "".join(out)
def _meta_chip_text(values, cls):
    return "".join(f"<span class='{cls}'>{html.escape(v)}</span>" for v in values)
def build_films(session, user_id):
    movies = get_movies(session, JELLYFIN_URL, user_id)
    now_ts = int(datetime.now(timezone.utc).timestamp())
    new_cutoff = now_ts - (2 * 24 * 60 * 60)
    missing_models = 0
    missing_studio = 0
    missing_genre = 0
    films_unwatched_total = 0
    model_counts = {}
    studio_counts = {}
    genre_counts = {}
    seen_ids = set()
    dupe_rows = []
    items = []
    for m in movies:
        name = (m.get("Name") or "").strip()
        mid = m.get("Id")
        if not name or not mid:
            continue
        if mid in seen_ids:
            dupe_rows.append((name, mid))
            continue
        seen_ids.add(mid)
        year = m.get("ProductionYear")
        genres = _clean_list_str(m.get("Genres"), limit=4)
        studios = _extract_studios(m.get("Studios"), limit=2)
        directors, actors = _extract_people(m.get("People"), max_directors=1, max_actors=6)
        added_disp, added_ts = _parse_datecreated(m.get("DateCreated") or "")
        ud = m.get("UserData") or {}
        played_flag = False
        try:
            if bool(ud.get("Played")):
                played_flag = True
            elif int(ud.get("PlayCount") or 0) > 0:
                played_flag = True
        except Exception:
            played_flag = bool(ud.get("Played"))
        played01 = "1" if played_flag else "0"
        if played01 == "0":
            films_unwatched_total += 1
        if not (directors or actors):
            missing_models += 1
        if not studios:
            missing_studio += 1
        if not genres:
            missing_genre += 1
        for person in (directors + actors):
            k = person.strip().lower()
            if k:
                model_counts[k] = model_counts.get(k, 0) + 1
        for st in studios:
            k = st.strip().lower()
            if k:
                studio_counts[k] = studio_counts.get(k, 0) + 1
        for g in genres:
            k = g.strip().lower()
            if k:
                genre_counts[k] = genre_counts.get(k, 0) + 1
        items.append((name, mid, year, directors, actors, studios, genres, added_disp, added_ts, played01))
    if dupe_rows:
        print(f"INFO: Films: removed {len(dupe_rows)} duplicates (same Movie ID).")
    items.sort(key=lambda x: x[0].lower())
    def _top_n_from_counts(d, n=4):
        if not d:
            return []
        pairs = sorted(d.items(), key=lambda kv: (-int(kv[1]), kv[0]))
        out = []
        for k, c in pairs[: max(0, int(n))]:
            out.append({"name": k, "count": int(c)})
        return out
    top_models = _top_n_from_counts(model_counts, n=4)
    top_studios = _top_n_from_counts(studio_counts, n=4)
    top_genres = _top_n_from_counts(genre_counts, n=4)
    def _top1_from_list(lst):
        if not lst:
            return "—", 0
        return lst[0]["name"], int(lst[0]["count"])
    top_model_name, top_model_count = _top1_from_list(top_models)
    top_studio_name, top_studio_count = _top1_from_list(top_studios)
    top_genre_name, top_genre_count = _top1_from_list(top_genres)
    lis = []
    for name, mid, year, directors, actors, studios, genres, added_disp, added_ts, played01 in items:
        details_url = f"{JELLYFIN_URL}/web/index.html#/details?id={mid}&serverId={SERVER_ID}"
        img_url = f"{JELLYFIN_URL}/Items/{mid}/Images/Primary"
        year_txt = f" <span class='count'>({int(year)})</span>" if year else ""
        data_people = _pipewrap_lower(directors + actors)
        data_studios = _pipewrap_lower(studios)
        data_genres = _pipewrap_lower(genres)
        has_people = "1" if (directors or actors) else "0"
        has_studios = "1" if studios else "0"
        has_genres = "1" if genres else "0"
        is_new = bool(added_ts and added_ts >= new_cutoff)
        missing_people = not (directors or actors)
        missing_studio_flag = not bool(studios)
        missing_genre_flag = not bool(genres)
        has_any_missing = missing_people or missing_studio_flag or missing_genre_flag
        warn_is_red = (missing_people or missing_studio_flag)
        warn_is_white = (not warn_is_red) and missing_genre_flag
        badges = []
        if is_new:
            badges.append("<span class='badge badgeNew'>New</span>")
        if played01 == "1":
            badges.append("<span class='badge badgePlayed'>✓</span>")
        if has_any_missing:
            if warn_is_red:
                badges.append("<span class='badge badgeWarn badgeWarnRed'>!</span>")
            elif warn_is_white:
                badges.append("<span class='badge badgeWarn badgeWarnWhite'>!</span>")
        badges_html = ""
        if badges:
            badges_html = "<div class='badges'>" + "".join(badges) + "</div>"
        people_line = ""
        if directors or actors:
            director_btns = _filter_buttons(directors, "model", extra_cls="metaPerson", display_prefix="🎬 ")
            actor_btns = _filter_buttons(actors, "model", extra_cls="metaPerson")
            people_line = (
                "<div class='filmMetaRow'>"
                "<span class='filmMetaLabel'>Models:</span>"
                f"<span class='filmMetaChips'>{director_btns}{actor_btns}</span>"
                "</div>"
            )
        studio_line = ""
        if studios:
            studio_btns = _filter_buttons(studios, "studio", extra_cls="metaStudio")
            studio_line = (
                "<div class='filmMetaRow'>"
                "<span class='filmMetaLabel'>Studio:</span>"
                f"<span class='filmMetaChips'>{studio_btns}</span>"
                "</div>"
            )
        genre_line = ""
        if genres:
            genre_btns = _filter_buttons(genres, "genre", extra_cls="metaGenre")
            genre_line = (
                "<div class='filmMetaRow'>"
                "<span class='filmMetaLabel'>Genres:</span>"
                f"<span class='filmMetaChips'>{genre_btns}</span>"
                "</div>"
            )
        added_show = added_disp if added_disp else "—"
        added_line = (
            "<div class='filmMetaRow'>"
            f"<span class='filmMetaChips'>{_meta_chip_text([added_show], 'metaChip metaAdded')}</span>"
            "</div>"
        )
        meta_html = "<div class='filmMeta'>" + added_line + studio_line + genre_line + people_line + "</div>"
        lis.append(
            f"<li class='card' data-name='{html.escape(name).lower()}' data-count='0' "
            f"data-display='{html.escape(name)}' data-people='{html.escape(data_people)}' "
            f"data-studios='{html.escape(data_studios)}' data-genres='{html.escape(data_genres)}' "
            f"data-haspeople='{has_people}' data-hasstudios='{has_studios}' data-hasgenres='{has_genres}' "
            f"data-added='{added_ts}' data-played='{played01}'>"
            f"{badges_html}"
            f"<a class='cardLink' href='{details_url}' target='_blank' rel='noopener'>"
            f"<img class='thumb' src='{img_url}' onerror=\"this.style.display='none'\">"
            "</a>"
            "<div class='cardBody'>"
            f"<a class='titleLink' href='{details_url}' target='_blank' rel='noopener'>"
            f"<div class='name'>{html.escape(name)}{year_txt}</div>"
            "</a>"
            f"{meta_html}"
            "</div>"
            "</li>"
        )
    films_pool = [{"id": mid, "name": name} for (name, mid, *_rest) in items]
    latest_sorted = sorted(items, key=lambda x: (-int(x[8] or 0), x[0].lower()))
    films_latest = [{"id": mid, "name": name} for (name, mid, *_rest, _played01) in latest_sorted[:4]]
    film_stats = {
        "films_missing_models": missing_models,
        "films_missing_studio": missing_studio,
        "films_missing_genre": missing_genre,
        "films_unwatched_total": films_unwatched_total,
        "films_pool": films_pool,
        "films_latest": films_latest,
        "top_models": top_models,
        "top_studios": top_studios,
        "top_genres": top_genres,
        "top_model_name": top_model_name,
        "top_model_count": top_model_count,
        "top_studio_name": top_studio_name,
        "top_studio_count": top_studio_count,
        "top_genre_name": top_genre_name,
        "top_genre_count": top_genre_count,
    }
    return "\n".join(lis), len(items), film_stats
