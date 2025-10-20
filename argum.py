import argparse
import sys
from pathlib import Path


def get_interactive_input():
    """
    Fragt den Nutzer interaktiv nach den wichtigsten Parametern,
    wenn das Skript ohne Befehlszeilenargumente gestartet wird.
    """
    print("OCR-Extraktor – Interaktiver Modus\n")

    mets_path = input("Pfad zur METS-Datei: ").strip()
    while not mets_path:
        mets_path = input("Pfad darf nicht leer sein. Bitte erneut eingeben: ").strip()

    fmt = input("Ausgabeformat [txt/md/json] (Standard: txt): ").strip().lower() or "txt"
    while fmt not in {"txt", "md", "json"}:
        fmt = input("Ungültige Eingabe. Bitte 'txt', 'md' oder 'json' wählen: ").strip().lower()

    mode = input("Ausgabeart [full/page] (Standard: full): ").strip().lower() or "full"
    while mode not in {"full", "page"}:
        mode = input("Ungültige Eingabe. Bitte 'full' oder 'page' wählen: ").strip().lower()

    hist = input("Historische Zeichen beibehalten? [j/n] (Standard: n): ").strip().lower()
    histlit = hist == "j"

    out_dir = input("Ausgabeverzeichnis (leer lassen für Standard): ").strip() or None

    return {"mets_path": Path(mets_path),
            "format": fmt,
            "mode": mode,
            "histlit": histlit,
            "output": Path(out_dir) if out_dir else None,
    }


def parse_args():
    parser = argparse.ArgumentParser(description="Extrahiere OCR-Volltext aus METS/ALTO-Dateien.")
    parser.add_argument("mets_path", nargs="?", help="Pfad zur METS-Datei (lokal oder URL)")
    parser.add_argument("-txt", action="store_true", help="Ausgabe als Textdatei (Standard)")
    parser.add_argument("-md", "--markdown", action="store_true", help="Ausgabe als Markdown")
    parser.add_argument("-json", action="store_true", help="Ausgabe als JSON")
    parser.add_argument("-full", action="store_true", help="Gesamter Text in einer Datei (Standard)")
    parser.add_argument("-page", action="store_true", help="Jede Seite als eigene Datei speichern")
    parser.add_argument("-histlit", action="store_true", help="Behalte historische Zeichen (keine Normalisierung)")
    parser.add_argument("-o", "--output", type=str, help="Ausgabeverzeichnis (Standard: gleiches Verzeichnis wie METS-Datei)")

    args = parser.parse_args()

    # Wenn keine Argumente → Interaktiver Modus
    import sys
    from pathlib import Path
    if len(sys.argv) == 1:
        return get_interactive_input()

    # Pfad- und Formatlogik
    mets_path = Path(args.mets_path)
    output_mode = "md" if args.markdown else "json" if args.json else "txt"
    page_mode = "page" if args.page else "full"
    normalize_text = not args.histlit

    # 🔧 Fix: Standard-Ausgabeordner, falls keiner angegeben
    output_dir = Path(args.output) if args.output else mets_path.parent

    return {"mets_path": mets_path,
            "format": output_mode,
            "mode": page_mode,
            "histlit": not normalize_text,
            "output": output_dir,
    }


def get_args_or_interactive():
    """
    Wrapper-Funktion, die automatisch entscheidet,
    ob Argumente geparst oder interaktiv abgefragt werden.
    """
    if len(sys.argv) == 1:
        return get_interactive_input()
    else:
        return parse_args()
