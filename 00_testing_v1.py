{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Yijing Oracle Testing Notebook\n",
    "\n",
    "Dieses Notebook dient zum Testen der neuen Projektstruktur des Yijing Oracle Systems."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "# Imports und Setup\n",
    "import sys\n",
    "from pathlib import Path\n",
    "import logging\n",
    "\n",
    "# Logging konfigurieren\n",
    "logging.basicConfig(\n",
    "    level=logging.INFO,\n",
    "    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'\n",
    ")\n",
    "\n",
    "# Projektverzeichnis zum Python-Path hinzufügen\n",
    "project_dir = Path.cwd().parent  # Anpassen an tatsächlichen Pfad\n",
    "if str(project_dir) not in sys.path:\n",
    "    sys.path.insert(0, str(project_dir))\n",
    "\n",
    "# Yijing Module importieren\n",
    "from yijing import (\n",
    "    YijingOracle,\n",
    "    settings,\n",
    "    ConsultationMode,\n",
    "    cast_hypergram\n",
    ")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 1. Settings Test\n",
    "\n",
    "Zuerst testen wir die Settings-Konfiguration"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "# Settings anzeigen\n",
    "print(f\"Model Name: {settings.model_name}\")\n",
    "print(f\"Consultation Mode: {settings.consultation_mode}\")\n",
    "print(f\"Resources Dir: {settings.resources_dir}\")\n",
    "print(f\"Debug Mode: {settings.debug}\")\n",
    "\n",
    "# Prompt Template laden\n",
    "system_prompt = settings.get_system_prompt()\n",
    "print(\"\\nSystem Prompt (erste 200 Zeichen):\")\n",
    "print(system_prompt[:200], \"...\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 2. Hexagram Generation Test\n",
    "\n",
    "Testen der Hexagramm-Generierung mit der cast_hypergram Funktion"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "# Hexagramm generieren\n",
    "hypergram_data = cast_hypergram()\n",
    "\n",
    "print(\"Altes Hexagramm:\")\n",
    "print(hypergram_data.old_hexagram.to_unicode_representation())\n",
    "\n",
    "print(\"\\nWandelnde Linien:\")\n",
    "print(hypergram_data.changing_lines)\n",
    "\n",
    "print(\"\\nNeues Hexagramm:\")\n",
    "print(hypergram_data.new_hexagram.to_unicode_representation())"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 3. Oracle Initialization Test\n",
    "\n",
    "Test der YijingOracle-Klasse mit verschiedenen Konfigurationen"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "# Oracle mit Standard-Einstellungen initialisieren\n",
    "oracle = YijingOracle()\n",
    "\n",
    "# Oracle mit angepassten Einstellungen\n",
    "custom_oracle = YijingOracle(\n",
    "    custom_settings={\n",
    "        'consultation_mode': ConsultationMode.DIALOGUE,\n",
    "        'debug': True\n",
    "    }\n",
    ")\n",
    "\n",
    "print(\"Standard Oracle Mode:\", oracle.settings.consultation_mode)\n",
    "print(\"Custom Oracle Mode:\", custom_oracle.settings.consultation_mode)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 4. Consultation Test\n",
    "\n",
    "Test einer vollständigen Konsultation"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "# Testfrage\n",
    "question = \"Wie kann ich in meiner aktuellen beruflichen Situation die beste Entscheidung treffen?\"\n",
    "\n",
    "# Konsultation durchführen\n",
    "response = oracle.get_response(question)\n",
    "\n",
    "print(\"Ursprüngliches Hexagramm:\", response['hexagram_context']['original'])\n",
    "print(\"Wandelnde Linien:\", response['hexagram_context']['changing_lines'])\n",
    "print(\"Resultierendes Hexagramm:\", response['hexagram_context']['resulting'])\n",
    "print(\"\\nAntwort:\")\n",
    "print(response['answer'])"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 5. Resource Loading Test\n",
    "\n",
    "Test des Resource Loaders und der Validierung"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "from yijing.utils.validate_resources import validate_all_resources\n",
    "from yijing.utils.resource_loader import load_hexagram_data\n",
    "\n",
    "# Ressourcen validieren\n",
    "validation_result = validate_all_resources()\n",
    "print(\"Ressourcen Validierung erfolgreich:\", validation_result)\n",
    "\n",
    "# Hexagramm-Daten laden\n",
    "hex_data = load_hexagram_data(1)  # Lädt Hexagramm Nr. 1\n",
    "print(\"\\nName des ersten Hexagramms:\", hex_data['hexagram']['name'])"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 6. Formatting Test\n",
    "\n",
    "Test der Markdown-Formatierung"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "from yijing.utils.formatting import format_weissagung_markdown\n",
    "\n",
    "# Beispiel-Weissagung erstellen\n",
    "weissagung = {\n",
    "    'ursprung': hex_data,  # Verwende das zuvor geladene Hexagramm\n",
    "    'wandelnde_linien': {\n",
    "        'deutungen': [\n",
    "            {\n",
    "                'position': 1,\n",
    "                'text': 'Beispieltext',\n",
    "                'interpretation': 'Beispielinterpretation'\n",
    "            }\n",
    "        ]\n",
    "    },\n",
    "    'ergebnis': hex_data  # Verwende das gleiche für das Ergebnis\n",
    "}\n",
    "\n",
    "# Formatierung\n",
    "markdown_text = format_weissagung_markdown(weissagung)\n",
    "print(\"Markdown Output (erste 500 Zeichen):\")\n",
    "print(markdown_text[:500], \"...\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 7. Error Handling Test\n",
    "\n",
    "Test des Fehlermanagements"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "# Test mit ungültiger Hexagramm-Nummer\n",
    "try:\n",
    "    invalid_hex = load_hexagram_data(65)  # Es gibt nur 64 Hexagramme\n",
    "except Exception as e:\n",
    "    print(\"Erwarteter Fehler:\", str(e))\n",
    "\n",
    "# Test mit ungültigem Consultation Mode\n",
    "try:\n",
    "    invalid_oracle = YijingOracle(\n",
    "        custom_settings={'consultation_mode': 'invalid'}\n",
    "    )\n",
    "except Exception as e:\n",
    "    print(\"Erwarteter Fehler:\", str(e))"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
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
   "version": "3.8.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}