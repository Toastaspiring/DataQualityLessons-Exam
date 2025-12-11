# Projet de Profilage et Nettoyage Avancé de Données Cinématographiques (Pandas V2)

Ce projet implémente un pipeline de nettoyage de données robuste pour transformer un dataset brut (`dataset_movies.csv`) en un actif de données de haute qualité.

## 📊 Rapport de Qualité des Données (Deep Profile)

L'analyse approfondie a permis de qualifier précisemment le dataset.

### 1. Analyse Structurale et Sémantique
*   **Pollution Textuelle** : La colonne `ONE-LINE` (Synopsis) contenait des textes par défaut (*"Add a Plot"*, *"Plot unknown"*). Ces quasi-manquants ont été détectés et traités.
*   **Intégrité Temporelle** : ✅ Aucune année future (>2026) n'a été détectée. Le dataset est temporellement cohérent.
*   **Consistance des Genres** : ✅ Pas de redondance sémantique (ex: "Action, Action") détectée dans les tags de genre.
*   **Conflits Logiques** : Quelques durées aberrantes (0 min ou > 1000 min) ont été isolées.

### 2. Problématique des Doublons
*   **Volume** : ~35% de lignes identifiées comme doublons techniques.
*   **Cause** : Scrapping multiple du même objet avec des attributs fragmentaires.

---

## 🧹 Stratégie de Nettoyage "Qualité Maximale"

Pour atteindre un niveau de qualité supérieur, nous avons appliqué les transformations suivantes dans `src/cleaner.py` :

### 1. Nettoyage Sémantique (V2)
*   **Suppression des Placeholders** : Identification et suppression automatique des chaînes parasites ("Add a Plot", etc) remplacées par `NaN`.
*   **Typage Strict** : Conversion des `VOTES` et `Gross` en numérique.
*   **Validité** : Suppression des `RunTime` aberrants (négatifs ou extrêmes).

### 2. Agrégation Intelligente (Smart Deduplication)
*   **Fusion Intelligente** : Les doublons sont fusionnés (Titre + Année).
*   **Conservation de l'Information** :
    *   **Scores/Durées** : On calcule la moyenne des valeurs disponibles (**en ignorant les champs vides**, pour ne pas diluer la moyenne).
    *   **Votes** : Moyennés sans compter les manquants, avec replissage à 0 uniquement en dernier recours.
*   **Gain** : Passage de ~10 000 lignes brutes à ~6 500 entrées consolidées.

### 3. Extraction de Métadonnées (Feature Engineering)
*   **Categorisation** : `Type` (Movie/Series) et `Status` (Released/Ongoing/Ended) inférés.
*   **Découplage** : Séparation propre des Réalisateurs (`Director_Clean`) et du Casting (`Stars_Clean`).

---

## 🚀 Utilisation

### Installation
```bash
pip install -r requirements.txt
```

### Exécution (Pipeline Complet)
Ce script lance le profilage profond ET le nettoyage en une seule passe :

```bash
python main.py "dataset_movies.csv" --action clean --output "cleaned_dataset_movies.csv"
```
Le profil complet s'affichera dans la console, suivi de la génération du fichier nettoyé.
