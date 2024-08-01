import typing as T


from opengptxml.schema.converter_styles import ConverterStyles
from opengptxml.schema.style import OpenXMLStyle
from enum import Enum


class CompileMethod(Enum):
    DEFAULT = "DEFAULT"
    AI = "AI"

def compile_conversion_styles(
    styles: T.List[OpenXMLStyle],
    *,
    compile_method: CompileMethod = CompileMethod.DEFAULT
) -> ConverterStyles:
    if compile_method is compile_method.DEFAULT:
        return compile_conversion_styles_default(styles)

    if compile_method is compile_method.AI:
        return compile_conversion_styles_using_ai(styles)

    raise ValueError(
        f"Invalid value for type, must be one of `{list(CompileMethod)}`, but found `{repr(compile_method)}`"
    )
    
def compile_conversion_styles_using_ai(
    styles: T.List[OpenXMLStyle],
) -> ConverterStyles:
    #TODO: intelligently read these from the document
    # using a language model that assigns xml styles to the converter styles
    # based on html tags
    raise NotImplementedError()

def compile_conversion_styles_default(
    styles: T.List[OpenXMLStyle],
) -> ConverterStyles:
    styles_by_id = {
        style.style_id: style
        for style in styles
    }

    # TODO: use a text search and attribute valuesto extract these
    return ConverterStyles(
        p_style=styles_by_id["Normal"],
        strong_style=styles_by_id["Strong"],
        em_style=styles_by_id["Emphasis"],
        a_style=None,
        ol_style=styles_by_id["ListBullet"],
        ul_style=styles_by_id["ListNumber"],
        h1_style=styles_by_id["Heading1"],
        h2_style=styles_by_id["Heading2"],
        h3_style=styles_by_id["Heading3"],
        h4_style=styles_by_id["Heading4"],
        h5_style=styles_by_id["Heading5"],
        h6_style=styles_by_id["Heading6"],
    )
