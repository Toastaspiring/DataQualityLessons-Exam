# TP Data Quality

Voici notre rendu pour le projet de nettoyage de données.

## Installation
Il faut installer les trucs dans requirements :
`pip install -r requirements.txt`

## Lancement
Pour lancer le script il faut faire :
`python main.py "dataset_movies.csv" --action clean --output "cleaned_dataset_movies.csv"`

## Ce qu'on a fait
* On a enlevé les doublons (en faisant la moyenne des notes).
* On a séparé les acteurs et les réalisateurs.
* On a nettoyé les dates et mis les bonnes colonnes.
* On a géré les outliers (genre les durées bizarres).
* Les trucs vides sont marqués NaN.

Voilà le fichier sort propre normalement.
