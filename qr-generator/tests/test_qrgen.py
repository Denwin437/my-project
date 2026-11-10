import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import qrgen  # noqa: E402

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def decode(path):
    cv2 = pytest.importorskip("cv2")
    img = cv2.imread(str(path))
    text, _, _ = cv2.QRCodeDetector().detectAndDecode(img)
    return text


def test_png_is_valid_file(tmp_path):
    out = qrgen.make_qr("hello", tmp_path / "a.png")
    assert out.read_bytes().startswith(PNG_MAGIC)


def test_svg_output(tmp_path):
    out = qrgen.make_qr("hello", tmp_path / "a.svg")
    assert "<svg" in out.read_text()


def test_creates_missing_folders(tmp_path):
    assert qrgen.make_qr("x", tmp_path / "deep" / "dir" / "q.png").exists()


@pytest.mark.parametrize("data", ["hello world", "https://example.com/a?b=1&c=2", "ünïcödé ✓"])
def test_round_trip_decodes_to_original(tmp_path, data):
    qrgen.make_qr(data, tmp_path / "q.png")
    assert decode(tmp_path / "q.png") == data


def test_wifi_round_trip(tmp_path):
    payload = qrgen.wifi_payload("Home Net", "p;ss,word")
    assert payload == r"WIFI:T:WPA;S:Home Net;P:p\;ss\,word;;"
    qrgen.make_qr(payload, tmp_path / "w.png")
    assert decode(tmp_path / "w.png") == payload


def test_wifi_open_network_and_validation():
    assert qrgen.wifi_payload("Cafe", security="nopass") == "WIFI:T:NOPASS;S:Cafe;P:;;"
    with pytest.raises(ValueError):
        qrgen.wifi_payload("Cafe")
    with pytest.raises(ValueError):
        qrgen.wifi_payload("", "x")
    with pytest.raises(ValueError):
        qrgen.wifi_payload("Cafe", "x", "WPA3")


def test_url_validation():
    assert qrgen.url_payload(" https://example.com ") == "https://example.com"
    for bad in ("example.com", "javascript:alert(1)", "ftp://x.com", "http://"):
        with pytest.raises(ValueError):
            qrgen.url_payload(bad)


def test_contact_payload():
    card = qrgen.contact_payload("Asha Rao", "+91 98765 43210", "asha@example.com")
    assert card.startswith("BEGIN:VCARD") and "FN:Asha Rao" in card and card.endswith("END:VCARD")
    with pytest.raises(ValueError):
        qrgen.contact_payload("  ")
    with pytest.raises(ValueError):
        qrgen.contact_payload("A", email="nope")


@pytest.mark.parametrize(
    "kwargs",
    [{"data": ""}, {"data": "x" * 2001}, {"data": "x", "level": "Z"}, {"data": "x", "box_size": 0},
     {"data": "x", "border": 99}],
)
def test_make_qr_rejects_bad_input(tmp_path, kwargs):
    with pytest.raises(ValueError):
        qrgen.make_qr(path=tmp_path / "q.png", **kwargs)


def test_rejects_unknown_extension(tmp_path):
    with pytest.raises(ValueError):
        qrgen.make_qr("x", tmp_path / "q.jpg")


def test_cli_success_and_failure(tmp_path, capsys):
    out = tmp_path / "c.png"
    assert qrgen.main(["-o", str(out), "url", "https://example.com"]) == 0
    assert out.exists()
    assert qrgen.main(["-o", str(out), "url", "nope"]) == 2
    assert "error:" in capsys.readouterr().err
