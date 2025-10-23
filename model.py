import polars as pl
import streamlit as st
import patito as pt

# Esquema de validació per tres columnes del dataset
class Country (pt.Model):
    Country: str = pt.Field(description="Nom del país", unique=True, min_length=1)
    Ladder_score: float = pt.Field(description="Índex de felicitat", ge=0, le=10)
    Education_Index: float = pt.Field(description="Índex d'educació", ge=0, le=1)

