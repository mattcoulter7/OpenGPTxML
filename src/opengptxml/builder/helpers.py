import typing as T
import tempfile
import uuid

from contextlib import contextmanager


def resolve_markdown_input_type(
    markdown: T.Iterable[str],
) -> str:
    if isinstance(markdown, str):
        return markdown

    if isinstance(markdown, T.Iterable):
        return "".join([token for token in markdown])

    raise TypeError(
        f"markdown is not a valid str, found {repr(markdown)}"
    )


@contextmanager
def save_document(document, extension):
    with tempfile.TemporaryDirectory() as temp_dir:
        with open(f'{temp_dir}/{uuid.uuid4()}.{extension}', 'wb') as fp:
            document.save(fp)
            fp.seek(0)  # Move the file pointer to the beginning of the file
            yield fp
