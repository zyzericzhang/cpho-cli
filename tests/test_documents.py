from pathlib import Path

from cpho_cli.core.documents import load_document


def test_load_image_document(tmp_path: Path) -> None:
    image = tmp_path / "problem.png"
    image.write_bytes(b"not-a-real-image-but-carried-as-bytes")

    document = load_document(image)

    assert document.path == image
    assert len(document.pages) == 1
    assert document.pages[0].page_number == 1
    assert document.pages[0].image_bytes == b"not-a-real-image-but-carried-as-bytes"

