import streamlit as st
import polars as pl
from urllib.parse import urljoin
import patito as pt
import altair as alt
from country_normalization import country_name_map, normalize_country_column


st.title("ANÀLISI DE LA FELICITAT DELS PAISOS DEL MÓN")


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
     


# Carregar datasets
education = load_education_and_income()
happiness = load_happiness()
population = load_population()


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

# Renombrar columnes per poder validar amb el model
merged_happiness = merged_happiness.rename({
    "Ladder score": "Ladder_score",
    "Education Index": "Education_Index"
})




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
missing_population = merged_happiness.filter(pl.col("2022 Population").is_null())["Country"].to_list()

# Mostrar el resultat a Streamlit
st.header("Països sense població 2022")
col1, col2 = st.columns(2)
with col1:
    st.write("Nombre de paisos amb informació desconeguda sobre la població del 2022")
    st.write(len(missing_population))
with col2:
    st.write("Llistat de països pels quals no es disposa de dades de població del 2022.")
    st.markdown(missing_population)


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



# ------------ MAPA DEL MÓN AMB MITJANA D'INDEX DE FELICITAT PER CONTINENT -----------------
# Mitjana de l'índex de felicitat per continent
continent_avg = (merged_happiness.group_by("Continent")
                    .agg(pl.col("Ladder_score").mean().alias("Average_Happiness")))

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

base = (alt.Chart(world_map).mark_geoshape()
            .project("naturalEarth1")
            .properties(
                width=800,
                height=400
            ))

# Afegir els punts amb la mitjana de felicitat
points = alt.Chart(continent_avg).mark_circle(size=400, color="red").encode(
    longitude="lon:Q",
    latitude="lat:Q",
    tooltip=["Continent", alt.Tooltip("Average_Happiness", format=".2f")]
)

# Afegir text amb el valor exacte
labels = alt.Chart(continent_avg).mark_text(
    align="center",
    baseline="middle",
    fontSize=12,
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


# -------------- 5 PAISOS MÉS FELIÇOS PER CONTINENT --------------------
# Convertir a LazyFrame
lf = merged_happiness.lazy()

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



