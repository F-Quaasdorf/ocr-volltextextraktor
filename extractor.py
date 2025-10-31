import os
import json
import logging
from typing import List, Dict
from ocr_utils import load_xml, extract_alto_text


def extract_metadata_from_mets(mets_path: str) -> Dict[str, str]:
    """Liest Metadaten (Titel, Verfasser, Erscheinungsjahr, VD-Nummer) aus der METS-Datei."""
    try:
        mets_root = load_xml(mets_path)
    except Exception as e:
        logging.warning(f"Metadaten konnten nicht aus METS gelesen werden: {e}")
        return {"title": "", "author": "", "year": "", "vd_number": ""}

    ns = {
        "mets": "http://www.loc.gov/METS/",
        "mods": "http://www.loc.gov/mods/v3",
        "dc": "http://purl.org/dc/elements/1.1/"
    }

    title = ""
    author = ""
    year = ""
    vd_number = ""

    # Titel
    title_elem = mets_root.find(".//mods:title", ns)
    if title_elem is not None and title_elem.text:
        title = title_elem.text.strip()
    else:
        dc_title = mets_root.find(".//dc:title", ns)
        if dc_title is not None and dc_title.text:
            title = dc_title.text.strip()

    # Verfasser
    name_elem = mets_root.find(".//mods:name/mods:displayForm", ns)
    if name_elem is not None and name_elem.text:
        author = name_elem.text.strip()
    else:
        dc_author = mets_root.find(".//dc:creator", ns)
        if dc_author is not None and dc_author.text:
            author = dc_author.text.strip()

    # Erscheinungsjahr
    year_elem = mets_root.find(".//mods:originInfo/mods:dateIssued", ns)
    if year_elem is not None and year_elem.text:
        year = year_elem.text.strip()
    else:
        dc_date = mets_root.find(".//dc:date", ns)
        if dc_date is not None and dc_date.text:
            year = dc_date.text.strip()

    # VD-Nummer
    for vd_type in ("vd16", "vd17", "vd18"):
        vd_elem = mets_root.find(f".//mods:identifier[@type='{vd_type}']", ns)
        if vd_elem is not None and vd_elem.text:
            vd_number = f"{vd_type.upper()} {vd_elem.text.strip()}"
            break

    return {"title": title, "author": author, "year": year, "vd_number": vd_number}


def extract_alto_links(mets_path: str) -> List[str]:
    """Extrahiert ALTO-Dateilinks aus der METS-Datei."""
    try:
        mets_root = load_xml(mets_path)
    except Exception as e:
        logging.error(f"Konnte METS-Datei nicht laden: {e}")
        raise

    ns = {"mets": "http://www.loc.gov/METS/", "xlink": "http://www.w3.org/1999/xlink"}
    files = []

    for file_elem in mets_root.findall(".//mets:fileGrp[@USE='FULLTEXT']/mets:file", ns):
        file_id = file_elem.attrib.get("ID", "")
        flocat = file_elem.find(".//mets:FLocat", ns)
        if flocat is not None:
            href = flocat.attrib.get("{http://www.w3.org/1999/xlink}href", "")
            if href:
                files.append((file_id, href))

    def sort_key(item):
        try:
            return int(item[0].split("_")[-1])
        except Exception:
            return item[0]

    files.sort(key=sort_key)
    logging.info(f"{len(files)} ALTO-Dateien gefunden.")
    return [f[1] for f in files]


def extract_structure(mets_path: str) -> List[Dict[str, str]]:
    """Liest die logische Struktur (structMap TYPE='LOGICAL') aus METS."""
    try:
        mets_root = load_xml(mets_path)
    except Exception as e:
        logging.error(f"Konnte METS-Datei für Struktur nicht laden: {e}")
        return []

    ns = {"mets": "http://www.loc.gov/METS/"}
    struct_divs = mets_root.findall(".//mets:structMap[@TYPE='LOGICAL']//mets:div", ns)
    structure = []

    for div in struct_divs:
        order = div.attrib.get("ORDER")
        div_type = div.attrib.get("TYPE", "")
        label = div.attrib.get("LABEL", "")
        order_val = int(order) if order and order.isdigit() else None
        if div_type or label:
            structure.append({"order": order_val, "type": div_type, "label": label})

    logging.info(f"{len(structure)} Strukturelemente gefunden.")
    return structure


def extract_all_texts(mets_path: str, normalize: bool = True) -> Dict[str, str]:
    """Lädt alle referenzierten ALTO-Dateien und extrahiert den Text pro Seite."""
    alto_links = extract_alto_links(mets_path)
    texts = {}

    for i, link in enumerate(alto_links, start=1):
        try:
            alto_root = load_xml(str(link))
            text = extract_alto_text(alto_root, normalize=normalize)
            texts[f"page_{i:04d}"] = text
            logging.info(f"Seite {i:04d} erfolgreich verarbeitet.")
        except Exception as e:
            logging.warning(f"Fehler beim Verarbeiten von {link}: {e}")
            texts[f"page_{i:04d}"] = ""

    return texts


def save_full_output(texts: Dict[str, str], output_path: str, fmt: str,
                     structure=None, metadata=None) -> None:
    """Speichert den gesamten Text in einer einzigen Datei (mit Struktur + Metadaten)."""
    metadata = metadata or {}
    num_pages = len(texts)

    if fmt == "json":
        combined = []
        if structure or metadata:
            combined.append({
                "structure": {
                    "metadata": {
                        "title": metadata.get("title", ""),
                        "author": metadata.get("author", ""),
                        "year": metadata.get("year", ""),
                        "vd_number": metadata.get("vd_number", ""),
                        "source": os.path.basename(metadata.get("_mets_path", "")) if metadata.get("_mets_path") else None,
                        "num_pages": num_pages
                    },
                    "divs": structure or []
                }
            })
        for i, (page, content) in enumerate(texts.items(), start=1):
            combined.append({
                "page": page,
                "order": i,
                "text": content,
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "year": metadata.get("year", ""),
                "vd_number": metadata.get("vd_number", ""),
                "source": os.path.basename(metadata.get("_mets_path", "")) if metadata.get("_mets_path") else None
            })
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(combined, f, ensure_ascii=False, indent=2)
    else:
        sep = "\n\n---\n\n" if fmt == "md" else "\n\n"
        content = sep.join(texts.values())
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
    logging.info(f"Gesamtausgabe gespeichert: {output_path}")


def save_pagewise_output(texts: Dict[str, str], output_dir: str, fmt: str,
                         structure=None, metadata=None) -> None:
    """Speichert jede Seite einzeln (mit Strukturdatei content.json)."""
    metadata = metadata or {}
    os.makedirs(output_dir, exist_ok=True)
    num_pages = len(texts)

    if fmt == "json":
        # content.json mit Struktur + Metadaten + Seitenzahl
        if structure or metadata:
            content_path = os.path.join(output_dir, "content.json")
            content_data = {
                "metadata": {
                    "title": metadata.get("title", ""),
                    "author": metadata.get("author", ""),
                    "year": metadata.get("year", ""),
                    "vd_number": metadata.get("vd_number", ""),
                    "source": os.path.basename(metadata.get("_mets_path", "")) if metadata.get("_mets_path") else None,
                    "num_pages": num_pages
                },
                "divs": structure or []
            }
            with open(content_path, "w", encoding="utf-8") as f:
                json.dump(content_data, f, ensure_ascii=False, indent=2)
            logging.info(f"Strukturdatei gespeichert: {content_path}")

        for i, (page, content) in enumerate(texts.items(), start=1):
            out_path = os.path.join(output_dir, f"{page}.json")
            data = {
                "page": page,
                "order": i,
                "text": content,
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "year": metadata.get("year", ""),
                "vd_number": metadata.get("vd_number", ""),
                "source": os.path.basename(metadata.get("_mets_path", "")) if metadata.get("_mets_path") else None
            }
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logging.info(f"Seite gespeichert: {out_path}")


def run_extraction(mets_path: str,
                   output_format: str = "txt",
                   full: bool = True,
                   histlit: bool = False,
                   output_dir: str = ".") -> None:
    """Führt die gesamte OCR-Extraktion aus."""
    if not mets_path:
        raise ValueError("mets_path darf nicht leer sein.")
    if not output_dir:
        raise ValueError("output_dir darf nicht leer sein.")

    normalize = not histlit
    logging.info(f"Lese METS-Datei: {mets_path}")

    metadata = extract_metadata_from_mets(mets_path)
    metadata["_mets_path"] = mets_path  # Quelle speichern

    structure = extract_structure(mets_path)
    texts = extract_all_texts(mets_path, normalize=normalize)

    base_name = os.path.splitext(os.path.basename(mets_path))[0]
    os.makedirs(output_dir, exist_ok=True)

    if full:
        output_path = os.path.join(output_dir, f"{base_name}_volltext.{output_format}")
        save_full_output(texts, output_path, output_format, structure=structure, metadata=metadata)
    else:
        page_dir = os.path.join(output_dir, f"{base_name}_pages")
        save_pagewise_output(texts, page_dir, output_format, structure=structure, metadata=metadata)

    logging.info("Extraktion abgeschlossen.")
