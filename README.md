# OCR-Volltextextraktor
Das Skript extrahiert OCR-erkannte Volltexte aus Digitalisaten. Benötigt wird lediglich die METS.XML des Digitalisats, die die Volltexte enthält (Links auf ALTO-XML). Das Skript kann auf zwei Varianten genutzt werden:
## Variante 1: Schrittweise ausführen
Im Terminal kann das Skript mit `python ocr-extractor.py` ausgeführt werden oder über jede IDE. Es müssen alle Dateien im selben Ordner liegen. Anschließend kann schrittweise den Fragen gefolgt werden.
## Variante 2: Ausführen in der Konsole mit Befehlen
Im Terminal kann das Skript über zusätzliche Befehle zu `python ocr-extractor.py` ausgeführt werden:
- `mets.xml`: Angabe des Pfads der METS-Datei
- Art der Ausgabe des Volltexts:
    * `-full`: Der Volltext wird in einer einzigen Datei gespeichert. Wird keine Ausgabeart angegeben, werden die Texte standardmäßig in einer einzigen Datei gespeichert.
    * `-page`: Der Volltext wird seitenweise in einem separaten Ordner gespeichert
- Dateiformat:
    * `-txt`: Speicherung als Textdatei. Wird kein Dateiformat angegeben, wird der Text standardmäßig als .txt gespeichert.
    * `-md`: Speicherung als Markdown
    * `-json`: Speicherung als JSON
- Umgang mit historischen Zeichen (langes s, Ligaturen u.a.):
    * `-histlit`: Historische Zeichen werden als UTF-8-codierte Zeichen beibehalten. Wird der Befehl nicht gesetzt, werden die Zeichen normalisiert: `Ich ſehe dich` --> `Ich sehe dich`
- Speicherort:
    * `-o`, `-output` + Pfad: Speicherort des Textes. Wird kein Speicherort angegeben, werden die Volltexte im selben Ordner wie die Skripte gespeichert.

Beispiel: `python ocr-extractor.py mets.xml -json -full -histlit` Für die Speicherung des Volltexts in einer einzigen Datei als JSON mit historischen Zeichen.

**Achtung, frühe Version**:

Das Skript muss weiter getestet werden.
