import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.db import get_db

with open("data/france-travail.json", encoding="utf-8") as f:
    annonces = json.load(f)

m1802 = [a for a in annonces if a.get("romeCode") == "M1802"]

print("Total :", len(annonces))
print("M1802 :", len(m1802))

db = get_db()
collection = db["annonces"]

collection.delete_many({})          
collection.insert_many(m1802)       
print("Dans MongoDB :", collection.count_documents({}))   

collection.create_index("id", unique=True)
collection.create_index("typeContrat")
collection.create_index("lieuTravail.libelle")