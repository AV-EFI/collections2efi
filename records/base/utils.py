def compute_display_and_ordering_title(
    title_text: str, title_article: str | None
) -> tuple[str, str | None]:
    new_title_text = title_text

    if title_article is None:
        return new_title_text, None

    return f"{title_article} {title_text}", f"{title_text}, {title_article}"
