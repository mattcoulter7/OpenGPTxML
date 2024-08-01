import typing as T
import logging
import string
import random

from lxml import etree
from contextlib import contextmanager
from docxtpl import DocxTemplate, RichText

from opengptxml.schema.converter_settings import ConverterSettings
from opengptxml.converter.markdown_2_openxml import markdown_2_open_xml
from opengptxml.builder.helpers import (
    resolve_markdown_input_type,
    save_document,
)

logger = logging.getLogger()


@contextmanager
def build_docx_from_template(
    template: str,
    context: dict[str, T.Iterable[str]],
    *,
    rich_text_keys: T.List[str] = None,
    settings: T.Optional[ConverterSettings] = None,
):
    settings = settings or ConverterSettings()
    document = DocxTemplate(template)

    # convert markdown to rich text
    nest_id = _generate_nest_id()
    if rich_text_keys:
        for k in rich_text_keys:
            if k in context:
                markdown = context[k]
                rich_text = RichText()
                rich_text.xml = markdown_2_open_xml(
                    resolve_markdown_input_type(markdown),
                    settings=settings,
                    nest_id=nest_id,
                )
                context[k] = rich_text

    # render variables
    document.render(
        context,
        autoescape=True
    )

    # When we have loaded the converted markdown into the docx
    # as variables, any paragraph elements from the converted
    # markdown become nested inside of an existing paragraph
    # element.
    #
    # This is illegal structure on docx, so we we need to perform 
    # unnest all of those nested paragraph elements.
    if rich_text_keys:
        _unnest_nested_paragraphs(
            document.docx._element,
            nest_id=nest_id,
        )

    # When we load text into the variable, with the markdown conversion,
    # the first run gets added to a new paragraph.
    #
    # The original paragraph housing the {{ variable }} is simple an empty
    # paragraph, so we need to remove it.
    if rich_text_keys:
        _remove_empty_paragraphs(
            document.docx._element,
            after_p_styles=[
                style for k, style in settings.items()
                if k.startswith("h")
            ],
            remove_p_styles=[
                settings.get("p_style"),
            ],
        )

    with save_document(document, "docx") as fp:
        yield fp


def _unnest_nested_paragraphs(
    root: etree.ElementBase,
    *,
    nest_id: T.Optional[str] = None,
):
    namespaces = root.nsmap

    def process_paragraph(paragraph):
        nested_paragraphs = paragraph.findall('.//w:p', namespaces)
        for nested_paragraph in reversed(nested_paragraphs):
            if nest_id is not None:
                if nested_paragraph.get(f'{{{namespaces["w"]}}}nestId') != nest_id:
                    continue

            nested_paragraph.getparent().remove(nested_paragraph)
            paragraph.addnext(nested_paragraph)
            process_paragraph(nested_paragraph)
            if f'{{{namespaces["w"]}}}nestId' in nested_paragraph.attrib:
                del nested_paragraph.attrib[f'{{{namespaces["w"]}}}nestId']

    paragraphs = root.findall('.//w:p', namespaces)
    for paragraph in paragraphs:
        process_paragraph(paragraph)


def _remove_empty_paragraphs(
    root: etree.ElementBase,
    after_p_styles: T.List[str],  # only paragraphs after these styles can be removed
    remove_p_styles: T.List[str],  # only paragraphs with these styles can be removed
):
    namespaces = root.nsmap

    def get_paragraph_style(paragraph):
        pPr = paragraph.find('w:pPr', namespaces)
        if pPr is None:
            return None
        pStyle = pPr.find('w:pStyle', namespaces)
        if pStyle is None:
            return None
        return pStyle.get(f'{{{namespaces["w"]}}}val')

    paragraphs = root.findall('.//w:p', namespaces)

    for i in range(len(paragraphs) - 1, 0, -1):
        paragraph = paragraphs[i]
        paragraph_text = ''.join(paragraph.itertext()).strip()

        if not paragraph_text:  # Check if the paragraph is empty
            paragraph_style = get_paragraph_style(paragraph)

            if paragraph_style in remove_p_styles:
                previous_paragraph = paragraphs[i - 1]
                previous_paragraph_style = get_paragraph_style(previous_paragraph)

                if previous_paragraph_style in after_p_styles:
                    paragraph.getparent().remove(paragraph)


def _generate_nest_id():
    # Define the characters to use
    characters = string.digits + string.ascii_uppercase
    
    # Generate a random string of length 8
    random_string = ''.join(random.choice(characters) for _ in range(8))
    
    return random_string
