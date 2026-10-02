import os
import re
import zipfile
import mimetypes
import stat
from datetime import datetime

from termcolor import colored
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import exifread

PROMPT = "\033[1;35m>>>\033[0m "


# ---------- вспомогательные функции ----------

def _fmt_dt(ts: float) -> str: return datetime.fromtimestamp(ts).strftime("%A, %d %B %Y, %I:%M:%S %p")


def _fmt_dt_iso(ts: float) -> str: return datetime.fromtimestamp(ts).astimezone().isoformat()


def _fmt_size(num_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if num_bytes < 1024: return f"{num_bytes:.0f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} PB"


def _fmt_perms(mode: int) -> str: return stat.filemode(mode)


def _fmt_dms(value, ref) -> str:
    try:
        d, m, s = value
        return f"{int(float(d))} deg {int(float(m))}' {float(s):.2f}\" {ref}"
    except Exception: return f"{value} {ref}"


def _mime_type(path: str) -> str:
    try:
        import magic  # type: ignore
        return magic.from_file(path, mime=True)
    except Exception:
        guess, _ = mimetypes.guess_type(path)
        return guess or "unknown"


def _decode_gps(gps_info: dict) -> dict: return {GPSTAGS.get(k, k): v for k, v in gps_info.items()}


def _clean_xmp_value(value: str) -> str:
    if not value: return ""

    li = re.findall(r"<rdf:li[^>]*>(.*?)</rdf:li>", value, re.DOTALL | re.IGNORECASE)
    if li: value = li[-1]

    value = re.sub(r"<[^>]+>", "", value)
    value = re.sub(r"\s+", " ", value).strip()

    return value


def _print_rows(rows: list) -> None:
    if not rows: return
    width = max(len(str(label)) for label, _ in rows) + 2
    for label, value in rows: print(f"{colored(str(label).ljust(width), 'cyan')}: {value}")


def _ask_path(hint: str) -> str: return input(f"{hint} {PROMPT}").strip().strip('"').strip("'")


def _file_common_rows(path: str) -> list:
    st = os.stat(path)
    ext = os.path.splitext(path)[1].lstrip(".").lower()
    return [
        ("File Name", os.path.basename(path)),
        ("File Size", _fmt_size(st.st_size)),
        ("Created", _fmt_dt(st.st_ctime)),
        ("File Access Date/Time", _fmt_dt_iso(st.st_atime)),
        ("File Inode Change Date/Time", _fmt_dt_iso(st.st_ctime)),
        ("File Permissions", _fmt_perms(st.st_mode)),
        ("File Type Extension", ext),
        ("MIME Type", _mime_type(path)),
    ]


# ---------- изображения ----------

def _extract_copyright(path: str, tags: dict) -> str:
    value = ""

    try:
        with Image.open(path) as img:
            cp = img.getexif().get(0x8298)
            if cp: value = _clean_xmp_value(str(cp))
    except Exception: pass

    if not value:
        for key in ("Image Copyright", "EXIF Copyright", "Image XPCopyright"):
            if key in tags:
                v = _clean_xmp_value(str(tags[key]))
                if v: value = v; break

    if not value:
        try:
            with open(path, "rb") as f: raw = f.read()

            blobs = [m.group(0).decode("utf-8", errors="ignore")
                     for m in re.finditer(rb"<x:xmpmeta.*?</x:xmpmeta>", raw, re.DOTALL)]
            if not blobs: blobs = [m.group(0).decode("utf-8", errors="ignore")
                                   for m in re.finditer(rb"<rdf:RDF.*?</rdf:RDF>", raw, re.DOTALL)]

            tag_patterns = (
                r"<dc:rights[^>]*>(.*?)</dc:rights>",
                r"<photoshop:Copyright[^>]*>(.*?)</photoshop:Copyright>",
                r"<xmpRights:WebStatement[^>]*>(.*?)</xmpRights:WebStatement>",
                r"<xmpRights:Marked[^>]*>(.*?)</xmpRights:Marked>",
                r"<dc:creator[^>]*>(.*?)</dc:creator>",
            )
            attr_names = ("dc:rights", "photoshop:Copyright",
                          "xmpRights:WebStatement", "dc:creator")

            for blob in blobs:
                for pattern in tag_patterns:
                    m = re.search(pattern, blob, re.DOTALL | re.IGNORECASE)
                    if m:
                        v = _clean_xmp_value(m.group(1))
                        if v: value = v; break
                if value: break

                for attr in attr_names:
                    m = re.search(rf'{re.escape(attr)}\s*=\s*["\']([^"\']+)["\']', blob, re.IGNORECASE)
                    if m:
                        v = _clean_xmp_value(m.group(1))
                        if v: value = v; break
                if value: break

                for m in re.finditer(
                    r"<[^>]*?(?:copyright|rights|creator)[^>]*?>(.*?)</[^>]+>",
                    blob, re.DOTALL | re.IGNORECASE,
                ):
                    v = _clean_xmp_value(m.group(1))
                    if v and len(v) < 128: value = v; break
                if value: break
        except Exception as e: print(colored(f"[!] XMP parse error: {e}", "red"))

    if not value:
        try:
            with open(path, "rb") as f: raw = f.read()
            m = re.search(rb"[Cc]opyright[^<>]{0,4}([A-Za-z0-9_ .\-]{2,64})", raw)
            if m:
                v = _clean_xmp_value(m.group(1).decode("utf-8", errors="ignore"))
                if v: value = v
        except Exception: pass

    return value


def view_photo_metadata():
    path = _ask_path("path to photo")

    if not os.path.isfile(path): print(colored(f"[!] File not found: {path}", "red")); return

    print(colored("\n=== Image metadata ===\n", "magenta"))

    rows = _file_common_rows(path)

    img_format = None
    img_size = None
    exif_data = {}
    gps_data = {}

    try:
        with Image.open(path) as img:
            img_format = img.format
            img_size = img.size
            exif_data = img.getexif() or {}
    except Exception as e: print(colored(f"[!] Image read error: {e}", "red"))

    rows.append(("File Type", img_format or "unknown"))

    tags = {}
    try:
        with open(path, "rb") as f: tags = exifread.process_file(f, details=True)
    except Exception as e: print(colored(f"[!] exifread error: {e}", "red"))

    xmp_toolkit = tags.get("Image XMPToolkit") or tags.get("XMP Toolkit")
    if xmp_toolkit: rows.append(("XMP Toolkit", str(xmp_toolkit)))

    for tag_id, value in exif_data.items():
        tag = TAGS.get(tag_id, tag_id)
        if tag == "GPSInfo": gps_data = _decode_gps(value)

    lat_ref = gps_data.get("GPSLatitudeRef", "")
    lon_ref = gps_data.get("GPSLongitudeRef", "")
    lat_dms = gps_data.get("GPSLatitude")
    lon_dms = gps_data.get("GPSLongitude")

    if lat_dms: rows.append(("GPS Latitude", _fmt_dms(lat_dms, lat_ref)))
    if lon_dms: rows.append(("GPS Longitude", _fmt_dms(lon_dms, lon_ref)))

    copyright_value = _extract_copyright(path, tags)
    if copyright_value: rows.append(("Copyright", copyright_value))
    else: rows.append(("Copyright", colored("(not found)", "yellow")))

    if img_size:
        rows.append(("Image Width", img_size[0]))
        rows.append(("Image Height", img_size[1]))

    mapping = {
        "Encoding Process": ["File Encoding Process", "Image Encoding Process"],
        "Bits Per Sample": ["Image BitsPerSample", "EXIF BitsPerSample"],
        "Color Components": ["Image ColorComponents"],
        "Y Cb Cr Sub Sampling": ["Image YCbCrSubSampling"],
    }
    for label, keys in mapping.items():
        for k in keys:
            if k in tags: rows.append((label, str(tags[k]))); break

    if img_size:
        rows.append(("Image Size", f"{img_size[0]}x{img_size[1]}"))
        rows.append(("Megapixels", f"{img_size[0] * img_size[1] / 1_000_000:.1f}"))

    if lat_ref: rows.append(("GPS Latitude Ref", "North" if lat_ref == "N" else "South"))
    if lon_ref: rows.append(("GPS Longitude Ref", "East" if lon_ref == "E" else "West"))

    if lat_dms and lon_dms:
        rows.append(("GPS Position", f"{_fmt_dms(lat_dms, lat_ref)}, {_fmt_dms(lon_dms, lon_ref)}"))

    _print_rows(rows)

    if lat_dms and lon_dms:
        try:
            def to_dec(v):
                d, m, s = v
                return float(d) + float(m) / 60 + float(s) / 3600

            lat = to_dec(lat_dms)
            lon = to_dec(lon_dms)

            if lat_ref == "S": lat = -lat
            if lon_ref == "W": lon = -lon

            print(colored(f"\n[+] Google Maps: https://www.google.com/maps?q={lat},{lon}", "green"))
        except Exception: pass

    print()


# ---------- PDF ----------

def _pdf_date_to_str(raw) -> str:
    if not raw: return ""
    s = str(raw)
    m = re.match(r"D:(\d{4})(\d{2})?(\d{2})?(\d{2})?(\d{2})?(\d{2})?", s)
    if not m: return s
    parts = [p for p in m.groups() if p]
    parts += ["00"] * (6 - len(parts))
    try:
        dt = datetime(int(parts[0]), int(parts[1]), int(parts[2]),
                      int(parts[3]), int(parts[4]), int(parts[5]))
        return dt.strftime("%A, %d %B %Y, %I:%M:%S %p")
    except Exception: return s


def view_pdf_metadata():
    try:
        from pypdf import PdfReader
    except ImportError: print(colored("[!] Install pypdf: pip install pypdf", "red")); return

    path = _ask_path("path to pdf")

    if not os.path.isfile(path): print(colored(f"[!] File not found: {path}", "red")); return

    print(colored("\n=== PDF metadata ===\n", "magenta"))

    rows = _file_common_rows(path)
    rows.append(("File Type", "PDF"))

    try:
        reader = PdfReader(path)
        meta = reader.metadata or {}

        pdf_map = {
            "/Title": "Title",
            "/Author": "Author",
            "/Subject": "Subject",
            "/Keywords": "Keywords",
            "/Creator": "Creator (software)",
            "/Producer": "Producer",
            "/CreationDate": "Creation Date",
            "/ModDate": "Modification Date",
        }
        for key, label in pdf_map.items():
            val = meta.get(key)
            if not val: continue
            if key in ("/CreationDate", "/ModDate"): val = _pdf_date_to_str(val)
            rows.append((label, val))

        try:
            xmp = reader.xmp_metadata
            if xmp:
                xmp_map = {
                    "dc:title": "XMP Title",
                    "dc:creator": "XMP Creator",
                    "xmp:CreatorTool": "XMP Creator Tool",
                    "xmp:CreateDate": "XMP Create Date",
                    "xmp:ModifyDate": "XMP Modify Date",
                    "xmpMM:DocumentID": "XMP Document ID",
                    "pdf:Producer": "XMP Producer",
                }
                for attr, label in xmp_map.items():
                    val = getattr(xmp, attr.replace(":", "_"), None)
                    if val: rows.append((label, val))
        except Exception: pass

        rows.append(("Pages", len(reader.pages)))
        rows.append(("Encrypted", reader.is_encrypted))

    except Exception as e: print(colored(f"[!] PDF parse error: {e}", "red"))

    try:
        with open(path, "rb") as f: raw = f.read()
        patterns = {
            "Paths found": rb"[A-Za-z]:\\\\[^\s<>()]{3,120}",
            "UNIX paths": rb"/(?:home|Users)/[A-Za-z0-9_.\-]+/[^\s<>()]{2,120}",
            "Email addresses": rb"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}",
        }
        for label, pat in patterns.items():
            found = list({m.group(0).decode("utf-8", errors="ignore") for m in re.finditer(pat, raw)})
            if found: rows.append((label, ", ".join(found[:5]) + (" ..." if len(found) > 5 else "")))
    except Exception: pass

    _print_rows(rows)
    print()


# ---------- офисные документы ----------

def _read_office_core(path: str) -> dict:
    result = {}
    try:
        with zipfile.ZipFile(path) as z:
            names = z.namelist()

            if "docProps/core.xml" in names:
                core = z.read("docProps/core.xml").decode("utf-8", errors="ignore")
                fields = {
                    "dc:title": "Title",
                    "dc:creator": "Author",
                    "cp:lastModifiedBy": "Last Modified By",
                    "dc:subject": "Subject",
                    "dc:description": "Description",
                    "cp:keywords": "Keywords",
                    "cp:category": "Category",
                    "cp:contentStatus": "Content Status",
                    "dcterms:created": "Created",
                    "dcterms:modified": "Modified",
                    "cp:revision": "Revision",
                }
                for tag, label in fields.items():
                    m = re.search(rf"<{re.escape(tag)}[^>]*>(.*?)</{re.escape(tag)}>",
                                  core, re.DOTALL | re.IGNORECASE)
                    if m:
                        val = _clean_xmp_value(m.group(1))
                        if val: result[label] = val

            if "docProps/app.xml" in names:
                app = z.read("docProps/app.xml").decode("utf-8", errors="ignore")
                fields = {
                    "Application": "Application",
                    "AppVersion": "App Version",
                    "Company": "Company",
                    "Manager": "Manager",
                    "Template": "Template",
                    "TotalTime": "Total Editing Time (min)",
                    "Pages": "Pages",
                    "Words": "Words",
                    "Characters": "Characters",
                }
                for tag, label in fields.items():
                    m = re.search(rf"<{re.escape(tag)}[^>]*>(.*?)</{re.escape(tag)}>",
                                  app, re.DOTALL | re.IGNORECASE)
                    if m:
                        val = _clean_xmp_value(m.group(1))
                        if val: result[label] = val

            if "docProps/custom.xml" in names:
                custom = z.read("docProps/custom.xml").decode("utf-8", errors="ignore")
                for m in re.finditer(
                    r'<property[^>]*name="([^"]+)"[^>]*>(.*?)</property>',
                    custom, re.DOTALL | re.IGNORECASE,
                ):
                    name = m.group(1)
                    val = _clean_xmp_value(m.group(2))
                    if val: result[f"Custom: {name}"] = val
    except Exception as e: print(colored(f"[!] OOXML parse error: {e}", "red"))

    return result


def view_office_metadata():
    path = _ask_path("path to office file")

    if not os.path.isfile(path): print(colored(f"[!] File not found: {path}", "red")); return

    ext = os.path.splitext(path)[1].lstrip(".").lower()
    if ext not in ("docx", "xlsx", "pptx", "docm", "xlsm", "pptm"): print(colored(f"[!] Unsupported extension: .{ext}", "yellow")); return

    print(colored(f"\n=== Office document metadata ({ext}) ===\n", "magenta"))

    rows = _file_common_rows(path)
    rows.append(("File Type", ext.upper()))

    core = _read_office_core(path)
    for label in ("Title", "Author", "Last Modified By", "Subject", "Description",
                  "Keywords", "Category", "Content Status", "Created", "Modified",
                  "Revision", "Application", "App Version", "Company", "Manager",
                  "Template", "Total Editing Time (min)", "Pages", "Words",
                  "Characters"):
        if label in core: rows.append((label, core[label]))

    for label, val in core.items():
        if label.startswith("Custom: "): rows.append((label, val))

    try:
        with zipfile.ZipFile(path) as z:
            paths, emails = set(), set()
            for name in z.namelist():
                if not name.endswith(".xml"): continue
                data = z.read(name).decode("utf-8", errors="ignore")
                paths.update(re.findall(r"[A-Za-z]:\\\\[^\s<>()]{3,120}", data))
                paths.update(re.findall(r"/(?:home|Users)/[A-Za-z0-9_.\-]+/[^\s<>()]{2,120}", data))
                emails.update(re.findall(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}", data))
            if paths: rows.append(("Paths found", ", ".join(sorted(paths)[:5]) + (" ..." if len(paths) > 5 else "")))
            if emails: rows.append(("Email addresses", ", ".join(sorted(emails)[:5]) + (" ..." if len(emails) > 5 else "")))
    except Exception: pass

    _print_rows(rows)
    print()


# ---------- автоопределение ----------

def auto_detect_and_view():
    path = _ask_path("path to file")

    if not os.path.isfile(path): print(colored(f"[!] File not found: {path}", "red")); return

    ext = os.path.splitext(path)[1].lstrip(".").lower()
    mime = _mime_type(path)

    if ext in ("jpg", "jpeg", "png", "tif", "tiff", "webp", "heic", "bmp", "gif") or mime.startswith("image/"): view_photo_metadata_by_path(path)
    elif ext == "pdf" or mime == "application/pdf": view_pdf_metadata_by_path(path)
    elif ext in ("docx", "xlsx", "pptx", "docm", "xlsm", "pptm"): view_office_metadata_by_path(path)
    else: print(colored(f"[!] Unknown type: ext={ext}, mime={mime}", "yellow"))


# ---------- обёртки с уже известным путём ----------

def view_photo_metadata_by_path(path: str):
    global _ask_path
    _orig = _ask_path
    _ask_path = lambda hint: path  # type: ignore
    try: view_photo_metadata()
    finally: _ask_path = _orig


def view_pdf_metadata_by_path(path: str):
    global _ask_path
    _orig = _ask_path
    _ask_path = lambda hint: path  # type: ignore
    try: view_pdf_metadata()
    finally: _ask_path = _orig


def view_office_metadata_by_path(path: str):
    global _ask_path
    _orig = _ask_path
    _ask_path = lambda hint: path  # type: ignore
    try: view_office_metadata()
    finally: _ask_path = _orig