import html
def tag_bar(all_tags):
    if not all_tags:
        return ""
    buttons = []
    for t in all_tags:
        safe = html.escape(t)
        buttons.append(f"<button class='tag' data-tag='{html.escape(t).lower()}' type='button'>{safe}</button>")
    return (
        "<div class='tagbar' id='tagbar'>"
        "<div class='tagbarLeft'>"
        "<span class='tagTitle'>Tags</span>"
        "<button class='tagClear' id='tagClear' type='button'>Clear</button>"
        "</div>"
        "<div class='tagbarChips'>"
        + "".join(buttons) +
        "</div>"
        "</div>"
    )
