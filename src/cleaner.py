import pandas as pd
import re
import numpy as np

class CsvCleaner:
    def __init__(self, df):
        self.df = df.copy()

    # --- Pre-processing & Parsing ---

    def clean_text_fields(self):
        for col in ['GENRE', 'ONE-LINE', 'MOVIES']:
            if col in self.df.columns:
                self.df[col] = self.df[col].astype(str).str.strip()

    def clean_year(self):
        # Extract 4 digit year
        def extract_year(val):
            if pd.isna(val): return None
            match = re.search(r'(\d{4})', str(val))
            return int(match.group(1)) if match else None
        
        if 'YEAR' in self.df.columns:
            self.df['YEAR_Clean'] = self.df['YEAR'].apply(extract_year)

    def extract_type_and_status(self):
        # Detect Series vs Movie and Status based on YEAR column format like (2019– ) or (2019–2020)
        def parse_type_status(val):
            val = str(val)
            is_series = False
            status = 'Released' # Default for movies
            
            # Logic: If it has a range separator '–' or '-', it's likely a series.
            # Exception: Some movies might have it in title, but this is YEAR column.
            if '–' in val or '-' in val:
                is_series = True
                # If it ends with the separator or has no end year '2019– )', it's ongoing
                if re.search(r'(\d{4})[\s]*[–-][\s]*\)', val): 
                    status = 'Ongoing'
                else:
                    status = 'Ended'
            
            # Heuristic: If it's a Movie but marked Ongoing, force it to Series? 
            # Or trust the Year format? Let's stick to year format.
            
            return ('Series' if is_series else 'Movie', status)

        if 'YEAR' in self.df.columns:
            type_status = self.df['YEAR'].apply(parse_type_status)
            self.df['Type'] = type_status.apply(lambda x: x[0])
            self.df['Status'] = type_status.apply(lambda x: x[1])

    def clean_placeholders(self):
        # Remove "Add a Plot" and similar spam
        placeholders = ["Add a Plot", "See full summary", "See full synopsis", "Plot unknown"]
        cols_to_check = ['ONE-LINE', 'MOVIES', 'GENRE']
        
        for col in cols_to_check:
            if col in self.df.columns:
                for ph in placeholders:
                    # Replace strictly or substrings? "Add a Plot" is usually the whole string.
                    # We'll use regex to be safe
                    self.df[col] = self.df[col].apply(
                        lambda x: np.nan if isinstance(x, str) and ph.lower() in x.lower() else x
                    )

    def clean_votes(self):
        if 'VOTES' in self.df.columns:
            # Remove commas, coeff to numeric. 
            # NOTE: We keep NaN here so aggregation ignores them (100 + NaN -> 100, not 50).
            # We will fill 0 at the very end.
            self.df['VOTES'] = self.df['VOTES'].astype(str).str.replace(',', '', regex=False)
            self.df['VOTES'] = pd.to_numeric(self.df['VOTES'], errors='coerce')


    def clean_gross(self):
        if 'Gross' in self.df.columns:
            def parse_gross(val):
                if pd.isna(val) or str(val).lower() == 'nan': return np.nan
                val = str(val).replace('$', '').replace('M', '')
                try:
                    return float(val) * 1_000_000
                except:
                    return np.nan
            self.df['Gross_Clean'] = self.df['Gross'].apply(parse_gross)

    def clean_runtime(self):
        # Handle outliers: negative or super large.
        if 'RunTime' in self.df.columns:
            self.df['RunTime'] = pd.to_numeric(self.df['RunTime'], errors='coerce')
            
            # User request: remove aberrant values like 1000000 or negative
            # Let's set reasonable bounds: 0 < runtime < 500 (most movies/shows)
            mask_outliers = (self.df['RunTime'] <= 0) | (self.df['RunTime'] > 600) 
            self.df.loc[mask_outliers, 'RunTime'] = np.nan

    def extract_stars_director(self):
        if 'STARS' in self.df.columns:
            def parse_credits(val):
                director = None
                stars = []
                if pd.isna(val): return director, ", ".join(stars)
                val = str(val)
                d_match = re.search(r'Director(?:s)?:\s*(.*?)(?:\s*\|\s*|$)', val, re.DOTALL)
                if d_match:
                    director = d_match.group(1).strip().replace('\n', '')
                s_match = re.search(r'Star(?:s)?:\s*(.*?)$', val, re.DOTALL)
                if s_match:
                    stars_str = s_match.group(1).strip().replace('\n', '')
                    stars_str = re.sub(r'\s+', ' ', stars_str)
                    stars = [s.strip() for s in stars_str.split(',')]
                return director, ", ".join(stars)

            credits = self.df['STARS'].apply(parse_credits)
            self.df['Director_Clean'] = credits.apply(lambda x: x[0])
            self.df['Stars_Clean'] = credits.apply(lambda x: x[1])

    def clean_rating(self):
        if 'RATING' in self.df.columns:
            self.df['RATING'] = pd.to_numeric(self.df['RATING'], errors='coerce')
            # Remove invalid ratings (0-10 scale usually)
            self.df.loc[(self.df['RATING'] < 0) | (self.df['RATING'] > 10), 'RATING'] = np.nan

    # --- Aggregation Logic ---

    def aggregate_duplicates(self):
        """
        Groups by MOVIES and YEAR_Clean (if available) or just Title.
        Averages numeric columns: RATING, VOTES, RunTime, Gross_Clean.
        Keeps first non-null for text columns.
        """
        
        # Ensure we have the clean columns first
        self.clean_text_fields()
        self.clean_placeholders() # NEW: Remove garbage text before aggregation can rely on it
        self.clean_year()
        self.clean_votes() # Fills 0, so average works
        self.clean_gross() # Keeps NaN
        self.clean_runtime() # Keeps NaN
        self.clean_rating()
        self.extract_type_and_status()
        self.extract_stars_director()

        # Grouping keys
        group_keys = ['MOVIES', 'YEAR_Clean'] 
        # Note: YEAR_Clean might be NaN, so we fill it with a placeholder for grouping to avoid dropping
        self.df['YEAR_Clean_Group'] = self.df['YEAR_Clean'].fillna(-1)
        
        # Define aggregation dictionary
        agg_dict = {
            'RATING': 'mean',
            'VOTES': 'mean', # User wanted average of votes? Or sum? User said "réaliser une moyenne des champs numériques... votes". Logic: multiple entries same movie = same movie sampled/scraped multiple times, so average is better estimation of true value then sum found.
            'RunTime': 'mean',
            'Gross_Clean': 'mean',
            'GENRE': 'first',
            'ONE-LINE': 'first',
            'Director_Clean': 'first',
            'Stars_Clean': 'first',
            'Type': 'first',
            'Status': 'first'
        }
        
        # Filter agg_dict to only include columns that exist
        agg_dict = {k: v for k, v in agg_dict.items() if k in self.df.columns}

        # Perform aggregation
        # We group by Title and Year. 
        df_agg = self.df.groupby(['MOVIES', 'YEAR_Clean_Group'], as_index=False).agg(agg_dict)
        
        # Round numeric columns as requested ("arrondir la valeur")
        round_cols = ['RATING', 'VOTES', 'RunTime', 'Gross_Clean']
        for col in round_cols:
            if col in df_agg.columns:
                df_agg[col] = df_agg[col].round(2) # Keeping 2 decimals seems safe, or int for votes. User said "arrondir... soit inférieure soit excès". Standard round is closest.

        # Restore cleaned year (remove placeholder if we want strictly cleaned data)
        # But actually df_agg has YEAR_Clean_Group. We should treat -1 back to NaN if needed, or just ignore.
        # Let's clean up the group column
        if 'YEAR_Clean' in self.df.columns:
             # We can't easily map back perfectly if we grouped by modified col, but we can just drop the group buffer
             pass

        self.df = df_agg
        
        # FINAL STEP: Fix names and placeholders
        # 1. Rename YEAR_Clean_Group -> Year
        if 'YEAR_Clean_Group' in self.df.columns:
            self.df.rename(columns={'YEAR_Clean_Group': 'Year'}, inplace=True)
            # 2. Replace -1 (placeholder) with NaN
            self.df['Year'] = self.df['Year'].replace(-1, np.nan)

        # 3. Fill missing votes with 0, as strictly requested for the final output.
        if 'VOTES' in self.df.columns:
            self.df['VOTES'] = self.df['VOTES'].fillna(0)
            
        return len(self.df)

    def run_user_specific_cleaning(self):
        # This replaces the old run_advanced_cleaning flow
        # It calls aggregate_duplicates which calls the parsing steps internally
        initial_count = len(self.df)
        self.aggregate_duplicates()
        final_count = len(self.df)
        return initial_count - final_count

    def save_data(self, filepath):
        # User requested explicit "NaN" in the text file instead of empty strings
        self.df.to_csv(filepath, index=False, na_rep='NaN')
        return filepath
