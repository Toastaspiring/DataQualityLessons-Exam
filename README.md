# Projet Data Quality

Ce projet permet de nettoyer le dataset de films dataset_movies.csv.
On utilise Python et Pandas pour le traitement.

## Installation et Lancement

Installer les dependances:
pip install -r requirements.txt

Lancer le script de nettoyage:
python main.py "dataset_movies.csv" --action clean --output "cleaned_dataset_movies.csv"

## Details techniques du nettoyage

On a applique plusieurs methodes pour nettoyer les donnees:

1. Gestion des doublons
On ne fait pas juste un drop_duplicates. On agrege les lignes qui ont le meme titre et annee.
- Pour les notes (Votes, Rating) et durees : on fait la moyenne des valeurs disponibles (on ignore les Nan).
- Pour le texte : on prend la premiere valeur qui n'est pas vide.

2. Distinctions Film vs Serie
On regarde la colonne Year. Si il y a un trait d'union (ex: 2019- ), c'est une serie. Si l'intervalle est ouvert, le statut est Ongoing. Sinon c'est un Film.

3. Nettoyage des colonnes
- Votes : on enleve les virgules et on convertit en nombre.
- Gross : on enleve les $ et M, on garde la valeur en Millions de dollars.
- Runtime : on supprime les valeurs absurdes (negatives ou superieures a 50 000 minutes).
- Textes : on a utilise des regex pour virer les placeholders du type "Add a plot" ou "-1".

4. Formatage
- On a separe la colonne Stars en deux : Director et Actors.
- Le fichier de sortie contient des NaN explicites pour les valeurs manquantes.

Le code est dans src/cleaner.py si besoin de verifier la logique.
