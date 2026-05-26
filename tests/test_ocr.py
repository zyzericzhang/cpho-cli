from cpho_cli.core.ocr import normalize_ocr_blocks


def test_low_confidence_blocks_are_preserved() -> None:
    blocks = normalize_ocr_blocks(
        page_number=1,
        raw_blocks=[
            {"text": "F=ma", "confidence": 0.91, "bbox": [0, 0, 10, 10]},
            {"text": "alpha?", "confidence": 0.41, "bbox": [10, 10, 20, 20]},
        ],
        low_confidence_threshold=0.6,
    )

    assert blocks[0].low_confidence is False
    assert blocks[1].low_confidence is True
    assert blocks[1].text == "alpha?"

