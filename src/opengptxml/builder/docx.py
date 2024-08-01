import typing as T
import logging
from lxml import etree

from docx import Document as load_or_create_document
from contextlib import contextmanager

from opengptxml.schema.converter_settings import ConverterSettings
from opengptxml.converter.markdown_2_openxml import markdown_2_open_xml
from opengptxml.builder.helpers import (
    resolve_markdown_input_type,
    save_document,
)
from opengptxml.styles.loader import load_document_styles
from opengptxml.styles.compiler import compile_conversion_styles

logger = logging.getLogger()


@contextmanager
def build_docx(
    markdown: T.Iterable[str],
    *,
    reference_document: T.Optional[str] = None,
    settings: T.Optional[ConverterSettings] = None,
):
    settings = settings or ConverterSettings()

    # Create a new Word document
    document = load_or_create_document(reference_document)

    # Load styles from that document
    document_styles = load_document_styles(document.styles.element)
    document_conversion_styles = compile_conversion_styles(document_styles)
    settings.styles.load_default_styles(document_conversion_styles)

    # perform markdown -> rich text conversions
    content_xml = markdown_2_open_xml(
        resolve_markdown_input_type(markdown),
        settings=settings,
    )

    # Add content to the document
    _append_content_roots(
        document.element,
        content_xml,
    )

    with save_document(document, "docx") as fp:
        yield fp


def _resolve_content_namespaces(
    xml_string: str,
    namespaces: dict,
) -> str:
    if xml_string.startswith("<root"):
        logger.warning("<root> already defined in xml_string, unable to resolve namespaces")
        return xml_string

    # prepare namespaces string
    attr = []
    for prefix, uri in namespaces.items():
        attr.append(
            f"xmlns:{prefix}=\"{uri}\""
        )
    attr_serialised = " ".join(attr)

    return (
        f'<root {attr_serialised}>'
            f'{xml_string}' 
        f'</root>'
    )


def _append_content_roots(
    document_root: etree.ElementBase,
    *content_roots: T.Union[str, etree.ElementBase],
):
    # Extract namespaces from the document root
    namespaces = document_root.nsmap

    # Find the document body using the namespace map
    document_body = document_root.find('w:body', namespaces=namespaces)

    for content_root in content_roots:
        # Parse XML if content_root is a string
        if isinstance(content_root, str):
            content_root = _resolve_content_namespaces(
                content_root, namespaces,
            )
            content_root = etree.fromstring(content_root)

        for element in content_root:
            document_body.append(element)
