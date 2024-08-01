import logging

from markdown_it import MarkdownIt

logger = logging.getLogger()
markdowner = MarkdownIt("js-default", {"linkify": True})


def markdown_2_html(markdown: str) -> str:
    return markdowner.render(markdown)
