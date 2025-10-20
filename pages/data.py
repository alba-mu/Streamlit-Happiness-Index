import streamlit as st
import polars as pl
from urllib.parse import urljoin
import patito as pt

st.header("Index de felicitat")


# URL base dels fitxers CSV
base_url = "https://gitlab.com/xtec/python/polars-data/-/raw/main/"


# Definició funcions per carregar els fitxers csv en datasets de polars
@st.cache_data
def load_education_and_income():
    education_income = pl.read_csv(urljoin(base_url, "world-education-and-income.csv"))
    return education_income

@st.cache_data
def load_happiness():
    happiness = pl.read_csv(urljoin(base_url, "world-happiness.csv"))
    return happiness

@st.cache_data
def load_population():
    population = pl.read_csv(urljoin(base_url, "world-population.csv"))
    return population


# Carregar datasets
education = load_education_and_income()
happiness = load_happiness()
population = load_population()


# Rename de les columnes amb informació sobre el país per poder usar-les com a id pel join
happiness = happiness.rename({"Country name": "Country"})
education = education.rename({"Country": "Country"})
population = population.rename({"Country/Territory": "Country"})

# INNER join per quedar-nos només amb països que surten al dataset de felicitat:
merged = (
    happiness
    .join(education, on="Country", how="inner")
    .join(population, on="Country", how="inner")
)



# Esquema de validació per tres columnes del dataset
class Country (pt.Model):
    Country: str = pt.Field(description="Nom del país", unique=True, min_length=1)
    Ladder_score: float = pt.Field(description="Índex de felicitat", ge=0, le=10)
    Education_Index: float = pt.Field(description="Índex d'educació", ge=0, le=1)

# Renombrar columnes per poder validar amb el model
merged = merged.rename({
    "Ladder score": "Ladder_score",
    "Education Index": "Education_Index"
})

# Validació del DataFrame Polars (merged)
if Country.validate(merged, allow_superfluous_columns=True).is_empty():
    st.write("not valid dataset")

else:
    # --- Mostrar dataset merged i validat---
    st.header("Raw merged dataset")
    st.write(
        "Conjunt de dades resultant de la unió (join) dels tres datasets originals, que inclou totes les columnes de cadascun i utilitza el nom del país com a identificador comú.")
    if st.checkbox("Show raw data"):
        st.write(merged)
