
from collections import Counter
from recherche import charger_annonces


def afficher_statistiques():
    annonces = charger_annonces()

    print("\n===== STATISTIQUES FRANCE TRAVAIL =====")

    # Nombre total d'annonces
    print(f"\nNombre total d'annonces : {len(annonces)}")

    # Répartition par type de contrat
    contrats = Counter(
        annonce.get("typeContrat") or "Non renseigné"
        for annonce in annonces
    )

    print("\n--- TYPES DE CONTRATS ---")
    for contrat, nombre in contrats.most_common():
        print(f"{contrat} : {nombre} annonce(s)")

    # Répartition par ville
    villes = Counter(
        (annonce.get("lieuTravail") or {}).get("libelle")
        or "Non renseigné"
        for annonce in annonces
    )

    print("\n--- TOP DES LOCALISATIONS ---")
    for ville, nombre in villes.most_common(10):
        print(f"{ville} : {nombre} annonce(s)")

    # Répartition par intitulé de poste
    metiers = Counter(
        annonce.get("intitule") or "Non renseigné"
        for annonce in annonces
    )

    print("\n--- TOP DES MÉTIERS ---")
    for metier, nombre in metiers.most_common(10):
        print(f"{metier} : {nombre} annonce(s)")

    # Pourcentage de CDI
    nombre_cdi = contrats.get("CDI", 0)
    total = len(annonces)

    pourcentage_cdi = (
        nombre_cdi / total * 100 if total > 0 else 0
    )

    print(f"\nPourcentage de CDI : {pourcentage_cdi:.1f}%")
