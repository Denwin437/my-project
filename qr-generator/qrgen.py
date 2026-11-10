"""QR code generator: text, URLs, Wi-Fi logins and contact cards to PNG or SVG."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from urllib.parse import urlparse

import qrcode
import qrcode.image.svg
from qrcode.constants import ERROR_CORRECT_H, ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q

LEVELS = {"L": ERROR_CORRECT_L, "M": ERROR_CORRECT_M, "Q": ERROR_CORRECT_Q, "H": ERROR_CORRECT_H}
MAX_CHARS = 2000


def _escape(value: str) -> str:
    """Escape characters that are special inside Wi-Fi and vCard-style payloads."""
    for ch in ("\\", ";", ",", ":", '"'):
        value = value.replace(ch, "\\" + ch)
    return value


def url_payload(url: str) -> str:
    parsed = urlparse(url.strip())
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("URL must start with http:// or https:// and include a host")
    return url.strip()


def wifi_payload(ssid: str, password: str | None = None, security: str = "WPA") -> str:
    security = security.upper()
    if security not in ("WPA", "WEP", "NOPASS"):
        raise ValueError("security must be WPA, WEP or nopass")
    if not ssid:
        raise ValueError("SSID must not be empty")
    if security != "NOPASS" and not password:
        raise ValueError("a password is required unless security is nopass")
    pw = "" if security == "NOPASS" else _escape(password or "")
    return f"WIFI:T:{security};S:{_escape(ssid)};P:{pw};;"


def contact_payload(name: str, phone: str = "", email: str = "") -> str:
    if not name.strip():
        raise ValueError("name must not be empty")
    if email and "@" not in email:
        raise ValueError("email looks invalid")
    lines = ["BEGIN:VCARD", "VERSION:3.0", f"FN:{name.strip()}"]
    if phone:
        lines.append(f"TEL:{phone.strip()}")
    if email:
        lines.append(f"EMAIL:{email.strip()}")
    lines.append("END:VCARD")
    return "\n".join(lines)


def make_qr(data: str, path: str | Path, level: str = "M", box_size: int = 10, border: int = 4) -> Path:
    """Render data to a PNG or SVG file chosen by the file extension."""
    if not data:
        raise ValueError("nothing to encode")
    if len(data) > MAX_CHARS:
        raise ValueError(f"data too long ({len(data)} chars, max {MAX_CHARS})")
    if level.upper() not in LEVELS:
        raise ValueError("error-correction level must be one of L, M, Q, H")
    if not 1 <= box_size <= 50:
        raise ValueError("box size must be between 1 and 50")
    if not 1 <= border <= 20:
        raise ValueError("border must be between 1 and 20")

    out = Path(path)
    ext = out.suffix.lower()
    if ext not in (".png", ".svg"):
        raise ValueError("output file must end in .png or .svg")

    qr = qrcode.QRCode(error_correction=LEVELS[level.upper()], box_size=box_size, border=border)
    qr.add_data(data)
    qr.make(fit=True)
    if ext == ".svg":
        img = qr.make_image(image_factory=qrcode.image.svg.SvgPathImage)
    else:
        img = qr.make_image(fill_color="black", back_color="white")
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(out))
    return out


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="qrgen", description="Generate QR codes as PNG or SVG.")
    p.add_argument("-o", "--output", default="qr.png", help="output file (.png or .svg)")
    p.add_argument("--level", default="M", help="error correction: L, M, Q or H")
    p.add_argument("--box-size", type=int, default=10, help="pixels per module")
    p.add_argument("--border", type=int, default=4, help="quiet-zone width in modules")
    sub = p.add_subparsers(dest="kind", required=True)
    t = sub.add_parser("text", help="plain text")
    t.add_argument("text")
    u = sub.add_parser("url", help="a web link")
    u.add_argument("url")
    w = sub.add_parser("wifi", help="Wi-Fi login")
    w.add_argument("ssid")
    w.add_argument("--password", default=None)
    w.add_argument("--security", default="WPA", help="WPA, WEP or nopass")
    c = sub.add_parser("contact", help="contact card (vCard)")
    c.add_argument("name")
    c.add_argument("--phone", default="")
    c.add_argument("--email", default="")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.kind == "text":
            data = args.text
        elif args.kind == "url":
            data = url_payload(args.url)
        elif args.kind == "wifi":
            data = wifi_payload(args.ssid, args.password, args.security)
        else:
            data = contact_payload(args.name, args.phone, args.email)
        out = make_qr(data, args.output, args.level, args.box_size, args.border)
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"Saved {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
