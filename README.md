# GENESIS-OSINT-Tool-v1.1.0
![GENESIS | Preview ](https://github.com/sou1ton-exe/GENESIS-OSINT-Tool-v1.1.0/blob/main/images/preview.jpg)

# GENESIS — OSINT Tool v1.1.0

A set of basic tools for gathering information from open sources (OSINT).

**Author:** [sou1toon](https://dalink.to/sou1toon)

**Telegram Channel:** [@s_lowcode_w](https://t.me/s_lowcode_w)

---

## About

GENESIS is a command-line Python utility for basic OSINT reconnaissance. It bundles several tools for extracting file metadata and checking IP addresses, email addresses, and usernames.

The project is built for educational purposes and distributed as open-source code.

---

## Features

| # | Feature | Description | Status |
|---|---------|-------------|--------|
| 1 | Image metadata | EXIF, GPS coordinates, XMP, copyright, Google Maps link | done |
| 2 | PDF metadata | Author, creation date, software, XMP, embedded paths & emails | done |
| 3 | Office document metadata | DOCX / XLSX / PPTX / DOCM / XLSM / PPTM | done |
| 4 | Auto-detect file type | Automatically picks the right parser by extension/MIME | done |
| 5 | IP / domain info | Geolocation and provider data via the 2ip API | done |
| 6 | Email check | Holehe + XposedOrNot + EmailRep | not done |
| 7 | Username check | Account search across 3000+ sites via Maigret | done |
| 8 | Phone check | Telegram + carrier lookup | not done |

---

## Project Structure

```
GENESIS/
├── main.py              # Entry point, menu and banner
├── metadata.py          # Metadata parsing: images, PDF, office files
├── ip_info.py           # IP / domain / URL information
├── email_info.py        # Email check (Holehe, XposedOrNot, EmailRep)
├── nickname_info.py     # Username check via Maigret
├── phone_info.py        # Phone check (work in progress)
├── prints.py            # Logo, menu panel, prompts
├── requirements.txt     # Dependencies
└── README.md
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/sou1ton-exe/GENESIS-OSINT-Tool-v1.1.0
cd GENESIS-OSINT-Tool-v1.1.0/genesis
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install external tools (optional)

```bash
pip install holehe      # email check across 120+ platforms
pip install maigret     # username search across 3000+ sites
```

For proper MIME detection in `metadata.py`, install `python-magic`:

```bash
pip install python-magic
# Linux: sudo apt install libmagic1
# Windows: pip install python-magic-bin
```

---

## Usage

Run the tool:

```bash
python main.py
```

You will see an interactive menu:

```
[1] Viewing image metadata
[2] Viewing PDF metadata
[3] Viewing office document metadata
[4] Auto-detect file type
[5] Information about an IP address or domain
[6] Check email (120+ platforms) - not done [x]
[7] Check nickname (3000+ sites)
[8] Check phone number (telegram + operator) - not done [x]
[0] exit
```

Pick an option by entering its number and follow the prompts.

---

## Examples

### Image metadata

```
>>> 1
path to photo >>> /home/user/photo.jpg

=== Image metadata ===

File Name            : photo.jpg
File Size            : 2.4 MB
Created              : Monday, 15 January 2024, 03:42:11 PM
GPS Latitude         : 55 deg 45' 21.00" N
GPS Longitude        : 37 deg 37' 04.00" E
Copyright            : John Doe
Image Size           : 4032x3024
Megapixels           : 12.2

[+] Google Maps: https://www.google.com/maps?q=55.7558,37.6178
```

### IP information

```
>>> 5
IP / domain / URL >>> github.com

=== IP / Domain info ===
Target: github.com
IP Address           : 140.82.121.4
Domain               : github.com

--- [ Geolocation ] ---
country              : United States
city                 : San Francisco
...

--- [ Provider ] ---
name                 : GitHub, Inc.
...
```

### Username check

```
>>> 7
Username / nickname: sou1toon
```

Maigret scans 3000+ sites and prints discovered accounts directly to the console.

---

## Dependencies

| Package | Purpose |
|---------|---------|
| termcolor | Colored console output |
| Pillow | Image processing |
| exifread | EXIF parsing |
| pypdf | PDF reading |
| python-docx, openpyxl, python-pptx | Office documents |
| olefile | Legacy MS Office format |
| requests | HTTP requests |
| 2ip | IP geolocation |
| holehe | Email platform check |
| maigret | Username search |

---

## Limitations & Warnings

- Items 6 and 8 (email and phone) are marked as "not done". The email code exists but is commented out / non-functional.
- Some APIs have rate limits (EmailRep, XposedOrNot) — frequent requests may trigger `429 Too Many Requests`.
- Maigret can take a long time (up to 30 minutes for a full scan).
- The tool is intended for lawful use only: checking your own data, authorized pentesting, and educational purposes.

---

## Development

### Adding a new feature

1. Create a module, e.g. `new_module.py`.
2. Implement a function `information_about_<something>()`.
3. Import the module in `main.py` and add an entry to the menu (`prints.py`).

### Output formatting

For consistent output, use the `_print_rows(rows)` helper:

```python
rows = [("Label", "Value"), ("Another", 123)]
_print_rows(rows)
```

---

## License

This project is distributed for educational purposes. The author is not responsible for any use that violates the law.

---

## Credits

- [Holehe](https://github.com/megadose/holehe)
- [Maigret](https://github.com/soxoj/maigret)
- [2ip](https://2ip.io/)
- [XposedOrNot](https://xposedornot.com/)
- [EmailRep](https://emailrep.io/)

---

GENESIS v1.1.0 — Open source code to explore
