import time
import typing as T

DEFAULT_FILE_PATH = r"src/tests/data/sample_text.md"

def _split_into_chunks(
    text: str,
    chunk_size: int = 4,
) -> T.Generator[str, None, None]:
    """Splits the string s into chunks of size chunk_size."""
    for i in range(0, len(text), chunk_size):
        yield text[i:i+chunk_size]


def generate_sample_markdown(
    file_path: str = DEFAULT_FILE_PATH,
) -> T.Generator[str, None, None]:
    """Imagine this is an llm feeding us some tokens!"""
    text = None
    with open(file_path, "r") as fp:
        text = fp.read()

    yield from _split_into_chunks(text)
