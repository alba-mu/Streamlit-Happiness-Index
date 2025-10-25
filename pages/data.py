import streamlit as st
import polars as pl
from urllib.parse import urljoin
import altair as alt
from country_normalization import normalize_country_column
from models.Country import Country

st.set_page_config(layout="wide")

st.title("ANÀLISI DE L'ÍNDEX DE FELICITAT DELS PAÏSOS DEL MÓN")


# URL base dels fitxers CSV
base_url = "https://gitlab.com/xtec/python/polars-data/-/raw/main/"


# Definició funcions per carregar els fitxers csv en datasets de polars
@st.cache_data
def load_education_and_income():
    return pl.read_csv(urljoin(base_url, "world-education-and-income.csv"))
     
@st.cache_data
def load_happiness():
    return pl.read_csv(urljoin(base_url, "world-happiness.csv"))
     
@st.cache_data
def load_population():
    return pl.read_csv(urljoin(base_url, "world-population.csv"))
     

# ------------------- CÀRREGA DE DATASETS -----------------------------
education = load_education_and_income()
happiness = load_happiness()
population = load_population()


# --------------------------- JOIN -------------------------------------
# Rename de les columnes amb informació sobre el país per poder usar-les com a id pel join
happiness = happiness.rename({"Country name": "Country"})
education = education.rename({"Country": "Country"})
population = population.rename({"Country/Territory": "Country"})

# Normalització de la columna 'Country'
happiness = normalize_country_column(happiness, col="Country")   # si ja està bé no passa res
population = normalize_country_column(population, col="Country")
education = normalize_country_column(education, col="Country")

# LEFT join per quedar-nos amb tots els països que surten al dataset de felicitat:
merged_happiness = (
    happiness
    .join(population, on="Country", how="left")
    .join(education, on="Country", how="left")

)

# -------------------------- VALIDACIÓ ------------------------------
# Renombrar columnes per poder validar amb el model
merged_happiness = merged_happiness.rename({
    "Country": "Country",
    "Regional indicator": "Regional_indicator",
    "Ladder score": "Ladder_score",
    "upperwhisker": "upperwhisker",
    "lowerwhisker": "lowerwhisker",
    "Log GDP per capita": "Log_GDP_per_capita",
    "Social support": "Social_support",
    "Healthy life expectancy": "Healthy_life_expectancy",
    "Freedom to make life choices": "Freedom_to_make_life_choices",
    "Generosity": "Generosity",
    "Perceptions of corruption": "Perceptions_of_corruption",
    "Dystopia + residual": "Dystopia_residual",
    "Rank": "Rank",
    "CCA3": "CCA3",
    "Capital": "Capital",
    "Continent": "Continent",
    "2022 Population": "Population_2022",
    "2020 Population": "Population_2020",
    "2015 Population": "Population_2015",
    "2010 Population": "Population_2010",
    "2000 Population": "Population_2000",
    "1990 Population": "Population_1990",
    "1980 Population": "Population_1980",
    "1970 Population": "Population_1970",
    "Area (km²)": "Area_km2",
    "Density (per km²)": "Density_per_km2",
    "Growth Rate": "Growth_Rate",
    "World Population Percentage": "World_Population_Percentage",
    "Education Index": "Education_Index",
    "Education Level": "Education_Level",
    "Income": "Income"
})

# Omplir valors nuls de Education_Index
merged_happiness = merged_happiness.with_columns(
    pl.col("Education_Index").fill_null(0)
)

# Eliminar duplicats segons Country
merged_happiness = merged_happiness.unique(subset="Country")

# Validació del DataFrame Polars (merged)
validation_result = Country.validate(
    merged_happiness,
    allow_superfluous_columns=True,
    allow_missing_columns=True
)

# Validació del DataFrame Polars (merged)
if validation_result.is_empty():
    st.write("Dataset not valid")

else:
    # --- Mostrar dataset merged i validat---
    st.header("Raw merged dataset")
    st.write(
        "Conjunt de dades resultant de la unió (join) dels tres datasets originals, que inclou totes les columnes de cadascun i utilitza el nom del país com a identificador comú.")
    st.markdown("""
        ### Procés de normalització de noms de països

        En els tres datasets utilitzats (`world-happiness`, `world-population` i `world-education`) s'ha detectat que alguns països apareixien amb noms diferents (per exemple, "Czechia" vs "Czech Republic" o "Turkiye" vs "Turkey").  

        Per garantir que les dades es poguessin unir correctament:
        1. S'ha creat un **diccionari de normalització** amb les correspondències entre noms diferents.
        2. S'ha aplicat aquest diccionari a la columna `Country` de cada dataset.
        3. S'ha realitzat un **join** utilitzant `Country` com a identificador unificat.
        
        Aquesta normalització assegura que els països coincideixin entre datasets i evita errors en l'anàlisi combinada de felicitat, educació i població.
        """)
    
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
st.write("Es mostra el nom del país, l'índex de felicitat, l'índex educatiu i el nivell d'ingressos.")
st.dataframe(sorted_df)

# -------------- PAISOS AMB POBLACIÓ 2022 DESCONEGUDA ---------------
# Filtrar països del dataset happiness amb població del 2022 desconeguda
missing_population = merged_happiness.filter(pl.col("Population_2022").is_null())["Country"].to_list()

# Mostrar el resultat a Streamlit
st.header("Països sense població 2022")
col1, col2 = st.columns(2)
with col1:
    st.write("Nombre de paisos amb informació desconeguda sobre la població del 2022")
    st.write(len(missing_population))
with col2:
    st.write("Països pels quals no es disposa de dades de població del 2022.")
    st.markdown(missing_population)


# -------------- GRÀFIC POBLACIÓ vs ÍNDEX DE FELICITAT ---------------
# Filtrar només països amb dades de població i felicitat
plot_df = merged_happiness.filter(
    (pl.col("Population_2022").is_not_null()) &
    (pl.col("Ladder_score").is_not_null())
)

# Seleccionar les columnes clau
plot_df = plot_df.select(["Country", "Population_2022", "Ladder_score"])

# Crear gràfic de punts
scatter = alt.Chart(plot_df).mark_circle(size=60).encode(
    x=alt.X("Population_2022", title="Població 2022", scale=alt.Scale(type="log")),
    y=alt.Y("Ladder_score", title="Índex de felicitat"),
    tooltip=["Country", "Population_2022", "Ladder_score"]
).properties(
    title="Relació entre població i índex de felicitat",
    width=700,
    height=400
).interactive()

# Mostrem el gràfic a Streamlit
st.header("Gràfic de punts Població vs Índex de felicitat")
st.write("Aquesta visualització mostra la relació entre la població d’un país (eix X) i el seu índex de felicitat (eix Y), permetent observar com varia la felicitat en funció de la mida de la població.")
st.altair_chart(scatter)



# ------------ MAPA DEL MÓN AMB MITJANA D'INDEX DE FELICITAT PER CONTINENT -----------------
# Filtrar països amb continent assignat i calcular mitjana de l'índex de felicitat per continent
continent_avg = (
    merged_happiness
    .filter(pl.col("Continent").is_not_null())  # <-- eliminar països sense continent [Kosovo]
    .group_by("Continent")
    .agg(pl.col("Ladder_score").mean().alias("Average_Happiness"))
)

# Coordenades aproximades per centrar els continents al mapa
continent_coords = {
    "Africa": {"lat": 0, "lon": 20},
    "Asia": {"lat": 35, "lon": 100},
    "Europe": {"lat": 50, "lon": 10},
    "North America": {"lat": 50, "lon": -100},
    "South America": {"lat": -15, "lon": -60},
    "Oceania": {"lat": -25, "lon": 135},
}

# Afegir latitud i longitud amb with_columns
continent_avg = continent_avg.with_columns([
    pl.col("Continent").map_elements(lambda c: continent_coords[c]["lat"], return_dtype=pl.Float64).alias("lat"),
    pl.col("Continent").map_elements(lambda c: continent_coords[c]["lon"], return_dtype=pl.Float64).alias("lon")
])

# Crear el mapa base amb les fronteres mundials
world_map = alt.topo_feature("https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json", "countries")

base = (alt.Chart(world_map).mark_geoshape(fill='lightgrey', stroke='white', strokeWidth=0.5)
            .project("naturalEarth1")
            .properties(
                width=1000,
                height=600
            ))

# Afegir els punts amb la mitjana de felicitat
points = alt.Chart(continent_avg).mark_circle(size=1500, color="black").encode(
    longitude="lon:Q",
    latitude="lat:Q",
    tooltip=["Continent", alt.Tooltip("Average_Happiness", format=".2f")]
)

# Afegir text amb el valor exacte
labels = alt.Chart(continent_avg).mark_text(
    align="center",
    baseline="middle",
    fontSize=18,
    fontWeight="bold",
    color="white"
).encode(
    longitude="lon:Q",
    latitude="lat:Q",
    text=alt.Text("Average_Happiness", format=".2f"),
    tooltip=["Continent", alt.Tooltip("Average_Happiness", format=".2f")]
)

# Combinar el mapa, punts i labels
map_chart = base + points + labels

# Mostrar a Streamlit
st.header("Mitjana de l'índex de felicitat per continent")
st.altair_chart(map_chart)

# Mostrar països sense continent
missing_continent = merged_happiness.filter(pl.col("Continent").is_null())["Country"].to_list()
if missing_continent:
    st.warning(f"Països sense continent assignat: {missing_continent}")


# -------------- 5 PAISOS MÉS FELIÇOS PER CONTINENT --------------------

# Filtrar països amb continent assignat
lf = merged_happiness.filter(pl.col("Continent").is_not_null()).lazy()

# Query: ordenar, agrupar, agafar top 5 i seleccionar columnes
top5_lazy = (
    lf.sort(["Continent", "Ladder_score"], descending=[False, True])
    .group_by("Continent")
    .agg([
        pl.col("Country").head(5).alias("País"),
        pl.col("Ladder_score").head(5).alias("Índex de felicitat"),
        pl.col("Education_Index").head(5).alias("Education index"),
        pl.col("Income").head(5).alias("Ingressos")
    ])
)

# Executar la query amb collect
top5 = top5_lazy.collect()

# Explode per tenir cada país en una fila
top5 = top5.explode(["País", "Índex de felicitat", "Education index", "Ingressos"])

# Mostrem a Streamlit
st.header("Top 5 països més feliços per continent")
st.write("La següent taula mostra els 5 països més feliços de cada continent, amb el seu índex de felicitat, l’índex educatiu i el nivell d’ingressos.")
st.dataframe(top5)



