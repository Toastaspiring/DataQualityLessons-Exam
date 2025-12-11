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

## 🧹 Stratégie de Nettoyage & Logique Détaillée

Pour garantir une transparence totale sur la qualité des données, voici les règles techniques appliquées à chaque champ :

### 1. Classification (Film vs Série) & Statut
La distinction se fait par l'analyse syntaxique de la colonne brute `YEAR` :
*   **Film (`Movie`)** : Si la date est une année unique ex: `(2020)`.
*   **Série (`Series`)** : Si la date contient un intervalle (trait d'union) ex: `(2019-2020)` ou `(2019- )`.
*   **Statut (`Status`)** :
    *   **Ongoing (En cours)** : Si l'intervalle est ouvert, détecté par le pattern Regex `(\d{4})[\s]*[–-][\s]*\)`. Ex: `(2019- )`.
    *   **Ended (Terminé)** : Si l'intervalle est fermé. Ex: `(2019-2021)`.
    *   **Released (Sorti)** : Statut par défaut pour les films.

### 2. Nettoyage et Typage (Parsing)
*   **`Year`** : Extraction des 4 premiers chiffres via Regex `(\d{4})`. Les valeurs fantaisistes (chiffres romains, texte) sont ignorées.
*   **`VOTES`** :
    1.  Suppression des virgules (`1,234` -> `1234`).
    2.  Conversion en numérique (Float).
    3.  **Traitement des vides** : Les valeurs manquantes sont remplies par `0` uniquement à la toute fin du processus (Option C), pour ne pas fausser les moyennes intermédiaires.
*   **`Gross`** :
    1.  Suppression des symboles `$` et `M`.
    2.  Conversion en float (Unités : **Millions de dollars**).
    3.  Renommage de la colonne en `Gross ($M)`.
    4.  Les erreurs de conversion sont transformées en `NaN`.

### 3. Gestion des Outliers (Validité)
*   **`RunTime`** : Les durées sont validées.
    *   Si `t <= 0` (ex: négatifs) -> Suppression (`NaN`).
    *   Si `t > 50,000` min (ex: 1 million de minutes) -> Suppression (`NaN`). On accepte les séries longues.
*   **`ONE-LINE` (Synopsis)** : Détection et suppression des descriptions génériques via Regex (ex: *"Add a Plot"*, *"See full summary"*). Ces valeurs sont remplacées par `NaN`.

### 4. Agrégation des Doublons (Smart Deduplication)
Lors de la fusion des entrées multiples pour un même film (Title + Year) :
*   **Score/Durée** : Moyenne arithmétique des valeurs **existantes** (on ignore les `NaN`).
    *   *Exemple : Film A (Note: 8) + Film A (Note: NaN) = Moyenne 8 (et non 4).*
*   **Textes** : Conservation de la première valeur non-nulle trouvée.

### 5. Extraction de Métadonnées (Feature Engineering)
*   **Categorisation** : `Type` (Movie/Series) et `Status` (Released/Ongoing/Ended) inférés.
*   **Découplage** : Séparation propre des Réalisateurs (`Director`) et du Casting (`Actors`).

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
