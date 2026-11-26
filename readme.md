# Projet NoSQL — France Travail (Groupe 03 — Code ROME M1802)

Application CLI développée en Python permettant d'importer, interroger, consulter, exporter et analyser statistiquement les offres d'emploi France Travail correspondant au code ROME **M1802** (_Expert(e) systèmes et réseaux informatiques_ — 548 annonces sur les 2 902 du jeu de données initial du 12/11/2026).

---

## 1. Architecture du projet

- **Stack technique :** Python 3, MongoDB (conteneurisé via Docker Compose), bibliothèque `pymongo`.
- **Organisation du dépôt :**
  - `docker-compose.yml` : déploiement du conteneur MongoDB (port `27017`).
  - `requirements.txt` : dépendances Python du projet.
  - `src/db.py` : gestion de la connexion à la base MongoDB (`france_travail`).
  - `scripts/import.py` : filtrage du fichier JSON brut sur `romeCode == "M1802"`, réinitialisation propre de la collection `annonces` et création des index (`id` unique, `typeContrat`, `lieuTravail.libelle`).
  - `main.py` : point d'entrée de l'interface en ligne de commande (menu principal).
  - `recherche.py` : recherche multicritère d'annonces.
  - `annonces.py` : affichage détaillé d'une annonce à partir de son identifiant métier (`id`).
  - `export.py` : export au format JSON d'une annonce ou d'une liste de résultats dans `exports/`.
  - `statistiques.py` : calcul et affichage des statistiques métier et des indicateurs de qualité des données via des pipelines d'agrégation MongoDB.

---

## 2. Procédure de reproduction

### Prérequis

- Docker Desktop (ou Docker Engine + Docker Compose)
- Python 3.10+

### Installation et lancement

1. **Démarrer MongoDB avec Docker :**

   ```bash
   docker compose up -d
   ```

2. **Installer les dépendances Python :**Bash

   ```
   pip install -r requirements.txt
   ```

3. **Préparer les données :**
   - Télécharger l'archive depuis `https://data.atontour.info/france-travail.zip`.
   - Extraire le fichier `france-travail.json` dans le dossier `data/` à la racine du projet (`data/france-travail.json`).
4. **Importer les 548 annonces M1802 dans MongoDB :**Bash

   ```
   python scripts/import.py
   ```

   _(Script idempotent : vide la collection `annonces` avant réinsertion pour éviter tout doublon)._

5. **Lancer l'application CLI :**Bash

   ```
   python main.py
   ```

## 3. Choix techniques et limites (Statistiques & Qualité des données)

Les indicateurs de `statistiques.py` s'appuient sur des pipelines d'agrégation MongoDB (`$group`, `$unwind`, `$project`, `$objectToArray`, `$substrCP`). En raison de la structure hétérogène des annonces France Travail, plusieurs conventions ont été retenues :

- **Gestion des champs manquants ou vides :** Les valeurs `None`, `""`, `[]` et `{}` sont explicitement exclues des taux de remplissage et des classements (`Top 10`), et remplacées par `"Non renseigné"` lorsque pertinent (ex. type de contrat).
- **Top des départements et des communes :**
  - Le département est extrait en découpant le préfixe avant `" - "` dans `lieuTravail.libelle`. Lorsque la valeur vaut `"France"`, elle est regroupée sous `"Télétravail (100 %)"`.
  - Le top des communes affiche le libellé complet `lieuTravail.libelle` (ex. `"75 - PARIS 01"`) plutôt que le code INSEE (`lieuTravail.commune`), afin de garantir une lecture immédiate en console.
- **Durée de travail :** Catégorisée à partir de `dureeTravailLibelle` via expressions régulières (`^[0-9]+H` pour le temps plein avec heures précisées, `^Temps partiel` pour le temps partiel, puis séparation des libellés sans durée chiffrée et des champs non renseignés).
- **Télétravail (estimation) :** Aucun champ booléen dédié n'existant dans le schéma, le télétravail est estimé par recherche insensible à la casse (`t.l.travail`) dans la description, le lieu et le contexte de travail, tout en excluant les mentions négatives explicites (_"pas de télétravail"_, _"sans télétravail"_, _"aucun télétravail"_).
- **Qualité des données :** Calculée dynamiquement via `$objectToArray` sur `$$ROOT` pour mesurer le taux de remplissage des champs de premier niveau, complétée par un suivi ciblé des sous-champs imbriqués critiques (`lieuTravail.*`, `entreprise.*`, `salaire.*`, `contact.*`, `agence.courriel`) et l'identification des 3 annonces les plus complètes et les 3 plus incomplètes.
