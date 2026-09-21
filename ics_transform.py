#!/usr/bin/env python3
"""
Récupère un calendrier ICS en ligne, applique un traitement sur les événements
(ici : renommage du titre), et génère un nouveau fichier .ics.

Dépendances :
    pip install requests icalendar

Configuration :
    Renseigne ICS_URL ci-dessous avec le lien de ton calendrier.

Usage :
    python ics_transform.py
"""

import os
import re
import requests
from icalendar import Calendar

# URL du calendrier ICS à récupérer.
# Peut être surchargée par la variable d'environnement ICS_URL
# (pratique pour GitHub Actions : mets l'URL dans un secret plutôt
# qu'en clair dans le code).
ICS_URL = os.environ.get("ICS_URL", "https://exemple.com/mon-calendrier.ics")

# Nom du fichier de sortie, généré dans le même dossier que ce script
OUTPUT_FILENAME = "calendrier_modifie.ics"


def fetch_ics(url: str) -> bytes:
    """Télécharge le contenu brut du fichier .ics depuis une URL."""
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return response.content


def transform_title(original_title: str, event=None) -> str:
    """
    Ne garde que le nom de la matière, extrait de la ligne
    "Matière : ..." présente dans le champ DESCRIPTION.
    Exemples : "Anglais : MyCow", "Algorithmique et Programmation
    Orienté Objet".

    On ne parse pas le SUMMARY directement car son format varie trop
    (préfixes "fermé -", "amphi 9 -", "Soutenance -", etc.).

    Si aucune ligne "Matière :" n'est trouvée (ex : jour férié),
    le titre original est conservé tel quel.
    """
    if event is not None:
        description = str(event.get("description", ""))
        match = re.search(r"Mati[eè]re\s*:\s*([^\n]+)", description)
        if match:
            return match.group(1).strip()

    return original_title


def process_calendar(raw_ics: bytes) -> Calendar:
    """Parse le calendrier et modifie chaque événement (SUMMARY)."""
    cal = Calendar.from_ical(raw_ics)

    for component in cal.walk():
        if component.name == "VEVENT":
            original_title = str(component.get("summary", ""))
            new_title = transform_title(original_title, component)
            component["summary"] = new_title

    return cal


def save_ics(cal: Calendar, output_path: str) -> None:
    """Écrit le calendrier transformé dans un nouveau fichier .ics."""
    with open(output_path, "wb") as f:
        f.write(cal.to_ical())


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, OUTPUT_FILENAME)

    print(f"Téléchargement du calendrier depuis {ICS_URL} ...")
    raw_ics = fetch_ics(ICS_URL)

    print("Traitement des événements ...")
    cal = process_calendar(raw_ics)

    print(f"Écriture du nouveau fichier ICS dans {output_path} ...")
    save_ics(cal, output_path)

    print("Terminé.")


if __name__ == "__main__":
    main()