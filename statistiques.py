from src.db import get_db

LIBELLES_CONTRAT = {
    "CDI": "CDI",
    "CDD": "CDD",
    "MIS": "Intérim",
    "LIB": "Profession libérale",
}


def repartition_contrats(collection):
    pipeline = [
        {"$group": {
            "_id": {"$ifNull": ["$typeContrat", "Non renseigné"]},
            "nb": {"$sum": 1},
        }},
        {"$sort": {"nb": -1, "_id": 1}},
    ]
    return [
        (LIBELLES_CONTRAT.get(d["_id"], d["_id"]), d["nb"])
        for d in collection.aggregate(pipeline)
    ]


def part_alternance(collection):
    total = collection.count_documents({})
    nb = collection.count_documents({"alternance": True})
    pourcentage = nb / total * 100 if total > 0 else 0
    return nb, total, pourcentage


def top_departements(collection, limite=10):
    pipeline = [
        {"$group": {
            "_id": {"$arrayElemAt": [
                {"$split": [
                    {"$ifNull": ["$lieuTravail.libelle", "Non renseigné"]},
                    " - ",
                ]},
                0,
            ]},
            "nb": {"$sum": 1},
        }},
        {"$sort": {"nb": -1, "_id": 1}},
        {"$limit": limite},
    ]
    resultats = []
    for d in collection.aggregate(pipeline):
        nom = "Télétravail (100 %)" if d["_id"] == "France" else d["_id"]
        resultats.append((nom, d["nb"]))
    return resultats


def top_champ(collection, chemin, limite=10):
    """Top des valeurs d'un champ simple. Les annonces sans valeur sont ignorées."""
    filtre = {chemin: {"$nin": [None, ""]}}
    nb_renseignes = collection.count_documents(filtre)
    pipeline = [
        {"$match": filtre},
        {"$group": {"_id": "$" + chemin, "nb": {"$sum": 1}}},
        {"$sort": {"nb": -1, "_id": 1}},
        {"$limit": limite},
    ]
    resultats = [(d["_id"], d["nb"]) for d in collection.aggregate(pipeline)]
    return resultats, nb_renseignes


def top_tableau(collection, tableau, champ="libelle", limite=10):
    """Top des valeurs d'un champ à l'intérieur d'un tableau (competences, langues)."""
    chemin = tableau + "." + champ
    nb_annonces = collection.count_documents(
        {tableau + ".0": {"$exists": True}}
    )
    pipeline = [
        {"$unwind": "$" + tableau},
        {"$match": {chemin: {"$nin": [None, ""]}}},
        {"$group": {"_id": "$" + chemin, "nb": {"$sum": 1}}},
        {"$sort": {"nb": -1, "_id": 1}},
        {"$limit": limite},
    ]
    resultats = [(d["_id"], d["nb"]) for d in collection.aggregate(pipeline)]
    return resultats, nb_annonces


def evolution_par_jour(collection):
    pipeline = [
        {"$match": {"dateCreation": {"$type": "string"}}},
        {"$group": {
            "_id": {"$substrCP": ["$dateCreation", 0, 10]},
            "nb": {"$sum": 1},
        }},
        {"$sort": {"_id": 1}},
    ]
    return [(d["_id"], d["nb"]) for d in collection.aggregate(pipeline)]

def evolution_par_mois(collection):
    pipeline = [
        {"$match": {"dateCreation": {"$type": "string"}}},
        {"$group": {
            "_id": {"$substrCP": ["$dateCreation", 0, 7]},
            "nb": {"$sum": 1},
        }},
        {"$sort": {"_id": 1}},
    ]
    return [(d["_id"], d["nb"]) for d in collection.aggregate(pipeline)]

def part_handicap(collection):
    total = collection.count_documents({})
    criteres = {
        "Employeurs engagés handicap": {"employeurHandiEngage": True},
        "Annonces accessibles aux travailleurs handicapés": {"accessibleTH": True},
        "Entreprises adaptées": {"entrepriseAdaptee": True},
        "Au moins un de ces trois critères": {"$or": [
            {"employeurHandiEngage": True},
            {"accessibleTH": True},
            {"entrepriseAdaptee": True},
        ]},
    }
    resultats = []
    for nom, filtre in criteres.items():
        nb = collection.count_documents(filtre)
        pct = nb / total * 100 if total > 0 else 0
        resultats.append((nom, nb, pct))
    return resultats

def repartition_duree_travail(collection):
    total = collection.count_documents({})
    champ = "dureeTravailLibelle"
    nb_plein = collection.count_documents({champ: {"$regex": "^[0-9]+H"}})
    nb_partiel = collection.count_documents({champ: {"$regex": "^Temps partiel"}})
    nb_renseigne = collection.count_documents({champ: {"$nin": [None, ""]}})
    return [
        ("Temps plein (heures hebdomadaires indiquées)", nb_plein),
        ("Temps partiel", nb_partiel),
        ("Renseigné sans durée précise", nb_renseigne - nb_plein - nb_partiel),
        ("Non renseigné", total - nb_renseigne),
    ]

def part_teletravail(collection):
    total = collection.count_documents({})
    motif = "t.l.travail"
    negation = "(pas de|sans|aucun)\\s+t.l.travail"
    regex = {"$regex": motif, "$options": "i"}
    filtre = {"$and": [
        {"description": {"$not": {"$regex": negation, "$options": "i"}}},
        {"$or": [
            {"description": regex},
            {"lieuTravail.libelle": regex},
            {"contexteTravail.conditionsExercice": regex},
            {"contexteTravail.horaires": regex},
        ]},
    ]}
    nb = collection.count_documents(filtre)
    pourcentage = nb / total * 100 if total > 0 else 0
    return nb, total, pourcentage

VIDES = [None, "", [], {}]

CHAMPS_IMBRIQUES = [
    "lieuTravail.libelle",
    "lieuTravail.commune",
    "lieuTravail.codePostal",
    "lieuTravail.latitude",
    "lieuTravail.longitude",
    "entreprise.nom",
    "entreprise.url",
    "salaire.libelle",
    "salaire.complement1",
    "contact.nom",
    "contact.courriel",
    "contact.urlPostulation",
    "agence.courriel",
]


def taux_remplissage_champs(collection):
    """Taux de remplissage de chaque champ de premier niveau."""
    total = collection.count_documents({})
    pipeline = [
        {"$project": {"champs": {"$objectToArray": "$$ROOT"}}},
        {"$unwind": "$champs"},
        {"$match": {"champs.k": {"$ne": "_id"}}},
        {"$group": {
            "_id": "$champs.k",
            "nb": {"$sum": {"$cond": [
                {"$in": ["$champs.v", {"$literal": VIDES}]}, 0, 1
            ]}},
        }},
        {"$sort": {"nb": -1, "_id": 1}},
    ]
    resultats = []
    for d in collection.aggregate(pipeline):
        pct = d["nb"] / total * 100 if total > 0 else 0
        resultats.append((d["_id"], d["nb"], pct))
    return resultats


def taux_remplissage_imbriques(collection):
    total = collection.count_documents({})
    resultats = []
    for chemin in CHAMPS_IMBRIQUES:
        nb = collection.count_documents({chemin: {"$nin": VIDES}})
        pct = nb / total * 100 if total > 0 else 0
        resultats.append((chemin, nb, pct))
    return resultats


def classement_completude(collection, meilleurs=True, limite=3):
    """Annonces classées selon le nombre de champs de premier niveau renseignés."""
    ordre = -1 if meilleurs else 1
    pipeline = [
        {"$project": {
            "_id": 0,
            "id": 1,
            "intitule": 1,
            "score": {"$size": {"$filter": {
                "input": {"$objectToArray": "$$ROOT"},
                "as": "c",
                "cond": {"$and": [
                    {"$ne": ["$$c.k", "_id"]},
                    {"$not": [{"$in": ["$$c.v", {"$literal": VIDES}]}]},
                ]},
            }}},
        }},
        {"$sort": {"score": ordre, "id": 1}},
        {"$limit": limite},
    ]
    return [
        (d.get("id"), d.get("intitule"), d["score"])
        for d in collection.aggregate(pipeline)
    ]


def afficher_qualite(collection):
    total = collection.count_documents({})
    if total == 0:
        return

    taux = taux_remplissage_champs(collection)
    print("\n--- QUALITÉ DES DONNÉES : REMPLISSAGE DES CHAMPS PRINCIPAUX ---")
    for champ, nb, pct in taux:
        print(f"{champ:32} {nb:4}/{total}  {pct:5.1f}%")

    print("\n--- QUALITÉ DES DONNÉES : REMPLISSAGE DES CHAMPS IMBRIQUÉS ---")
    for chemin, nb, pct in taux_remplissage_imbriques(collection):
        print(f"{chemin:32} {nb:4}/{total}  {pct:5.1f}%")

    nb_champs = len(taux)
    for titre, meilleurs in [
        ("LES 3 ANNONCES LES PLUS COMPLÈTES", True),
        ("LES 3 ANNONCES QUASI VIDES", False),
    ]:
        print(f"\n--- {titre} (sur {nb_champs} champs) ---")
        for id_annonce, intitule, score in classement_completude(collection, meilleurs):
            print(f"{id_annonce} | {intitule} | {score}/{nb_champs} champs renseignés")


def afficher_top(titre, resultats, nb_base, unite="annonce(s)"):
    print(f"\n--- {titre} (sur {nb_base} annonces renseignées) ---")
    if not resultats:
        print("Aucune donnée.")
    for nom, nb in resultats:
        print(f"{nom} : {nb} {unite}")


def afficher_statistiques():
    db = get_db()
    collection = db["annonces"]
    total = collection.count_documents({})
    if total == 0:
        print("Aucune annonce en base.")
        return


    print(f"\n===== STATISTIQUES ({total} annonces) =====")

    print("\n--- TYPES DE CONTRAT ---")
    for nom, nb in repartition_contrats(collection):
        print(f"{nom} : {nb} annonce(s) ({nb / total * 100:.1f}%)")

    nb_alt, _, pct_alt = part_alternance(collection)
    print("\n--- ALTERNANCE ---")
    print(f"{nb_alt} annonce(s) en alternance ({pct_alt:.1f}%)")

    print("\n--- TOP 10 DES DÉPARTEMENTS ---")
    for nom, nb in top_departements(collection):
        print(f"{nom} : {nb} annonce(s)")

    res, base = top_champ(collection, "appellationlibelle")
    afficher_top("TOP 10 DES MÉTIERS", res, base)

    res, base = top_champ(collection, "entreprise.nom")
    afficher_top("TOP 10 DES ENTREPRISES", res, base)

    res, base = top_champ(collection, "experienceLibelle")
    afficher_top("TOP 10 DE L'EXPÉRIENCE EXIGÉE", res, base)

    res, base = top_champ(collection, "codeNAF")
    afficher_top("TOP 10 DES CODES NAF", res, base)

    res, base = top_tableau(collection, "competences")
    afficher_top("TOP 10 DES COMPÉTENCES", res, base, "mention(s)")

    res, base = top_tableau(collection, "langues")
    afficher_top("TOP 10 DES LANGUES", res, base, "mention(s)")

    res, base = top_champ(collection, "natureContrat")
    afficher_top("RÉPARTITION PAR NATURE DE CONTRAT", res, base)

    print("\n--- ANNONCES LIÉES AU HANDICAP ---")
    for nom, nb, pct in part_handicap(collection):
        print(f"{nom} : {nb} annonce(s) ({pct:.1f}%)")

    print("\n--- DURÉE DE TRAVAIL ---")
    for nom, nb in repartition_duree_travail(collection):
        print(f"{nom} : {nb} annonce(s) ({nb / total * 100:.1f}%)")

    nb_tt, _, pct_tt = part_teletravail(collection)
    print("\n--- TÉLÉTRAVAIL (approximation) ---")
    print(f"{nb_tt} annonce(s) mentionnent le télétravail ({pct_tt:.1f}%)")

    print("\n--- ÉVOLUTION DU NOMBRE D'ANNONCES PAR MOIS ---")
    for mois, nb in evolution_par_mois(collection):
        print(f"{mois} : {nb} annonce(s)")

    res, base = top_champ(collection, "lieuTravail.libelle")
    afficher_top("TOP 10 DES COMMUNES (libellé du lieu de travail)", res, base)

    afficher_qualite(collection)


if __name__ == "__main__":
    afficher_statistiques()