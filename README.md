# Projet Data Quality

Ce projet permet de nettoyer le dataset de films dataset_movies.csv.
On utilise Python et Pandas pour le traitement.

## Installation et Lancement

Installer les dépendances:
pip install -r requirements.txt

Lancer le script de nettoyage:
python main.py "dataset_movies.csv" --action clean --output "cleaned_dataset_movies.csv"

## Détails techniques du nettoyage

On a appliqué plusieurs méthodes pour nettoyer les données:

1. Gestion des doublons
On ne fait pas juste un drop_duplicates. On agrège les lignes qui ont le même titre et année.
- Pour les notes (Votes, Rating) et durées : on fait la moyenne des valeurs disponibles (on ignore les Nan).
- Pour le texte : on prend la première valeur qui n'est pas vide.

```python
        agg_dict = {
            'RATING': 'mean',
            'VOTES': 'mean',
            'RunTime': 'mean',
            'Gross_Clean': 'mean',
            'GENRE': 'first',
            'ONE-LINE': 'first',
            'Director_Clean': 'first',
            'Stars_Clean': 'first',
            'Type': 'first',
            'Status': 'first'
        }
        
        agg_dict = {k: v for k, v in agg_dict.items() if k in self.df.columns}

        df_agg = self.df.groupby(['MOVIES', 'YEAR_Clean_Group'], as_index=False).agg(agg_dict)
```

2. Distinctions Film vs Série
On regarde la colonne Year. Si il y a un trait d'union (ex: 2019- ), c'est une série. Si l'intervalle est ouvert, le statut est Ongoing. Sinon c'est un Film.

```python
            if '–' in val or '-' in val:
                is_series = True
                if re.search(r'(\d{4})[\s]*[–-][\s]*\)', val): 
                    status = 'Ongoing'
                else:
                    status = 'Ended'
            
            return ('Series' if is_series else 'Movie', status)
```

3. Nettoyage des colonnes
- Votes : on enlève les virgules et on convertit en nombre.
- Gross : on enlève les $ et M, on garde la valeur en Millions de dollars.
- Runtime : on supprime les valeurs absurdes (négatives ou supérieures à 50 000 minutes).
- Textes : on a utilisé des regex pour virer les placeholders du type "Add a plot" ou "-1".

Votes et Gross en Millions:
```python
            self.df['VOTES'] = self.df['VOTES'].astype(str).str.replace(',', '', regex=False)
            self.df['VOTES'] = pd.to_numeric(self.df['VOTES'], errors='coerce')

            def parse_gross(val):
                if pd.isna(val) or str(val).lower() == 'nan': return np.nan
                val = str(val).replace('$', '').replace('M', '')
                try:
                    return float(val) 
                except:
                    return np.nan
```

Outliers Runtime (50k min):
```python
            self.df['RunTime'] = pd.to_numeric(self.df['RunTime'], errors='coerce')
            
            mask_outliers = (self.df['RunTime'] <= 0) | (self.df['RunTime'] > 50000) 
            self.df.loc[mask_outliers, 'RunTime'] = np.nan
```

4. Formatage
On a séparé la colonne Stars en deux : Director et Actors.
Le fichier de sortie contient des NaN explicites.

Le code est dans src/cleaner.py si besoin de vérifier la logique.
