import typing as T

from opengptxml.schema.style import OpenXMLStyle

from lxml import etree


def load_document_styles(
    root: etree.ElementBase,
) -> T.List[OpenXMLStyle]:
    namespaces = root.nsmap
    style_elements = root.findall('.//w:style', namespaces)

    styles = []
    for document_style_element in style_elements:
        type = document_style_element.get(f"{{{namespaces['w']}}}type")
        default = document_style_element.get(f"{{{namespaces['w']}}}default")
        style_id = document_style_element.get(f"{{{namespaces['w']}}}styleId")

        name_element = document_style_element.find(f"w:name", namespaces)
        name = name_element.get(f"{{{namespaces['w']}}}val")

        style = OpenXMLStyle(
            style_id=style_id,
            name=name,
            type=type,
            default=default,
        )

        styles.append(style)

    return styles
