import streamlit as st

# Menu
recipe_finder = st.Page("pages/recipe_finder.py", title="Recept kereső", icon="🔎")
saved_page = st.Page("pages/saved.py", title="Mentett receptek", icon="📌")
pg = st.navigation([recipe_finder, saved_page])
pg.run()