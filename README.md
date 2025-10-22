# OCR-Volltextextraktor
Python-Skript zur Extraktion von OCR-erkannten Volltexten aus Digitalisaten. Dazu wird ein METS.XML eingelesen, um die ALTO-Dateien zu extrahieren und den Text als .txt, JSON oder Markdown auszugeben.
## Voraussetzungen
Benötigt werden die Bibliotheken `requests` und `lxml`.
## Anwendung
Das Skript ist über die Konsole ausführbar.
### Befehlszeilenargumente
Für die Verwendung mit Argumenten der Befehlszeile muss eine METS.XML angegeben werden.

```python ocr-extractor.py mets.xml [Optionen]```

Folgende Optionen sind verfügbar:
| Option | Beschreibung
|:-------|:---------------------------------
| `-txt` | Ausgabe als .txt (wird als Standard angewandt)
| `-json`| Ausgabe als JSON (Standard: .txt)
| `-md` | Ausgabe als Markdown (Standard: .txt)
| `-full` | Gesamter Text wird in einer Datei gespeichert (wird als Standard angewandt)
| `-page` | Jede Seite wird als eigene Datei gespeichert
| `-histlist` | Beibehaltung historischer Zeichen (Bspw. Ligaturen, ſ statt s)
| `-o <Pfad>` | Ausgabeverzeichnis angeben (standardmäßig wird der gleiche Ordner verwandt)

Beispiel: 

```python ocr-extractor.py mets.xml -page -json -histlit -o ausgabe/```

Der Text wird seitenweise als JSON mit historischen Zeichen in einem neu angelegten Ordner `ausgabe` gespeichert.
### Ohne Befehlszeilenargumente
Das Skript kann interaktiv ausgeführt werden. Über

```python ocr-extractor.py```

werden alle erforderlichen Schritte nacheinander abgefragt. 
