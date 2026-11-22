
import json
from pathlib import Path

FICHIER = (
    Path(__file__).resolve().parent
    / "data"
    / "annonces_test.json"
)


def charger_annonces():
    with open(FICHIER, "r", encoding="utf-8") as fichier:
        return json.load(fichier)


def rechercher_annonces():
    annonces = charger_annonces()

    print("\n===== RECHERCHE D'ANNONCES =====")

    mot_cle = input("Mot-clé (facultatif) : ").strip().lower()
    ville = input("Ville (facultatif) : ").strip().lower()
    contrat = input("Contrat CDI/CDD (facultatif) : ").strip().lower()

    resultats = []

    for annonce in annonces:
        titre = annonce.get("intitule", "").lower()
        description = annonce.get("description", "").lower()
        lieu = annonce.get("lieuTravail") or {}
        localisation = lieu.get("libelle", "").lower()
        type_contrat = annonce.get("typeContrat", "").lower()

        if mot_cle and mot_cle not in titre + " " + description:
            continue

        if ville and ville not in localisation:
            continue

        if contrat and contrat != type_contrat:
            continue

        resultats.append(annonce)

    print(f"\n{len(resultats)} annonce(s) trouvée(s).\n")

    for annonce in resultats:
        print(
            f"{annonce['id']} | "
            f"{annonce['intitule']} | "
            f"{annonce['lieuTravail']['libelle']} | "
            f"{annonce['typeContrat']}"
        )

    return resultats
