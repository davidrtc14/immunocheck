import hashlib
from pathlib import Path

import pytest

from scripts.build_pilot_corpus import _verify_download


def test_download_receipt_accepts_matching_file(tmp_path: Path) -> None:
    content = b"validated document"
    path = tmp_path / "document.pdf"
    path.write_bytes(content)
    receipt: dict[str, object] = {
        "size_bytes": len(content),
        "sha256": hashlib.sha256(content).hexdigest(),
    }

    _verify_download(path, receipt)


@pytest.mark.parametrize(
    "receipt",
    (
        {"size_bytes": 99, "sha256": hashlib.sha256(b"document").hexdigest()},
        {"size_bytes": 8, "sha256": "0" * 64},
    ),
)
def test_download_receipt_rejects_changed_file(
    tmp_path: Path,
    receipt: dict[str, object],
) -> None:
    path = tmp_path / "document.pdf"
    path.write_bytes(b"document")

    with pytest.raises(ValueError, match="divergente"):
        _verify_download(path, receipt)
