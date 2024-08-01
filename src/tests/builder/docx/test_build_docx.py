import shutil

from opengptxml.builder.docx import build_docx
from tests import generate_sample_markdown

OUTPUT_PATH = rf"src/tests/data/{__name__}.docx"


def test():
    markdown = generate_sample_markdown()
    
    with build_docx(
        markdown=markdown,
    ) as fp:
        shutil.copy(fp.name, OUTPUT_PATH)

    print(
        f"Please inspect the file at `{OUTPUT_PATH}`"
    )

    assert True