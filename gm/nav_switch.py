def nav_switch(active: str):
    d_cls = "tab active" if active == "dashboard" else "tab"
    f_cls = "tab active" if active == "films" else "tab"
    m_cls = "tab active" if active == "models" else "tab"
    s_cls = "tab active" if active == "studios" else "tab"
    g_cls = "tab active" if active == "genres" else "tab"
    return (
        "<div class='tabs'>"
        f"<a class='{d_cls}' href='dashboard.html'>"
        "<img src='dashboard.png' alt='Dashboard' class='tabIcon'>"
        "</a>"
        f"<a class='{f_cls}' href='films.html'>Films</a>"
        f"<a class='{m_cls}' href='models.html'>Models</a>"
        f"<a class='{s_cls}' href='studios.html'>Studios</a>"
        f"<a class='{g_cls}' href='genres.html'>Genres</a>"
        "</div>"
    )
