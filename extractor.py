"""
extractor.py
-------------
Zentrale Extraktionslogik für OCR-Text aus METS/ALTO-Dateien.
"""

import os
import json
import logging
from ocr_utils import load_xml, extract_alto_text


def extract_alto_links(mets_path: str) -> list[str]:
    """
    Extrahiert ALTO-Dateilinks aus einer METS-Datei.
    Gibt eine Liste von URLs oder lokalen Pfaden zurück.
    """
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
        except ValueError:
            return item[0]

    files.sort(key=sort_key)
    logging.info(f"{len(files)} ALTO-Dateien gefunden.")
    return [f[1] for f in files]


def extract_all_texts(mets_path: str, normalize: bool = True) -> dict[str, str]:
    """
    Lädt alle in METS referenzierten ALTO-Dateien
    und extrahiert den Text pro Seite.
    """
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


def save_full_output(texts: dict[str, str], output_path: str, fmt: str) -> None:
    """Speichert den gesamten Text in einer einzigen Datei."""
    if fmt == "json":
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(texts, f, ensure_ascii=False, indent=2)
    else:
        sep = "\n\n---\n\n" if fmt == "md" else "\n\n"
        content = sep.join(texts.values())
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
    logging.info(f"Gesamtausgabe gespeichert: {output_path}")


def save_pagewise_output(texts: dict[str, str], output_dir: str, fmt: str) -> None:
    """Speichert jede Seite einzeln in einem Unterordner."""
    os.makedirs(output_dir, exist_ok=True)
    for page, content in texts.items():
        if fmt == "json":
            out_path = os.path.join(output_dir, f"{page}.json")
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump({"page": page, "text": content}, f, ensure_ascii=False, indent=2)
        else:
            out_path = os.path.join(output_dir, f"{page}.{fmt}")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(content)
        logging.info(f"Seite gespeichert: {out_path}")


def run_extraction(mets_path: str,
                   output_format: str = "txt",
                   full: bool = True,
                   histlit: bool = False,
                   output_dir: str = ".") -> None:
    """
    Führt die gesamte OCR-Extraktion aus:
    - Liest METS-Datei
    - Extrahiert Texte aus allen ALTO-Dateien
    - Speichert Ausgabe als Gesamtdatei oder seitenweise
    """
    if not mets_path:
        raise ValueError("mets_path darf nicht leer sein.")
    if not output_dir:
        raise ValueError("output_dir darf nicht leer sein.")

    mets_path = str(mets_path)
    output_dir = str(output_dir)
    normalize = not histlit

    logging.info(f"Lese METS-Datei: {mets_path}")
    texts = extract_all_texts(mets_path, normalize=normalize)

    base_name = os.path.splitext(os.path.basename(mets_path))[0]
    os.makedirs(output_dir, exist_ok=True)

    if full:
        output_path = os.path.join(output_dir, f"{base_name}_volltext.{output_format}")
        save_full_output(texts, output_path, output_format)
    else:
        page_dir = os.path.join(output_dir, f"{base_name}_pages")
        save_pagewise_output(texts, page_dir, output_format)

    logging.info("Extraktion abgeschlossen.")
