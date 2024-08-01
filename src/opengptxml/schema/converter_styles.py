import typing as T
from dataclasses import dataclass, field

from opengptxml.schema.style import OpenXMLStyle

@dataclass
class ConverterStyles:
    p_style: T.Optional[OpenXMLStyle] = field(default=None)
    strong_style: T.Optional[OpenXMLStyle] = field(default=None)
    em_style: T.Optional[OpenXMLStyle] = field(default=None)
    a_style: T.Optional[OpenXMLStyle] = field(default=None)
    ol_style: T.Optional[OpenXMLStyle] = field(default=None)
    ul_style: T.Optional[OpenXMLStyle] = field(default=None)
    h1_style: T.Optional[OpenXMLStyle] = field(default=None)
    h2_style: T.Optional[OpenXMLStyle] = field(default=None)
    h3_style: T.Optional[OpenXMLStyle] = field(default=None)
    h4_style: T.Optional[OpenXMLStyle] = field(default=None)
    h5_style: T.Optional[OpenXMLStyle] = field(default=None)
    h6_style: T.Optional[OpenXMLStyle] = field(default=None)

    def load_default_styles(
        self,
        *converter_styles: "ConverterStyles"
    ) -> None:
        for converter_style in converter_styles:
            for (attr, style) in converter_style:
                if getattr(self, attr) is None:
                    setattr(self, attr, style)

    def get_style_key(
        self,
        html_tag: str
    ) -> str:
        return f"{html_tag}_style"

    def validate_html_tag(
        self,
        html_tag: str
    ) -> None:
        if not hasattr(self, self.get_style_key(html_tag)):
            raise ValueError(
                f"`{html_tag}` isn't supported in ConverterSettings"
                f" please help us out and raise a PR to support this!"
            )

    def get_style(
        self,
        html_tag: str,
    ) -> T.Optional[OpenXMLStyle]:
        self.validate_html_tag(html_tag)
        return getattr(self, self.get_style_key(html_tag))
    
    def set_style(
        self,
        html_tag: str,
        style: T.Optional[OpenXMLStyle] = None,
    ):
        self.validate_html_tag()
        setattr(self, self.get_style_key(html_tag), style)

    def iter_styles(self) -> T.Generator[T.Tuple[str, T.Optional[OpenXMLStyle]], None, None]:
        for tuple in self:
            style_key = tuple[0]
            if not style_key.endswith("_style"):
                continue

            # tuple is mutable, allowing modification by iterator!
            yield tuple
    
    def __iter__(self) -> T.Generator[T.Tuple[str, T.Optional[OpenXMLStyle]], None, None]:
        for tuple in self.__dict__.items():
            # tuple is mutable, allowing modification by iterator!
            yield tuple
