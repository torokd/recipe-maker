import streamlit as st

st.title("Későbbre mentett receptek 📌")

if "saved_recipes" not in st.session_state:
    st.session_state.saved_recipes = []

if not st.session_state.saved_recipes:
    st.info("Még nincs elmentett recept. Ments el egyet a receptkereső oldalon!")
else:
    for recipe in st.session_state.saved_recipes:
        with st.expander(f"📖 {recipe.get('name', 'Recept')}", expanded=True):
            st.markdown("**Hozzávalók:**")
            for ingredient in recipe.get("ingredients", []):
                st.write(f"- {ingredient}")

            st.markdown("**Elkészítés:**")
            for step in recipe.get("instructions", []):
                st.write(f"- {step}")