def az_bar():
    return (
        "<div class='azbar'>"
        "<button data-letter='ALL' class='az active'>All</button>"
        + "".join([f"<button data-letter='{c}' class='az'>{c}</button>" for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"])
        + "</div>"
    )
