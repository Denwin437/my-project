# QR Code Generator

Create QR codes from the command line as PNG or SVG files: plain text, web links, Wi-Fi logins and contact cards.

## Features
- Four payload types: `text`, `url`, `wifi` and `contact` (vCard)
- PNG or SVG output, chosen by the file extension
- Adjustable error correction (L, M, Q, H), module size and border
- Input validation: only `http(s)` links, Wi-Fi secrets are escaped correctly, size and range limits
- Verified by decoding generated images back to the original text (OpenCV, test-only)

## Setup and usage
```bash
pip install -r requirements.txt
python qrgen.py -o site.png url https://example.com
python qrgen.py -o wifi.svg wifi "Home Network" --password "s3cret"
python qrgen.py -o card.png contact "Asha Rao" --phone "+91 98765 43210" --email asha@example.com
python qrgen.py -o note.png --level H text "Meet at 5pm"
```
Run `python qrgen.py --help` for all options. Errors exit with code 2 and a clear message.

## Run the tests
```bash
pip install -r requirements.txt -r requirements-dev.txt pytest
pytest
```
17 tests cover file output, round-trip decoding (including Unicode and special characters), payload formats, validation and the CLI. Without `requirements-dev.txt` the decoding tests are skipped.

## Known limitations
- Maximum 2000 characters per code.
- No logo overlay or custom colors yet.
- The Wi-Fi and contact formats follow common conventions; scanner support varies by phone.
