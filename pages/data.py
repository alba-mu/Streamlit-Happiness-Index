import streamlit as st
import polars as pl
from urllib.parse import urljoin

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
education_income = load_education_and_income()
happiness = load_happiness()
population = load_population()

st.header("Education and Income")
st.write(education_income.head())
st.header("Happiness")
st.write(happiness.head())
st.header("Population")
st.write(population.head())
