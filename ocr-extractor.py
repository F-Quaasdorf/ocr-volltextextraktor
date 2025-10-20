"""
ocr-extractor.py
----------------
Startpunkt des OCR-Extraktionsskripts.
Kann über Konsole oder interaktiv ausgeführt werden.

Beispiele:
    python ocr-extractor.py mets.xml -json -page
    python ocr-extractor.py
"""

import logging
from pathlib import Path
from sys import exit
from argum import get_args_or_interactive
from extractor import run_extraction


def setup_logging() -> None:
    """Logging-Setup."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )


def resolve_paths(args: dict) -> tuple[Path, Path]:
    """Validiert und normalisiert Pfade."""
    mets_in = args.get("mets_path")
    if not mets_in:
        logging.error("Kein Pfad zur METS-Datei angegeben.")
        exit(1)

    mets_path = Path(mets_in)
    if not mets_path.exists() and not str(mets_path).startswith("http"):
        logging.error(f"METS-Datei nicht gefunden: {mets_path}")
        exit(1)

    output_dir = Path(args.get("output") or mets_path.parent)
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logging.error(f"Ausgabeverzeichnis konnte nicht erstellt werden: {e}")
        exit(1)

    return mets_path, output_dir


def normalize_args(args: dict) -> dict:
    """Sichert gültige Standardwerte."""
    format_map = {"txt", "md", "json"}
    mode_map = {"full", "page"}

    out_format = args.get("format", "txt")
    if out_format not in format_map:
        logging.warning(f"Unbekanntes Format '{out_format}', verwende 'txt'.")
        out_format = "txt"

    mode = args.get("mode", "full")
    if mode not in mode_map:
        logging.warning(f"Unbekannter Modus '{mode}', verwende 'full'.")
        mode = "full"

    return {"format": out_format,
            "mode": mode,
            "histlit": bool(args.get("histlit", False)),
    }


def main() -> None:
    setup_logging()
    args = get_args_or_interactive()

    mets_path, output_dir = resolve_paths(args)
    params = normalize_args(args)

    try:
        run_extraction(mets_path=str(mets_path),
                       output_format=params["format"],
                       full=(params["mode"] == "full"),
                       histlit=params["histlit"],
                       output_dir=str(output_dir),
        )
        logging.info("OCR-Extraktion erfolgreich abgeschlossen.")
    except Exception:
        logging.exception("Fehler während der Extraktion.")
        exit(1)


if __name__ == "__main__":
    main()
