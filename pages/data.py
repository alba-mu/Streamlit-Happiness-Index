import streamlit as st
import polars as pl
from urllib.parse import urljoin
import patito as pt
import altair as alt

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
merged_happiness = (
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
merged_happiness = merged_happiness.rename({
    "Ladder score": "Ladder_score",
    "Education Index": "Education_Index"
})

# Validació del DataFrame Polars (merged)
if Country.validate(merged_happiness, allow_superfluous_columns=True).is_empty():
    st.write("Dataset not valid")

else:
    # --- Mostrar dataset merged i validat---
    st.header("Raw merged dataset")
    st.write(
        "Conjunt de dades resultant de la unió (join) dels tres datasets originals, que inclou totes les columnes de cadascun i utilitza el nom del país com a identificador comú.")
    if st.checkbox("Show raw data"):
        st.dataframe(merged_happiness)

    # -------------- PAISOS ORDENATS PER ÍNDEX DE FELICITAT ---------------
    # Ordenar el DataFrame de major a menor segons Ladder_score
    sorted_df = merged_happiness.sort("Ladder_score", descending=True)

    # Seleccionar només les columnes que volem mostrar
    columns = ["Country", "Ladder_score", "Education_Index", "Income"]
    sorted_df = sorted_df.select(columns)

    # Mostrar el resultat a Streamlit
    st.header("Països ordenats per índex de felicitat")
    st.write("Es mostra el nom del país, l’índex de felicitat, l’índex educatiu i el nivell d’ingressos.")
    st.dataframe(sorted_df)

    # -------------- PAISOS AMB POBLACIÓ 2022 DESCONEGUDA ---------------
    # LEFT join per obtenir tota la informació sobre les poblacions dels paisos:
    merged_population = (
        population
        .join(education, on="Country", how="left")
        .join(happiness, on="Country", how="left")
    )

    # Filtrar països amb població del 2022 desconeguda
    missing_population = merged_population.filter(pl.col("2022 Population").is_null())

    # Seleccionar les columnes d'interès
    columns = ["Country", "2022 Population"]
    missing_population = missing_population.select(columns)

    # Mostrar el resultat a Streamlit
    st.header("Països sense població 2022")
    st.write("Nombre de paisos amb informació desconeguda sobre la població del 2022")
    st.write(merged_population.select(pl.col("2022 Population").null_count()))
    st.write("Llistat de països pels quals no es disposa de dades de població del 2022.")
    st.dataframe(missing_population)

    # -------------- GRÀFIC POBLACIÓ vs ÍNDEX DE FELICITAT ---------------
    # Filtrar només països amb dades de població i felicitat
    plot_df = merged_happiness.filter(
        (pl.col("2022 Population").is_not_null()) &
        (pl.col("Ladder_score").is_not_null())
    )

    # Seleccionar les columnes clau
    plot_df = plot_df.select(["Country", "2022 Population", "Ladder_score"])

    # Crear gràfic de punts
    scatter = alt.Chart(plot_df).mark_circle(size=60).encode(
        x=alt.X("2022 Population", title="Població 2022", scale=alt.Scale(type="log")),
        y=alt.Y("Ladder_score", title="Índex de felicitat"),
        tooltip=["Country", "2022 Population", "Ladder_score"]
    ).properties(
        title="Relació entre població i índex de felicitat",
        width=700,
        height=400
    ).interactive()

    # Mostrem el gràfic a Streamlit
    st.header("Gràfic de punts Població vs Índex de felicitat")
    st.write("Aquesta visualització mostra la relació entre la població d’un país (eix X) i el seu índex de felicitat (eix Y), permetent observar com varia la felicitat en funció de la mida de la població.")
    st.altair_chart(scatter)



