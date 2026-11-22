import json
from pathlib import Path
from recherche import charger_annonces

DOSSIER_EXPORT = Path(__file__).resolve().parent / "exports"


def enregistrer_json(donnees, nom_fichier):
    DOSSIER_EXPORT.mkdir(exist_ok=True)
    chemin = DOSSIER_EXPORT / nom_fichier

    with open(chemin, "w", encoding="utf-8") as fichier:
        json.dump(donnees, fichier, ensure_ascii=False, indent=4)

    print(f"\nExport réussi : {chemin}")


def exporter_annonce():
    annonces = charger_annonces()
    identifiant = input("ID de l'annonce à exporter : ").strip()

    for annonce in annonces:
        if annonce.get("id") == identifiant:
            enregistrer_json(annonce, f"annonce_{identifiant}.json")
            return

    print("Annonce introuvable.")


def exporter_resultats(resultats):
    if not resultats:
        print("Aucun résultat à exporter.")
        return

    enregistrer_json(resultats, "resultats_recherche.json")

