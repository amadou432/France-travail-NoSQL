from recherche import rechercher_annonces
from annonces import afficher_annonce
from export import exporter_annonce, exporter_resultats
from statistiques import afficher_statistiques

while True:
    print("\n===== FRANCE TRAVAIL =====")
    print("Groupe 03 - Code ROME M1802")
    print("==========================")
    print("1. Rechercher des annonces")
    print("2. Afficher une annonce par ID")
    print("3. Afficher les statistiques")
    print("4. Exporter des annonces")
    print("5. Quitter")
    choix = input("\nVotre choix : ")
    if choix == "1":
        rechercher_annonces()
    elif choix == "2":
        afficher_annonce()

    elif choix == "3":
        afficher_statistiques()

    elif choix == "4":
        exporter_annonce()

    elif choix == "5":
        print("Au revoir !")
        break

    else:
        print("Choix invalide")



