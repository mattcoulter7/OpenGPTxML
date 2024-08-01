import typing as T

from opengptxml.schema.converter_settings import ConverterSettings

from .markdown_2_html import markdown_2_html
from .html_2_openxml import html_2_open_xml


def markdown_2_open_xml(
    markdown: str,
    settings: ConverterSettings,
    *,
    nest_id: T.Optional[str] = None,
):
    html = markdown_2_html(markdown)
    open_xml = html_2_open_xml(
        html,
        settings,
        nest_id=nest_id,
    )
    return open_xml
