import streamlit as st
from recipe_storage import delete_saved_recipe, get_saved_recipes

st.title("Későbbre mentett receptek 📌")
st.caption("Ez a lista minden alkalmazáshasználó számára közös.")

try:
    saved_recipes = get_saved_recipes()
    if not saved_recipes:
        st.info("Még nincs elmentett recept. Ments el egyet a receptkereső oldalon!")
    else:
        for recipe in saved_recipes:
            # Oszlopok: a bal oldali a lenyitható recept, a jobb oldali a mindig látható törlés gomb
            expander_col, btn_col = st.columns([0.82, 0.18])

            with expander_col:
                # Az expanded=False miatt alapból összecsukott
                with st.expander(f"📖 {recipe.get('name', 'Recept')}", expanded=False):
                    st.markdown("**Hozzávalók:**")
                    for ingredient in recipe.get("ingredients", []):
                        st.write(f"- {ingredient}")

                    st.markdown("**Elkészítés:**")
                    for step in recipe.get("instructions", []):
                        st.write(f"- {step}")

            with btn_col:
                # Ez a gomb kint van az expanderen kívül, így összecsukott állapotban is látszik és kattintható!
                if st.button(
                    "Törlés",
                    icon=":material/delete:",
                    type="tertiary",
                    help="Recept törlése",
                    key=f"remove_saved_recipe_{recipe['id']}",
                ):
                    delete_saved_recipe(recipe["id"])
                    st.rerun()
                    
except Exception as e:
    st.error(f"Nem sikerült betölteni a mentett recepteket: {e}")