# 📊 Análisis del Índice de Felicidad Mundial

Aplicación interactiva desarrollada con **Streamlit** que analiza y visualiza el índice de felicidad de los países del mundo, combinando datos de felicidad, educación, ingresos y población.

## 🎯 ¿En qué consiste?

Este proyecto permite explorar las relaciones entre el índice de felicidad de los países y diferentes factores socioeconómicos mediante visualizaciones interactivas. La aplicación integra tres fuentes de datos:

- **World Happiness Report**: Índice de felicidad y factores asociados
- **Datos de Educación e Ingresos**: Nivel educativo e ingresos por país
- **Datos de Población Mundial**: Población histórica, área y densidad

La aplicación ofrece múltiples análisis y visualizaciones:

- 📈 Ranking de países por índice de felicidad
- 🗺️ Mapa mundial con la felicidad media por continente
- 📊 Gráficos de correlación entre población y felicidad
- 🔥 Heatmap de felicidad según educación e ingresos
- 🏆 Top 5 países más felices por continente

## 📁 Estructura del proyecto

```
Streamlit-Happiness-Index/
│
├── main.py                        # Punto de entrada de la aplicación
├── country_normalization.py       # Normalización de nombres de países
│
├── pages/
│   └── data.py                    # Página principal con análisis y visualizaciones
│
├── models/
│   └── Country.py                 # Modelo de validación de datos (Patito)
│
├── pyproject.toml                 # Configuración del proyecto y dependencias
├── uv.lock                        # Archivo de bloqueo de dependencias (uv)
└── .python-version                # Versión de Python requerida (3.13)
```

### Descripción de archivos principales

#### `main.py`
Punto de entrada de la aplicación Streamlit. Define la configuración de la página y la navegación.

#### `country_normalization.py`
Contiene un diccionario de mapeo y una función auxiliar para normalizar los nombres de países que varían entre los diferentes datasets (por ejemplo, "Czech Republic" → "Czechia", "Turkey" → "Turkiye").

#### `pages/data.py`
Archivo principal de la aplicación que:
- Carga los tres datasets desde GitLab
- Normaliza y combina los datos mediante joins
- Valida los datos utilizando el modelo `Country`
- Genera múltiples visualizaciones interactivas

#### `models/Country.py`
Define el esquema de validación de datos utilizando **Patito** (wrapper sobre Polars). Especifica los tipos de datos, restricciones y valores posibles para cada campo.

## 🚀 Cómo arrancar el proyecto

### Requisitos previos

- Python 3.13 o superior
- `uv` (gestor de paquetes moderno) o `pip`

### Instalación

#### Opción 1: Usando `uv` (recomendado)

```bash
# Clonar el repositorio
git clone https://github.com/alba-mu/Streamlit-Happiness-Index.git
cd Streamlit-Happiness-Index

# Instalar dependencias con uv
uv sync
```

#### Opción 2: Usando `pip`

```bash
# Clonar el repositorio
git clone https://github.com/alba-mu/Streamlit-Happiness-Index.git
cd Streamlit-Happiness-Index

# Crear un entorno virtual
python3.13 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install streamlit polars patito altair
```

### Ejecutar la aplicación

```bash
# Con uv
uv run streamlit run main.py

# Con pip (con el entorno virtual activado)
streamlit run main.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

## 🛠️ Tecnologías utilizadas

- **[Streamlit](https://streamlit.io/)** (v1.50.0): Framework para crear aplicaciones web interactivas
- **[Polars](https://pola.rs/)** (v1.34.0): Procesamiento eficiente de dataframes
- **[Altair](https://altair-viz.github.io/)** (v5.5.0): Librería de visualización declarativa
- **[Patito](https://github.com/JakobGM/patito)** (v0.8.5): Validación de esquemas de datos sobre Polars

## 📊 Características principales

### Normalización de datos
El proyecto implementa un sistema robusto de normalización de nombres de países para garantizar que los datos de diferentes fuentes se puedan unir correctamente.

### Validación de datos
Utiliza **Patito** para validar que los datos combinados cumplan con el esquema esperado antes de realizar análisis.

### Visualizaciones interactivas
- Gráficos de dispersión con escala logarítmica
- Mapas mundiales con proyección geográfica
- Heatmaps con escalas de color
- Tablas dinámicas ordenables

### Caché de datos
Implementa `@st.cache_data` para optimizar la carga de datasets y mejorar el rendimiento.

## 📝 Notas adicionales

- Los datos se cargan dinámicamente desde GitLab en cada ejecución
- La aplicación soporta filtrado interactivo y tooltips informativos
- Se incluye manejo de valores nulos y datos faltantes
- Toda la interfaz está en catalán

## 🎓 Proyecto Educativo

Este proyecto ha sido desarrollado como **práctica educativa** del ciclo formativo de **Desarrollo de Aplicaciones Web con perfil en Bioinformática (DAW-BIO)**.

**Objetivo**: Aplicar conocimientos de análisis de datos, visualización interactiva y desarrollo web utilizando tecnologías modernas de Python.





