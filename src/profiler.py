import pandas as pd
import io
import os

class CsvProfiler:
    def __init__(self, filepath):
        self.filepath = filepath
        self.df = None
        try:
            self.df = pd.read_csv(filepath)
        except FileNotFoundError:
            print(f"Error: File not found at {filepath}")
        except Exception as e:
            print(f"Error loading CSV: {e}")

    def get_summary(self):
        if self.df is None: return None
        buffer = io.StringIO()
        self.df.info(buf=buffer)
        return {
            "rows": self.df.shape[0],
            "cols": self.df.shape[1],
            "info": buffer.getvalue(),
            "description": self.df.describe(include='all').to_string()
        }

    def get_missing_stats(self):
        if self.df is None: return None
        missing = self.df.isnull().sum()
        missing_percent = (missing / len(self.df)) * 100
        return pd.concat([missing, missing_percent], axis=1, keys=['Total Missing', 'Percent Missing'])

    def get_duplicates(self):
        if self.df is None: return 0
        return self.df.duplicated().sum()

    def check_text_quality(self):
        """Checks for common placeholder text in string columns."""
        if self.df is None: return {}
        
        text_issues = {}
        placeholders = ["Add a Plot", "See full summary", "See full synopsis", "Plot unknown"]
        
        for col in self.df.select_dtypes(include=['object']):
            # frequency of placeholders
            for ph in placeholders:
                count = self.df[col].astype(str).apply(lambda x: ph.lower() in x.lower()).sum()
                if count > 0:
                    text_issues[f"{col}_contains_{ph}"] = int(count)
        return text_issues

    def check_logical_consistency(self):
        """Checks logical rules (e.g. Runtime vs Type)."""
        if self.df is None: return {}
        
        issues = {}
        
        # Check 1: Movies with 0 runtime (if numeric)
        if 'RunTime' in self.df.columns and 'Type' in self.df.columns:
            # Assuming RunTime is cleaner now or we use raw 
            # We need valid numerics
            temp_df = self.df.copy()
            temp_df['RunTime'] = pd.to_numeric(temp_df['RunTime'], errors='coerce')
            
            zero_runtime_movies = temp_df[(temp_df['Type'] == 'Movie') & (temp_df['RunTime'] <= 1)].shape[0]
            if zero_runtime_movies > 0:
                issues['Movies_with_Zero_Runtime'] = int(zero_runtime_movies)

        # Check 2: Ongoing Movies? (Should be Series)
        if 'Status' in self.df.columns and 'Type' in self.df.columns:
             ongoing_movies = self.df[(self.df['Type'] == 'Movie') & (self.df['Status'] == 'Ongoing')].shape[0]
             if ongoing_movies > 0:
                 issues['Movies_marked_Ongoing'] = int(ongoing_movies)

        return issues

    def check_content_validity(self):
        """Checks for content specific validity (Years in future, Redundant Genres)."""
        if self.df is None: return {}
        issues = {}
        
        # Check Year Validity (e.g. > 2030)
        # Need to parse year first lightly for this check or use raw if clean
        # If we run this on raw data, we might need regex. 
        # Let's try to detect 4-digit years > 2026 in string
        if 'YEAR' in self.df.columns:
            # Extract basic year
            years = self.df['YEAR'].astype(str).str.extract(r'(\d{4})').astype(float)
            future_content = years[years[0] > 2026].shape[0]
            if future_content > 0:
                issues['Content_with_Future_Years(>2026)'] = int(future_content)

        # Check Genre Redundancy (e.g. "Action, Action")
        if 'GENRE' in self.df.columns:
            def has_redundant_genre(val):
                if pd.isna(val): return False
                genres = [g.strip() for g in str(val).split(',')]
                return len(genres) != len(set(genres))
            
            redundant_genres = self.df['GENRE'].apply(has_redundant_genre).sum()
            if redundant_genres > 0:
                issues['Rows_with_Redundant_Genres'] = int(redundant_genres)
                
        return issues

    def generate_report(self):
        if self.df is None:
            return "No data loaded."
        
        summary = self.get_summary()
        missing_stats = self.get_missing_stats()
        duplicates = self.get_duplicates()
        text_issues = self.check_text_quality()
        logic_issues = self.check_logical_consistency()
        content_issues = self.check_content_validity()
        
        report = []
        report.append("=== CSV Profile Report ===")
        report.append(f"File: {os.path.basename(self.filepath)}") # Changed self.file_path to self.filepath
        report.append(f"Rows: {summary['rows']}, Columns: {summary['cols']}")
        report.append(f"Duplicates: {duplicates}")
        report.append("\n--- Missing Values ---")
        report.append(missing_stats.to_string())
        report.append("\n--- Text Quality Issues (Placeholders found) ---")
        report.append(pd.Series(text_issues).to_string() if text_issues else "None detected")
        report.append("\n--- Logical Consistency Issues ---")
        report.append(pd.Series(logic_issues).to_string() if logic_issues else "None detected")
        report.append("\n--- Content Validity Issues ---")
        report.append(pd.Series(content_issues).to_string() if content_issues else "None detected")
        report.append("\n--- Column Info ---")
        report.append(summary['info'])
        report.append("\n--- Descriptive Statistics ---")
        report.append(summary['description'])
        
        return "\n".join(report)
