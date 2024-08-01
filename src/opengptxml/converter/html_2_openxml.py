import typing as T
import logging
import random
import six

from html import escape
from bs4 import BeautifulSoup, PageElement

from opengptxml.schema.converter_settings import ConverterSettings
from opengptxml.schema.style import OpenXMLStyle

logger = logging.getLogger()


def html_2_open_xml(
    html: str,
    settings: ConverterSettings,
    *,
    nest_id: T.Optional[str] = None,
) -> str:
    soup = BeautifulSoup(html, "html.parser")
    return html_element_2_open_xml(
        soup,
        settings=settings,
        nest_id=nest_id,
    )


def html_element_2_open_xml(
    element: PageElement,
    settings: ConverterSettings,
    *,
    tag_hierarchy: T.Optional[T.List[str]] = None,
    children_override: T.Optional[T.Iterable[T.Union[str, PageElement]]] = None,
    nest_id: T.Optional[str] = None,
    ilvl: T.Optional[int] = None,
    num_id: T.Optional[int] = None,
) -> str:
    if tag_hierarchy is None:
        tag_hierarchy = []

    tag_hierarchy.append(element.name)
    
    children = children_override \
        if children_override is not None else element

    xml = ""
    for child in children:
        # new lines are unnecessary since paragraphs are already
        # separated
        if child == "\n":
            continue

        child_xml = get_element_open_xml(
            child,
            tag_hierarchy=[*tag_hierarchy],  # pass a copy for each branch
            settings=settings,
            nest_id=nest_id,
            ilvl=ilvl,
            num_id=num_id,
        )
        if child_xml is None:
            continue

        xml += child_xml

    return xml


def get_element_open_xml(
    element: T.Union[str, PageElement],
    *,
    tag_hierarchy: T.Optional[T.List[str]] = None,
    settings: ConverterSettings,
    nest_id: T.Optional[str] = None,
    ilvl: T.Optional[int] = None,
    num_id: T.Optional[int] = None,
) -> str:
    if tag_hierarchy is None:
        tag_hierarchy = []

    # text level
    if isinstance(element, str):
        return get_open_xml_run(
            element,
            style=settings.styles.get_style("p"),
        )

    # bold
    if element.name == "strong":
        return get_open_xml_run(
            element.text,
            bold=True,
            style=settings.styles.get_style("strong"),
        )

    # italic
    if element.name == "em":
        return get_open_xml_run(
            element.text,
            italic=True,
            style=settings.styles.get_style("em"),
        )

    # headings
    if element.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
        return get_open_xml_paragraph(
            inner=html_element_2_open_xml(
                element,
                settings=settings,
                tag_hierarchy=tag_hierarchy,
                nest_id=nest_id,
            ),
            style=settings.styles.get_style(element.name),
            nest_id=nest_id,
        )

    # text group level
    # paragraph
    if element.name == "p":
        return get_open_xml_paragraph(
            inner=html_element_2_open_xml(
                element,
                settings=settings,
                tag_hierarchy=tag_hierarchy,
                nest_id=nest_id,
            ),
            style=settings.styles.get_style("p"),
            nest_id=nest_id,
        ) 

    # anchor
    if element.name == "a":
        return get_open_xml_hyperlink(
            inner=html_element_2_open_xml(
                element,
                settings=settings,
                tag_hierarchy=tag_hierarchy,
                nest_id=nest_id,
            ),
            url_id=element.attrs.get('href', ''),
        )

    # list element
    if element.name == 'li':
        list_type = tag_hierarchy[-1]
        return get_open_xml_list(
            inner=html_element_2_open_xml(
                element,
                settings=settings,
                tag_hierarchy=tag_hierarchy,
                nest_id=nest_id,
                ilvl=ilvl,
                num_id=num_id,
            ),
            style=settings.styles.get_style(list_type),
            nest_id=nest_id,
            ilvl=ilvl,
            num_id=num_id,
        )

    # numbered list / bullet list
    if element.name in ['ol', 'ul']:
        return html_element_2_open_xml(
            element,
            settings=settings,
            tag_hierarchy=tag_hierarchy,
            # children_override=element.find_all('li'),  # only want to show list items
            nest_id=nest_id,
            ilvl=ilvl + 1 if ilvl is not None else 0,
            num_id=generate_num_id(1000,9999),
        )

    logger.warning(
        f"Unsupported element `{element.name}`, some formatting may be lost!"
    )
    return html_element_2_open_xml(
        element,
        settings=settings,
    )


def get_open_xml_run(
    inner: T.Any,
    *,
    style: T.Optional[OpenXMLStyle] = None,
    color: T.Optional[str] = None,
    highlight: T.Optional[str] = None,
    size: T.Optional[str] = None,
    subscript: T.Optional[str] = None,
    superscript: T.Optional[str] = None,
    bold: bool = False,
    italic: bool = False,
    underline: bool = False,
    strike: bool = False,
    font: T.Optional[str] = None,
    prop: str = u'',
) -> str:
    """
    Code Credit:    https://github.com/elapouya/python-docx-template/blob/v0.18.0/docxtpl/richtext.py#L26-L111
                    We have made changes based on the above source code.
    """

    # If not a string : cast to string (ex: int, dict etc...)
    if not isinstance(inner, (six.text_type, six.binary_type)):
        inner = six.text_type(inner)
    if not isinstance(inner, six.text_type):
        inner = inner.decode('utf-8', errors='ignore')

    inner = escape(inner)

    if style:
        prop += u'<w:rStyle w:val="%s"/>' % style
    if color:
        if color[0] == '#':
            color = color[1:]
        prop += u'<w:color w:val="%s"/>' % color
    if highlight:
        if highlight[0] == '#':
            highlight = highlight[1:]
        prop += u'<w:shd w:fill="%s"/>' % highlight
    if size:
        prop += u'<w:sz w:val="%s"/>' % size
        prop += u'<w:szCs w:val="%s"/>' % size
    if subscript:
        prop += u'<w:vertAlign w:val="subscript"/>'
    if superscript:
        prop += u'<w:vertAlign w:val="superscript"/>'
    if bold:
        prop += u'<w:b/>'
    if italic:
        prop += u'<w:i/>'
    if underline:
        if underline not in ['single', 'double', 'thick', 'dotted', 'dash', 'dotDash', 'dotDotDash', 'wave']:
            underline = 'single'
        prop += u'<w:u w:val="%s"/>' % underline
    if strike:
        prop += u'<w:strike/>'
    if font:
        regional_font = u''
        if ':' in font:
            region, font = font.split(':', 1)
            regional_font = u' w:{region}="{font}"'.format(font=font, region=region)
        prop += (
            u'<w:rFonts w:ascii="{font}" w:hAnsi="{font}" w:cs="{font}"{regional_font}/>'
            .format(font=font, regional_font=regional_font)
        )

    xml = u'<w:r>'
    if prop:
        xml += u'<w:rPr>%s</w:rPr>' % prop
    xml += u'<w:t xml:space="preserve">%s</w:t>' % inner
    xml += u'</w:r>'

    return xml


def get_open_xml_hyperlink(
    inner: str,
    url_id: str,
) -> str:
    return (u'<w:hyperlink r:id="%s" w:tgtFrame="_blank">%s</w:hyperlink>'
                % (url_id, inner))


def get_open_xml_paragraph(
    inner: str,
    *,
    style: T.Optional[OpenXMLStyle] = None,
    nest_id: T.Optional[str] = None,
    prop: str = u'',
) -> str:
    if style:
        prop += u'<w:pStyle w:val="%s"/>' % style

    xml = u'<w:p'
    if nest_id is not None:
        xml += u' w:nestId="%s"' % nest_id
    xml += u'>'
    if prop:
        xml += u'<w:pPr>%s</w:pPr>' % prop
    xml += inner
    xml += u'</w:p>'

    return xml


def get_open_xml_list(
    inner: str,
    *,
    style: T.Optional[OpenXMLStyle] = None,
    nest_id: T.Optional[str] = None,
    ilvl: T.Optional[int] = None,
    num_id: T.Optional[int] = None,
) -> str:
    if ilvl is None:
        ilvl = 0
    if num_id is None:
        logger.warning(
            f"num_id is null, this may cause odd groups of lists"
        )
        num_id = 1

    prop = (
        u'<w:numPr>'
            u'<w:ilvl w:val="%d"/>' % ilvl +
            u'<w:numId w:val="%d"/>' % num_id +
        u'</w:numPr>'
    )

    return get_open_xml_paragraph(
        inner,
        style=style,
        prop=prop,
        nest_id=nest_id,
    )


def generate_num_id(
    min: int,
    max: int,
) -> int:
    return random.randint(min, max)
