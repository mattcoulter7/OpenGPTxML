import typing as T

from opengptxml.schema.converter_styles import ConverterStyles
from opengptxml.schema.style import OpenXMLStyle


def compile_conversion_styles(
    styles: T.List[OpenXMLStyle],
) -> ConverterStyles:
    return ConverterStyles(
        # TODO: intelligently read these from the document
    )
