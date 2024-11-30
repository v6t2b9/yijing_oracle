{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Texterfassung Steuerzentrale für Yijing"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 1. Imports und Konfiguration"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import os\n",
    "import json\n",
    "from pathlib import Path\n",
    "from typing import List, Optional, Dict, Any\n",
    "from typing_extensions import TypedDict, NotRequired\n",
    "\n",
    "import google.generativeai as genai\n",
    "import pandas as pd\n",
    "from IPython.display import Markdown, display"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### API-Konfiguration"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Konfiguration des API-Schlüssels\n",
    "api_key = os.environ.get(\"API_KEY\")\n",
    "if not api_key:\n",
    "    raise ValueError(\"Die Umgebungsvariable 'API_KEY' ist nicht gesetzt.\")\n",
    "genai.configure(api_key=api_key)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Modellwahl"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Auswahl des Modells basierend auf der Umgebung oder Standardwahl\n",
    "model_speed = {\n",
    "    'dumb': 'gemini-1.5-flash-8b',\n",
    "    'fast': 'gemini-1.5-flash-latest',\n",
    "    'clever': 'gemini-1.5-pro-latest',\n",
    "    'experimental': 'gemini-exp-1121',\n",
    "}\n",
    "model_type = os.getenv(\"MODEL_TYPE\", model_speed['experimental'])\n",
    "print(\"Verwendetes Modell:\", model_type)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 2. Datenimport"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Yijing Text einlesen"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "yijing_txt_path = Path('yijing/resources/yijing.txt')\n",
    "\n",
    "# Funktionen zum Lesen des Yijing-Texts\n",
    "def read_yijing_lines(path: Path = yijing_txt_path) -> List[str]:\n",
    "    with path.open('r', encoding='utf-8') as f:\n",
    "        return f.readlines()\n",
    "\n",
    "def read_yijing_txt(path: Path = yijing_txt_path) -> str:\n",
    "    with path.open('r', encoding='utf-8') as f:\n",
    "        return f.read()\n",
    "\n",
    "# Laden der Daten\n",
    "yijing_txt = read_yijing_txt()\n",
    "yijing_chapters = read_yijing_lines()\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Erste Einblicke in die Daten"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Anzeige der ersten 5 Kapitel\n",
    "yijing_chapters[:5]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Anzeige des ersten Kapitels\n",
    "yijing_chapters[0]"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 3. Datenverarbeitung"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Strukturierter JSON-Text des ersten Kapitels"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "yijing_processed = \"\"\"\n",
    "{\n",
    "  \"hexagram\": {\n",
    "    \"name\": \"GUAI / DER DURCHBRUCH\",\n",
    "    \"subtitle\": \"Die Entschlossenheit\",\n",
    "    \"trigrams\": {\n",
    "      \"above\": {\n",
    "        \"name\": \"Dui\",\n",
    "        \"attributes\": \"das Heitere, der See\"\n",
    "      },\n",
    "      \"below\": {\n",
    "        \"name\": \"Kien\",\n",
    "        \"attributes\": \"das Schöpferische, der Himmel\"\n",
    "      }\n",
    "    },\n",
    "    \"meaning\": {\n",
    "      \"description\": \"Das Zeichen bedeutet einerseits einen Durchbruch nach lange angesammelter Spannung, wie den Durchbruch eines geschwellten Flusses durch seine Dämme, wie einen Wolkenbruch. Auf menschliche Verhältnisse übertragen, ist es andererseits die Zeit, da allmählich die Gemeinen im Schwinden sind. Ihr Einfluß ist im Abnehmen, und durch eine entschlossene Aktion kommt eine Änderung der Verhältnisse zum Durchbruch.\",\n",
    "      \"season\": \"dritter Monat (April-Mai)\"\n",
    "    }\n",
    "  },\n",
    "  \"judgment\": {\n",
    "    \"description\": \"Der Durchbruch. Entschlossen muß man am Hof des Königs die Sache bekanntmachen. Der Wahrheit gemäß muß sie verkündet werden. Gefahr! Man muß seine eigene Stadt benachrichtigen. Nicht fördernd ist es, zu den Waffen zu greifen. Fördernd ist es, etwas zu unternehmen.\",\n",
    "    \"analysis\": [\n",
    "      \"Leidenschaft und Vernunft können nicht zusammen bestehen, daher ist ein unbedingter Kampf notwendig.\",\n",
    "      \"Entschlossenheit muß auf Stärke und Freundlichkeit beruhen.\",\n",
    "      \"Kompromisse mit dem Schlechten sind nicht möglich.\",\n",
    "      \"Der Kampf darf nicht direkt durch Gewalt geführt werden.\",\n",
    "      \"Der Edle beginnt bei sich selbst, um das Böse zu entwaffnen.\"\n",
    "    ]\n",
    "  },\n",
    "  \"image\": {\n",
    "    \"description\": \"Der See ist an den Himmel emporgestiegen: das Bild des Durchbruchs.\",\n",
    "    \"lesson\": \"Der Edle spendet Reichtum nach unten hin und scheut es, bei seiner Tugend zu verweilen.\",\n",
    "    \"warning\": \"Sammeln führt zu Zerstreuen; rechtzeitige Vorbereitung kann einem gewaltsamen Zusammenbruch vorbeugen.\"\n",
    "  },\n",
    "  \"lines\": [\n",
    "    {\n",
    "      \"position\": \"Anfangs eine\",\n",
    "      \"text\": \"Mächtig in den vorwärtsschreitenden Zehen. Geht man hin und ist der Sache nicht gewachsen, so macht man einen Fehler.\",\n",
    "      \"interpretation\": \"Zu Beginn ist entschlossenes Voranschreiten schwierig. Blindes Draufgängertum führt zu unheilvollen Folgen.\"\n",
    "    },\n",
    "    {\n",
    "      \"position\": \"Neun auf zweitem Platz\",\n",
    "      \"text\": \"Alarmruf. Abends und nachts Waffen. Fürchte nichts.\",\n",
    "      \"interpretation\": \"Vorsicht und Wachsamkeit schützen vor Gefahren. Besonnenheit ist der rechte Weg zur Sicherheit.\"\n",
    "    },\n",
    "    {\n",
    "      \"position\": \"Neun auf drittem Platz\",\n",
    "      \"text\": \"Mächtig in den Backenknochen zu sein bringt Unheil.\",\n",
    "      \"interpretation\": \"Entschlossenheit ist notwendig, aber äußere Stärke zur falschen Zeit kann die Lage verschlimmern.\"\n",
    "    },\n",
    "    {\n",
    "      \"position\": \"Neun auf viertem Platz\",\n",
    "      \"text\": \"An den Oberschenkeln ist keine Haut, und das Gehen fällt schwer.\",\n",
    "      \"interpretation\": \"Eigensinn führt zu Konflikten. Würde man Ratschläge annehmen, könnte alles gutgehen.\"\n",
    "    },\n",
    "    {\n",
    "      \"position\": \"Neun auf fünftem Platz\",\n",
    "      \"text\": \"Dem Unkraut gegenüber braucht es feste Entschlossenheit.\",\n",
    "      \"interpretation\": \"Hindernisse müssen mit Entschlossenheit überwunden werden, ohne vom Weg abzukommen.\"\n",
    "    },\n",
    "    {\n",
    "      \"position\": \"Oben eine Sechs\",\n",
    "      \"text\": \"Kein Ruf! Schließlich kommt Unheil.\",\n",
    "      \"interpretation\": \"Nachlässigkeit beim Entfernen des Bösen führt zu erneutem Übel. Gründliche Arbeit ist notwendig.\"\n",
    "    }\n",
    "  ]\n",
    "}\n",
    "\"\"\"\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 4. Type Definitions für JSON Output"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "class Trigram(TypedDict):\n",
    "    name: str\n",
    "    attributes: str\n",
    "    element: NotRequired[str]  # Optional: z.B. Holz, Feuer, Erde, Metall, Wasser\n",
    "    symbolism: NotRequired[str]  # Optional: Symbolische Bedeutung des Trigramms\n",
    "\n",
    "class Trigrams(TypedDict):\n",
    "    above: Trigram\n",
    "    below: Trigram\n",
    "\n",
    "class Meaning(TypedDict):\n",
    "    description: str\n",
    "    season: NotRequired[str]  # Optional: Jahreszeit (z.B. \"Frühling\", \"Sommer\")\n",
    "    symbols: NotRequired[List[str]]  # Optional: Schlüsselwörter oder Symbole\n",
    "    context: NotRequired[str]  # Optional: Allgemeiner Kontext oder Bedeutung\n",
    "\n",
    "class Judgment(TypedDict):\n",
    "    description: str\n",
    "    analysis: List[str]  # Analyse oder Kommentare zum Urteil\n",
    "    advice: NotRequired[str]  # Optional: Handlungsempfehlungen aus dem Urteil\n",
    "\n",
    "class Image(TypedDict):\n",
    "    description: str\n",
    "    lesson: str\n",
    "    warning: NotRequired[str]  # Optional: Warnungen oder Vorsichtsmaßnahmen\n",
    "    additional_notes: NotRequired[str]  # Optional: Zusätzliche Kommentare oder Metaphern\n",
    "\n",
    "class Line(TypedDict):\n",
    "    position: str  # Position der Linie (z.B. 'Anfangs eine')\n",
    "    text: str  # Originaltext der Linie\n",
    "    interpretation: str  # Interpretation der Linie\n",
    "\n",
    "class HexagramCore(TypedDict):\n",
    "    name: str\n",
    "    subtitle: str\n",
    "    trigrams: Trigrams\n",
    "    meaning: Meaning\n",
    "\n",
    "class JudgmentDetail(TypedDict):\n",
    "    description: str\n",
    "    analysis: List[str]\n",
    "\n",
    "class ImageDetail(TypedDict):\n",
    "    description: str\n",
    "    lesson: str\n",
    "    warning: str\n",
    "\n",
    "class HexagramInfo(TypedDict):\n",
    "    hexagram: HexagramCore\n",
    "    judgment: JudgmentDetail\n",
    "    image: ImageDetail\n",
    "    lines: List[Line]\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 5. Funktionen"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Funktion zur Verarbeitung eines Hexagramms"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "def process_hexagram(text: str, model: genai.GenerativeModel) -> HexagramInfo:\n",
    "    \"\"\"\n",
    "    Verarbeitet einen Hexagramm-Text und gibt strukturierte Daten zurück.\n",
    "    \"\"\"\n",
    "    prompt = HEXAGRAM_PROMPT + text\n",
    "    result = model.generate_content(\n",
    "        prompt,\n",
    "        generation_config=genai.GenerationConfig(\n",
    "            response_mime_type=\"application/json\",\n",
    "            response_schema=HexagramInfo\n",
    "        ),\n",
    "    )\n",
    "    return result.candidates[0].content"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Funktionen zur Verarbeitung mehrerer Hexagramme"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import os\n",
    "import json\n",
    "from pathlib import Path\n",
    "from typing import List\n",
    "\n",
    "def load_hexagram_files(raw_dir: Path, number_of_hexagrams = None) -> List[Path]:\n",
    "    \"\"\"\n",
    "    Lädt alle Hexagramm-Textdateien aus dem angegebenen Verzeichnis.\n",
    "\n",
    "    Args:\n",
    "        raw_dir (Path): Pfad zum Verzeichnis mit den Hexagramm-Textdateien.\n",
    "\n",
    "    Returns:\n",
    "        List[Path]: Liste der Pfade zu den Hexagramm-Textdateien.\n",
    "    \"\"\"\n",
    "    if not raw_dir.exists() or not raw_dir.is_dir():\n",
    "        raise FileNotFoundError(f\"Das Verzeichnis {raw_dir} existiert nicht oder ist kein Verzeichnis.\")\n",
    "    \n",
    "    hexagram_files = sorted(raw_dir.glob(\"hexagram_*.txt\"))\n",
    "    if not hexagram_files:\n",
    "        raise FileNotFoundError(f\"Keine Hexagramm-Textdateien gefunden im Verzeichnis {raw_dir}.\")\n",
    "    \n",
    "    # Lade die Anzahl der Hexagramme (number_of_hexagrams), falls angegeben\n",
    "    if number_of_hexagrams:\n",
    "        hexagram_files = hexagram_files[:number_of_hexagrams]\n",
    "    else:\n",
    "        pass\n",
    "\n",
    "    print(f\"{len(hexagram_files)} Hexagramm-Dateien verarbeitet.\")\n",
    "    return hexagram_files\n",
    "\n",
    "def process_and_save_hexagram(file_path: Path, model: genai.GenerativeModel, output_dir: Path) -> None:\n",
    "    \"\"\"\n",
    "    Verarbeitet eine einzelne Hexagramm-Textdatei und speichert die resultierende JSON-Datei.\n",
    "\n",
    "    Args:\n",
    "        file_path (Path): Pfad zur Hexagramm-Textdatei.\n",
    "        model (genai.GenerativeModel): Konfiguriertes Generatives Modell.\n",
    "        output_dir (Path): Pfad zum Ausgabe-Verzeichnis für die JSON-Dateien.\n",
    "    \"\"\"\n",
    "    try:\n",
    "        with file_path.open('r', encoding='utf-8') as f:\n",
    "            hexagram_text = f.read()\n",
    "        \n",
    "        # Verarbeite den Hexagramm-Text\n",
    "        result = process_hexagram(hexagram_text, model)\n",
    "        \n",
    "        # Bestimme den Ausgabepfad\n",
    "        #hexagram_number = file_path.stem.split('_')[-1]  # z.B. 'hexagram_01' -> '01'\n",
    "        #output_file = output_dir / f\"hexagram_{hexagram_number}.json\"\n",
    "        \n",
    "        # Speichere die JSON-Daten\n",
    "        #with output_file.open('w', encoding='utf-8') as f_out:\n",
    "            #json.dump(result, f_out, ensure_ascii=False, indent=4)\n",
    "        \n",
    "        print(f\"Hexagramm {hexagram_number} erfolgreich verarbeitet und gespeichert.\")\n",
    "        return result\n",
    "    \n",
    "    except Exception as e:\n",
    "        print(f\"Fehler beim Verarbeiten von {file_path.name}: {e}\")\n",
    "\n",
    "def process_hexagrams(raw_dir: Path, output_dir: Path, model: genai.GenerativeModel, number_of_hexagrams = None) -> None:\n",
    "    \"\"\"\n",
    "    Verarbeitet alle Hexagramm-Textdateien aus dem Rohverzeichnis und speichert die JSON-Dateien.\n",
    "\n",
    "    Args:\n",
    "        raw_dir (Path): Pfad zum Verzeichnis mit den Hexagramm-Textdateien.\n",
    "        output_dir (Path): Pfad zum Ausgabe-Verzeichnis für die JSON-Dateien.\n",
    "        model (genai.GenerativeModel): Konfiguriertes Generatives Modell.\n",
    "    \"\"\"\n",
    "    # Lade die Anzahl der Hexagramme, falls angegeben\n",
    "\n",
    "    if number_of_hexagrams:\n",
    "        hexagram_files = load_hexagram_files(raw_dir, number_of_hexagrams)\n",
    "    else:\n",
    "        hexagram_files = load_hexagram_files(raw_dir)\n",
    "    \n",
    "    # Erstelle das Ausgabe-Verzeichnis, falls es nicht existiert\n",
    "    output_dir.mkdir(parents=True, exist_ok=True)\n",
    "    \n",
    "    hexagram_results = []\n",
    "\n",
    "    # Verarbeite jede Datei einzeln\n",
    "    for file_path in hexagram_files:\n",
    "        hexagram_results.append(process_and_save_hexagram(file_path, model, output_dir))\n",
    "    \n",
    "    print(\"Alle Hexagramme wurden verarbeitet.\")\n",
    "    return hexagram_results\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 6. Initialisierung"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Modell starten und Chat initialisieren"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "HEXAGRAM_PROMPT = \"\"\"\n",
    "Du bist ein I Ging-Experte mit der Aufgabe, Hexagramm-Texte zu analysieren und in ein spezifisches JSON-Format zu überführen.\n",
    "\n",
    "Wandle den Eingabetext in folgendes Format um:\n",
    "\n",
    "{\n",
    "  \"hexagram\": {\n",
    "    \"name\": \"Name des Hexagramms (z.B. 'GUAI / DER DURCHBRUCH')\",\n",
    "    \"subtitle\": \"Untertitel oder Kernbedeutung\", (z.B. 'Die Entschlossenheit')\n",
    "    \"trigrams\": {\n",
    "      \"above\": {\n",
    "        \"name\": \"Name des oberen Trigramms\", (z.B. 'Dui')\n",
    "        \"attributes\": \"Eigenschaften des Trigramms\" (z.B. 'das Heitere, der See')\n",
    "      },\n",
    "      \"below\": {\n",
    "        \"name\": \"Name des unteren Trigramms\", (z.B. 'Kien')\n",
    "        \"attributes\": \"Eigenschaften des Trigramms\" (z.B. 'das Schöpferische, der Himmel')\n",
    "      }\n",
    "    },\n",
    "    \"meaning\": {\n",
    "      \"description\": \"Hauptbedeutung des Hexagramms\", (z.B. 'Das Zeichen bedeutet...')\n",
    "      \"season\": \"Zugeordnete Jahreszeit\" (z.B. 'dritter Monat (April-Mai)')\n",
    "    }\n",
    "  },\n",
    "  \"judgment\": {\n",
    "    \"description\": \"Der Urteilstext\", (z.B. 'Der Durchbruch...')\n",
    "    \"analysis\": [\n",
    "      \"Liste von Analysepunkten zum Urteil\" (z.B. 'Leidenschaft und Vernunft...')\n",
    "    ]\n",
    "  },\n",
    "  \"image\": {\n",
    "    \"description\": \"Beschreibung des Bildes\", (z.B. 'Der See ist an den Himmel emporgestiegen...')\n",
    "    \"lesson\": \"Lehre für den:die Edle:n\", (z.B. 'Der:die Edle spendet Reichtum...')\n",
    "    \"warning\": \"Warnung oder zusätzliche Hinweise\" # (z.B. 'Sammeln führt zu Zerstreuen...')\n",
    "  },\n",
    "  \"lines\": [\n",
    "    {\n",
    "      \"position\": \"Position der Linie\", (z.B. 'Anfangs eine Sechs')\",\n",
    "      \"text\": \"Text der Linie\", z.B. 'Mächtig in den vorwärtsschreitenden Zehen...'\n",
    "      \"interpretation\": \"Interpretation der Linie\", z.B. 'Zu Beginn ist entschlossenes Voranschreiten...'\n",
    "    }\n",
    "  ]\n",
    "}\n",
    "\n",
    "Wichtige Hinweise:\n",
    "1. Extrahiere alle relevanten Informationen aus dem Eingabetext\n",
    "2. Behalte die originale Formulierung wo möglich bei\n",
    "3. Stelle sicher, dass alle Pflichtfelder gefüllt sind\n",
    "4. Das lines-Array muss genau 6 Einträge enthalten\n",
    "5. Füge fehlende Informationen mit \"Keine Information verfügbar\" ein\n",
    "\n",
    "Analysiere nun den folgenden Hexagramm-Text und gib ihn im spezifizierten JSON-Format zurück:\n",
    "\"\"\""
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Systemanweisung für das Modell (optional)\n",
    "#instruction = \"\"\"Du bist ein hilfreicher Assistent für die Analyse von Hexagrammen.\"\"\"\n",
    "instruction = HEXAGRAM_PROMPT"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "\n",
    "# Erstellen des Modells\n",
    "model = genai.GenerativeModel(\n",
    "    model_type,\n",
    "    system_instruction=instruction\n",
    ")\n",
    "\n",
    "# Chat-Instanz starten\n",
    "chat = model.start_chat()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 7. Verarbeitung und Export"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Hexagramm verarbeiten und anzeigen"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "def process_hexagram_text(hexagram_text):\n",
    "    \"\"\"\n",
    "    Verarbeitet einen Hexagramm-Text und gibt strukturierte Daten zurück.\n",
    "\n",
    "    Args:\n",
    "        hexagram_text (str): Der Hexagramm-Text.\n",
    "\n",
    "    Returns:\n",
    "        dict: Strukturierte Daten des Hexagramms.\n",
    "    \"\"\"\n",
    "\n",
    "    result = chat.send_message(hexagram_text)\n",
    "\n",
    "    # Überprüfen, ob die Antwort Teile enthält, um Fehler zu vermeiden\n",
    "    if hasattr(result, 'parts') and len(result.parts) > 0:\n",
    "        json_text = result.parts[0].text\n",
    "        # Entfernen von Codeblöcken, falls vorhanden\n",
    "        formated_text = json_text.strip('```json\\n').strip('```')\n",
    "        \n",
    "        # Laden des JSON in ein Python-Dictionary\n",
    "        data = json.loads(formated_text)\n",
    "        \n",
    "        # Anzeige der strukturierten Daten\n",
    "        #display(Markdown(\"### Verarbeitetes Hexagramm\"))\n",
    "        #display(data)\n",
    "    else:\n",
    "        print(\"Keine Antwortteile gefunden.\")\n",
    "\n",
    "    return data"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "\n",
    "# Erstellen des Modells\n",
    "model = genai.GenerativeModel(\n",
    "    model_type,\n",
    "    system_instruction=instruction\n",
    ")\n",
    "\n",
    "# Chat-Instanz starten\n",
    "chat = model.start_chat()\n",
    "\n",
    "i = 1\n",
    "\n",
    "extracted_hexagrams = []\n",
    "for chapter in yijing_chapters[:2]:\n",
    "    print(f\"Processing chapter {i}\")\n",
    "    extracted_hexagrams.append(process_hexagram_text(chapter))\n",
    "    print(f\"Processed chapter {i}\")\n",
    "    i += 1"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "i = 0\n",
    "\n",
    "for chapter in yijing_chapters:\n",
    "    print(chapter)\n",
    "    try:\n",
    "        save_hexagram_json(i + 1, extracted_hexagrams)\n",
    "        print(f\"Kapitel {i} erfolgreich verarbeitet und gespeichert.\")\n",
    "    except Exception as e:\n",
    "        print(f\"Fehler beim Speichern von Kapitel {i}: {e}\")\n",
    "    i += 1"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# type(extracted_hexagrams[0]) ist dict und soll in json umgewandelt werden\n",
    "# json.dumps() wandelt Python-Daten in JSON-Strings um\n",
    "\n",
    "hexagram_number = 1\n",
    "\n",
    "def save_hexagram_json(hexagram_number: int, extracted_hexagrams: List[Dict[str, Any]]) -> None:\n",
    "    if hexagram_number < 10:\n",
    "        hexagram_file_number_str = str(hexagram_number).zfill(2)\n",
    "    else:\n",
    "        hexagram_file_number_str = str(hexagram_number)\n",
    "\n",
    "    print(\"Hexagramm-Nummer:\", hexagram_file_number_str)\n",
    "\n",
    "    extracted_hexagram = extracted_hexagrams[hexagram_number - 1]\n",
    "    hexagram_json = json.dumps(extracted_hexagram)\n",
    "\n",
    "    # speichere das JSON in einer Datei\n",
    "    output_file = Path(f\"export/hexagram_json/hexagram_{hexagram_file_number_str}.json\")\n",
    "\n",
    "    with output_file.open('w', encoding='utf-8') as f:\n",
    "        f.write(hexagram_json)\n",
    "\n",
    "    print(f\"Die JSON-Daten wurden in der Datei {output_file} gespeichert.\")\n",
    "    # lade das JSON aus der Datei\n",
    "    with output_file.open('r', encoding='utf-8') as f:\n",
    "        loaded_json = json.load(f)\n",
    "\n",
    "def save_all_hexagram_json(extracted_hexagrams: List[Dict[str, Any]]) -> None:\n",
    "    for hexagram_number in range(0, len(extracted_hexagrams)):\n",
    "        save_hexagram_json(hexagram_number + 1, extracted_hexagrams)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "save_all_hexagram_json(extracted_hexagrams)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Export der Linien in ein DataFrame"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Konvertiere die \"lines\"-Daten in ein pandas DataFrame\n",
    "lines_df = pd.DataFrame(data.get('lines', []))\n",
    "lines_df"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Speicherung der Daten als JSON"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Speichern der strukturierten Daten in einer JSON-Datei\n",
    "output_path = Path('export/hexagram_json/processed_hexagram_XX.json')\n",
    "output_path.parent.mkdir(parents=True, exist_ok=True)\n",
    "with output_path.open('w', encoding='utf-8') as f:\n",
    "    json.dump(data, f, ensure_ascii=False, indent=4)\n",
    "print(f\"Daten gespeichert unter {output_path}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 8. Zusätzliche Analysen (Optional)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Beispiel: Analyse der Interpretationen"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "if 'lines_df' in locals():\n",
    "    # Beispielhafte Analyse: Häufigkeit von Schlüsselwörtern in den Interpretationen\n",
    "    from collections import Counter\n",
    "    import re\n",
    "    \n",
    "    all_interpretations = ' '.join(lines_df['interpretation'].dropna().tolist())\n",
    "    words = re.findall(r'\\w+', all_interpretations.lower())\n",
    "    word_counts = Counter(words)\n",
    "    \n",
    "    # Anzeige der häufigsten Wörter\n",
    "    common_words = word_counts.most_common(10)\n",
    "    common_df = pd.DataFrame(common_words, columns=['Wort', 'Häufigkeit'])\n",
    "    display(Markdown(\"### Häufigste Wörter in den Interpretationen\"))\n",
    "    display(common_df)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Weiteres"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import os\n",
    "import json\n",
    "from pathlib import Path\n",
    "from typing import List\n",
    "\n",
    "def load_hexagram_files(raw_dir: Path, number_of_hexagrams = None) -> List[Path]:\n",
    "    \"\"\"\n",
    "    Lädt alle Hexagramm-Textdateien aus dem angegebenen Verzeichnis.\n",
    "\n",
    "    Args:\n",
    "        raw_dir (Path): Pfad zum Verzeichnis mit den Hexagramm-Textdateien.\n",
    "\n",
    "    Returns:\n",
    "        List[Path]: Liste der Pfade zu den Hexagramm-Textdateien.\n",
    "    \"\"\"\n",
    "    if not raw_dir.exists() or not raw_dir.is_dir():\n",
    "        raise FileNotFoundError(f\"Das Verzeichnis {raw_dir} existiert nicht oder ist kein Verzeichnis.\")\n",
    "    \n",
    "    hexagram_files = sorted(raw_dir.glob(\"hexagram_*.txt\"))\n",
    "    if not hexagram_files:\n",
    "        raise FileNotFoundError(f\"Keine Hexagramm-Textdateien gefunden im Verzeichnis {raw_dir}.\")\n",
    "    \n",
    "    # Lade die Anzahl der Hexagramme (number_of_hexagrams), falls angegeben\n",
    "    if number_of_hexagrams:\n",
    "        hexagram_files = hexagram_files[:number_of_hexagrams]\n",
    "    else:\n",
    "        pass\n",
    "\n",
    "    print(f\"{len(hexagram_files)} Hexagramm-Dateien verarbeitet.\")\n",
    "    return hexagram_files\n",
    "\n",
    "def process_and_save_hexagram(file_path: Path, model: genai.GenerativeModel, output_dir: Path) -> None:\n",
    "    \"\"\"\n",
    "    Verarbeitet eine einzelne Hexagramm-Textdatei und speichert die resultierende JSON-Datei.\n",
    "\n",
    "    Args:\n",
    "        file_path (Path): Pfad zur Hexagramm-Textdatei.\n",
    "        model (genai.GenerativeModel): Konfiguriertes Generatives Modell.\n",
    "        output_dir (Path): Pfad zum Ausgabe-Verzeichnis für die JSON-Dateien.\n",
    "    \"\"\"\n",
    "    try:\n",
    "        with file_path.open('r', encoding='utf-8') as f:\n",
    "            hexagram_text = f.read()\n",
    "        \n",
    "        # Verarbeite den Hexagramm-Text\n",
    "        result = process_hexagram(hexagram_text, model)\n",
    "        \n",
    "        # Bestimme den Ausgabepfad\n",
    "        #hexagram_number = file_path.stem.split('_')[-1]  # z.B. 'hexagram_01' -> '01'\n",
    "        #output_file = output_dir / f\"hexagram_{hexagram_number}.json\"\n",
    "        \n",
    "        # Speichere die JSON-Daten\n",
    "        #with output_file.open('w', encoding='utf-8') as f_out:\n",
    "            #json.dump(result, f_out, ensure_ascii=False, indent=4)\n",
    "        \n",
    "        print(f\"Hexagramm {hexagram_number} erfolgreich verarbeitet und gespeichert.\")\n",
    "        return result\n",
    "    \n",
    "    except Exception as e:\n",
    "        print(f\"Fehler beim Verarbeiten von {file_path.name}: {e}\")\n",
    "\n",
    "def process_hexagrams(raw_dir: Path, output_dir: Path, model: genai.GenerativeModel, number_of_hexagrams = None) -> None:\n",
    "    \"\"\"\n",
    "    Verarbeitet alle Hexagramm-Textdateien aus dem Rohverzeichnis und speichert die JSON-Dateien.\n",
    "\n",
    "    Args:\n",
    "        raw_dir (Path): Pfad zum Verzeichnis mit den Hexagramm-Textdateien.\n",
    "        output_dir (Path): Pfad zum Ausgabe-Verzeichnis für die JSON-Dateien.\n",
    "        model (genai.GenerativeModel): Konfiguriertes Generatives Modell.\n",
    "    \"\"\"\n",
    "    # Lade die Anzahl der Hexagramme, falls angegeben\n",
    "\n",
    "    if number_of_hexagrams:\n",
    "        hexagram_files = load_hexagram_files(raw_dir, number_of_hexagrams)\n",
    "    else:\n",
    "        hexagram_files = load_hexagram_files(raw_dir)\n",
    "    \n",
    "    # Erstelle das Ausgabe-Verzeichnis, falls es nicht existiert\n",
    "    output_dir.mkdir(parents=True, exist_ok=True)\n",
    "    \n",
    "    hexagram_results = []\n",
    "\n",
    "    # Verarbeite jede Datei einzeln\n",
    "    for file_path in hexagram_files:\n",
    "        hexagram_results.append(process_and_save_hexagram(file_path, model, output_dir))\n",
    "    \n",
    "    print(\"Alle Hexagramme wurden verarbeitet.\")\n",
    "    return hexagram_results\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "\n",
    "# Beispielhafte Nutzung der Funktionen\n",
    "# Definiere die Verzeichnisse\n",
    "raw_directory = Path('import/yijing_raw/')\n",
    "json_output_directory = Path('import/yijing_json/')\n",
    "\n",
    "# Starte die Verarbeitung\n",
    "processed_hexagrams = process_hexagrams(raw_directory, json_output_directory, model, 3)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "gemini_310",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.10.15"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
