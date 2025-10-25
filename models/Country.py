from typing import Literal
import patito as pt


class Country(pt.Model):
    # Identificador principal
    Country: str = pt.Field(unique=True, min_length=1)

    # Camps de world_education_and_income.csv
    Education_Index: float | None = pt.Field(ge=0, le=1)
    Education_Level: Literal[
                         "Very High Education Level",
                         "High to Moderate Education Level",
                         "Low to Moderate Education Level",
                         "Very Low Education Level"
                     ] | None
    Income: Literal[
                "High income",
                "Upper middle income",
                "Lower middle income",
                "Low income"
            ] | None

    # Camps de world_happiness.csv
    Regional_indicator: str | None
    Ladder_score: float = pt.Field(ge=0, le=10)
    upperwhisker: float | None = pt.Field(ge=0, le=10)
    lowerwhisker: float | None = pt.Field(ge=0, le=10)
    Log_GDP_per_capita: float | None
    Social_support: float | None
    Healthy_life_expectancy: float | None = pt.Field(ge=0, le=1)
    Freedom_to_make_life_choices: float | None = pt.Field(ge=0, le=1)
    Generosity: float | None = pt.Field(ge=0, le=1)
    Perceptions_of_corruption: float | None = pt.Field(ge=0, le=1)
    Dystopia_residual: float | None

    # Camps de world_population.csv
    Rank: int | None
    CCA3: str | None = pt.Field(min_length=3, max_length=3)
    Capital: str | None
    Continent: Literal[
                   "Asia",
                   "Europe",
                   "Africa",
                   "Oceania",
                   "North America",
                   "South America"
               ] | None
    Population_2022: int | None
    Population_2020: int | None
    Population_2015: int | None
    Population_2010: int | None
    Population_2000: int | None
    Population_1990: int | None
    Population_1980: int | None
    Population_1970: int | None

    Area_km2: int | None
    Density_per_km2: float | None
    Growth_Rate: float | None
    World_Population_Percentage: float | None = pt.Field(ge=0, le=100)
