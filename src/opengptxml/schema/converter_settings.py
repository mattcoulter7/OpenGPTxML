import typing as T

from dataclasses import dataclass, field

from .converter_styles import ConverterStyles


@dataclass
class ConverterSettings:
    styles: ConverterStyles = field(default_factory=ConverterStyles)
