"""
ocr_utils.py
-------------
Hilfsfunktionen für die OCR-Text-Extraktion:
- Laden und Parsen von XML (lokal oder HTTP)
- Extraktion von Text aus ALTO-Dateien
- Optionale Normalisierung historischer Zeichen
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import requests
import logging
import re


def load_xml(source) -> ET.Element:
    """
    Lädt eine XML-Datei (lokal oder über HTTP).
    Gibt das Wurzelelement zurück.
    """
    source_str = str(source)
    try:
        if source_str.startswith("http"):
            response = requests.get(source_str, timeout=20)
            response.raise_for_status()
            return ET.fromstring(response.content)
        else:
            path = Path(source_str)
            with path.open("rb") as f:
                return ET.parse(f).getroot()
    except Exception as e:
        logging.error(f"Fehler beim Laden von XML ({source_str}): {e}")
        raise


def extract_alto_text(alto_root: ET.Element, normalize: bool = True) -> str:
    """
    Extrahiert den Text aus einer ALTO-XML-Struktur.
    Wenn normalize=True, werden historische Zeichen modernisiert.
    """
    ns = {"alto": "http://www.loc.gov/standards/alto/ns-v4#"}
    lines = []

    # Versucht, TextLine-Elemente zu finden (robust gegenüber Namespace-Abweichungen)
    for line_elem in alto_root.findall(".//alto:TextLine", ns) or alto_root.findall(".//TextLine"):
        words = [w.attrib.get("CONTENT", "") for w in line_elem.findall(".//alto:String", ns)]
        line_text = " ".join(w for w in words if w)
        if normalize:
            line_text = normalize_historical_characters(line_text)
        lines.append(line_text)

    return "\n".join(lines)


def normalize_historical_characters(text: str) -> str:
    """
    Normalisiert häufige historische Buchstabenformen
    wie das lange s (ſ), Ligaturen und Akzentvarianten.
    Diese Funktion kann je nach Projektbedarf erweitert werden.
    """
    replacements = {"ſ": "s",     # langes s
                    "ꝛ": "r",     # rundes r
                    "æ": "ae", "Æ": "Ae",
                    "œ": "oe", "Œ": "Oe",        
                    "ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl", "ﬃ": "ffi", "ﬄ": "ffl",
                    "ꞵ": "ß",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Entferne überflüssige Leerzeichen vor Satzzeichen
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)
    return text.strip()
