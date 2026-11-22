
from recherche import charger_annonces


def afficher_annonce():
    annonces = charger_annonces()

    print("\n===== DÉTAIL D'UNE ANNONCE =====")
    identifiant = input("ID de l'annonce : ").strip()

    for annonce in annonces:
        if annonce.get("id") == identifiant:
            lieu = annonce.get("lieuTravail") or {}

            print("\n----------------------------")
            print("ID :", annonce.get("id", "Non renseigné"))
            print("Titre :", annonce.get("intitule", "Non renseigné"))
            print("Contrat :", annonce.get("typeContrat", "Non renseigné"))
            print("Lieu :", lieu.get("libelle", "Non renseigné"))
            print("Description :", annonce.get("description", "Non renseigné"))
            print("----------------------------")
            return

    print("Aucune annonce trouvée avec cet ID.")
