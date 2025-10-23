import polars as pl

country_name_map = {
    # --- Variants entre happiness / population ---
    "Czech Republic": "Czechia",
    "Republic of the Congo": "Congo (Brazzaville)",
    "DR Congo": "Congo (Kinshasa)",
    "Hong Kong": "Hong Kong S.A.R. of China",
    "Turkey": "Turkiye",
    "Palestine": "State of Palestine",
    "Taiwan": "Taiwan Province of China",

    # --- Variants entre education i els altres ---
    "Cabo Verde": "Cape Verde",
    "Côte d'Ivoire": "Ivory Coast",
    "Lao People\\'s Dem. Rep": "Laos",
    "United States of America": "United States",
    "Brunei Darussalam": "Brunei",
    "Dem. People\\'s Rep. Korea": "North Korea",
    "Dem. Rep. of the Congo": "Congo (Kinshasa)",
    "China Hong Kong SAR": "Hong Kong S.A.R. of China",
    "Republic of Korea": "South Korea",
    "Syrian Arab Republic": "Syria",
    "The former Yugoslav": "North Macedonia",
    "Iran (Islamic Republic of)": "Iran",
    "Bolivia (Plurin. State of)": "Bolivia",
    "Russian Federation": "Russia",
    "Venezuela (Boliv. Rep. of)": "Venezuela",
    "Republic of Moldova": "Moldova",
    "Macedonia": "North Macedonia",
    "Cabo Verde": "Cape Verde",

    # --- Variants menors o d’accentuació ---
    "Viet Nam": "Vietnam",
    "United Rep. of Tanzania": "Tanzania",
}

# ---------- Funció auxiliar per normalitzar un dataframe (manté la resta de columnes) ----------
def normalize_country_column(df: pl.DataFrame, col: str = "Country") -> pl.DataFrame:
    """
    Normalitza la columna `col` d'un DataFrame polars fent servir el diccionari country_name_map.
    Si un nom no està al diccionari, es conserva tal qual.
    """
    return df.with_columns(
        pl.col(col)
        .map_elements(lambda x: country_name_map.get(x, x), return_dtype=pl.Utf8)
        .alias(col)
    )