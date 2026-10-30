import streamlit as st

# Menu
recipe_finder = st.Page("pages/recipe_finder.py", title="Recept kereső", icon="🔎")
pg = st.navigation([recipe_finder])
pg.run()