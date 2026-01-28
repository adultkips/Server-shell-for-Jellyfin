import html
import json
from .config import JELLYFIN_URL, SERVER_ID
def build_dashboard(stats: dict):
    def esc(s):
        return html.escape(str(s if s is not None else ""))
    models_img_map = stats.get("models_img_map") or {}
    studios_img_map = stats.get("studios_img_map") or {}
    genres_img_map = stats.get("genres_img_map") or {}
    def _lookup_img_id(name: str, mapping: dict):
        if not name:
            return ""
        key = str(name).strip().lower()
        return str(mapping.get(key) or "")
    def _norm_top_list(raw_list):
        out = []
        for item in raw_list or []:
            if not isinstance(item, dict):
                continue
            n = (item.get("name") or "").strip().lower()
            c = item.get("count")
            try:
                c = int(c or 0)
            except Exception:
                c = 0
            if n:
                out.append({"name": n, "count": c})
        return out[:4]
    top_models = _norm_top_list(stats.get("top_models"))
    top_studios = _norm_top_list(stats.get("top_studios"))
    top_genres = _norm_top_list(stats.get("top_genres"))
    top_models_with_img = [
        {"name": x["name"], "count": int(x["count"]), "id": _lookup_img_id(x["name"], models_img_map)}
        for x in top_models
    ]
    top_studios_with_img = [
        {"name": x["name"], "count": int(x["count"]), "id": _lookup_img_id(x["name"], studios_img_map)}
        for x in top_studios
    ]
    top_genres_with_img = [
        {"name": x["name"], "count": int(x["count"]), "id": _lookup_img_id(x["name"], genres_img_map)}
        for x in top_genres
    ]
    films_pool = stats.get("films_pool") or []
    norm_pool = []
    if isinstance(films_pool, list):
        for it in films_pool:
            if not isinstance(it, dict):
                continue
            fid = (it.get("id") or it.get("Id") or "").strip()
            fname = (it.get("name") or it.get("Name") or "").strip()
            if fid and fname:
                norm_pool.append({"id": fid, "name": fname})
    films_latest = stats.get("films_latest") or []
    norm_latest = []
    if isinstance(films_latest, list):
        for it in films_latest:
            if not isinstance(it, dict):
                continue
            fid = (it.get("id") or it.get("Id") or "").strip()
            fname = (it.get("name") or it.get("Name") or "").strip()
            if fid and fname:
                norm_latest.append({"id": fid, "name": fname})
    norm_latest = norm_latest[:4]
    default_cards = [
        "vert_film_1",
        "vert_film_2",
        "vert_film_3",
        "vert_film_4",
        "films_total",
        "models_total",
        "studios_total",
        "genres_total",
        "top_model_1",
        "top_model_2",
        "top_model_3",
        "top_model_4",
        "vert_latest_1",
        "vert_latest_2",
        "vert_latest_3",
        "vert_latest_4",
        "films_unwatched_total",
        "films_missing_models",
        "films_missing_studio",
        "films_missing_genre",
        "top_studio_1",
        "top_studio_2",
        "top_studio_3",
        "top_studio_4",
        "top_genre_1",
        "top_genre_2",
        "top_genre_3",
        "top_genre_4",
    ]
    js_stats_obj = {
        "films_total": int(stats.get("films_total") or 0),
        "models_total": int(stats.get("models_total") or 0),
        "studios_total": int(stats.get("studios_total") or 0),
        "genres_total": int(stats.get("genres_total") or 0),
        "films_missing_models": int(stats.get("films_missing_models") or 0),
        "films_missing_studio": int(stats.get("films_missing_studio") or 0),
        "films_missing_genre": int(stats.get("films_missing_genre") or 0),
        "films_unwatched_total": int(stats.get("films_unwatched_total") or 0),
        "top_models": top_models_with_img,
        "top_studios": top_studios_with_img,
        "top_genres": top_genres_with_img,
        "films_pool": norm_pool,
        "films_latest": norm_latest,
    }
    js_cfg_obj = {
        "jellyfinUrl": str(JELLYFIN_URL),
        "serverId": str(SERVER_ID),
        "lsKey": "dash_cards_v1",
        "apiGet": "/dash/layout",
        "apiSet": "/dash/layout",
        "emptyToken": "__empty__",
    }
    js_stats_json = json.dumps(js_stats_obj, ensure_ascii=False)
    js_default_json = json.dumps(default_cards, ensure_ascii=False)
    js_cfg_json = json.dumps(js_cfg_obj, ensure_ascii=False)
    dashboard_js_src = "static/dashboard.js"
    body = f"""
<div class="dashWrap">
  <div class="dashRows" id="dashRows"></div>
  <div class="dashMeta">
    Click “+” to add cards. Drag to reorder.
  </div>
  <div class="dashPicker" id="dashPicker" aria-hidden="true">
    <div class="dashPickerBox" role="dialog" aria-modal="true" aria-label="Add card">
      <div class="dashPickerTitle">Add card</div>
      <div class="dashPickerList" id="dashPickerList"></div>
      <div class="dashPickerActions">
        <button class="dashBtn" id="dashPickerClose" type="button">Close</button>
      </div>
    </div>
  </div>
</div>
<script>
  window.DASH_STATS = {js_stats_json};
  window.DASH_DEFAULT = {js_default_json};
  window.DASH_CFG = {js_cfg_json};
</script>
<script src="{esc(dashboard_js_src)}"></script>
    """.strip()
    return body
