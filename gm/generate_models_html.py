from .config import FILMS_OUT, MODELS_OUT, STUDIOS_OUT, GENRES_OUT, DASHBOARD_OUT
from .auth_session import auth_session
from .write_page import write_page
from .build_films import build_films
from .build_models import build_models
from .build_studios import build_studios
from .build_genres import build_genres
from .build_dashboard import build_dashboard
def main():
    session, user_id = auth_session()
    films_lis, films_n, films_stats = build_films(session, user_id)
    write_page(
        FILMS_OUT,
        "Film",
        "films",
        films_lis,
        extra_bar_html="",
        page_class="wide",
        default_grid_px=360,
    )
    print(f"OK: Wrote {FILMS_OUT} with {films_n} films")
    models_lis, models_n, models_tags_bar, models_img_map = build_models(session, user_id)
    write_page(
        MODELS_OUT,
        "Models",
        "models",
        models_lis,
        extra_bar_html=models_tags_bar,
        default_grid_px=230,
    )
    print(f"OK: Wrote {MODELS_OUT} with {models_n} models")
    studios_lis, studios_n, studios_img_map = build_studios(session, user_id)
    write_page(
        STUDIOS_OUT,
        "Studios",
        "studios",
        studios_lis,
        extra_bar_html="",
        default_grid_px=230,
    )
    print(f"OK: Wrote {STUDIOS_OUT} with {studios_n} studios")
    genres_lis, genres_n, genres_img_map = build_genres(session, user_id)
    write_page(
        GENRES_OUT,
        "Genres",
        "genres",
        genres_lis,
        extra_bar_html="",
        default_grid_px=230,
    )
    print(f"OK: Wrote {GENRES_OUT} with {genres_n} genres")
    stats = {
        "films_total": films_n,
        "models_total": models_n,
        "studios_total": studios_n,
        "genres_total": genres_n,
        "models_img_map": models_img_map or {},
        "studios_img_map": studios_img_map or {},
        "genres_img_map": genres_img_map or {},
    }
    if isinstance(films_stats, dict):
        stats.update(films_stats)
    dash_body_html = build_dashboard(stats)
    dash_lis = (
        "<li class='dashHost' style='list-style:none;'>"
        + dash_body_html +
        "</li>"
    )
    write_page(
        DASHBOARD_OUT,
        "Dashboard",
        "dashboard",
        dash_lis,
        extra_bar_html="",
        default_grid_px=230,
    )
    print(f"OK: Wrote {DASHBOARD_OUT} with dashboard")
if __name__ == "__main__":
    main()
