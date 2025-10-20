import streamlit as st

data = st.Page("pages/data.py", title="data")


pg = st.navigation([data])

st.set_page_config(page_title="Index de felicitat", page_icon=":grinning:")
pg.run()
