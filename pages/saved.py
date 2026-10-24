import time
import streamlit as st
from recipe_storage import delete_saved_recipe, get_saved_recipes

st.title("Későbbre mentett receptek 📌")
st.caption("Ez a lista minden alkalmazáshasználó számára közös.")

# --- EGYEDI CSS A TOAST ÜZENET KÖZÉPRE ALULRA POZICIONÁLÁSÁHOZ ---
st.markdown(
    """
    <style>
    div[data-testid="stToast"] {
        position: fixed;
        bottom: 2rem;
        left: 50%;
        transform: translateX(-50%);
        right: auto;
        top: auto;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

try:
    saved_recipes = get_saved_recipes()
    if not saved_recipes:
        st.info("Még nincs elmentett recept. Ments el egyet a receptkereső oldalon!")
    else:
        for recipe in saved_recipes:
            expander_col, btn_col = st.columns([0.82, 0.18])

            with expander_col:
                with st.expander(
                    f"📖 {recipe.get('name', 'Recept')}", expanded=False
                ):
                    st.markdown("**Hozzávalók:**")
                    for ingredient in recipe.get("ingredients", []):
                        st.write(f"- {ingredient}")

                    st.markdown("**Elkészítés:**")
                    for step in recipe.get("instructions", []):
                        st.write(f"- {step}")

            with btn_col:
                if st.button(
                    "Törlés",
                    icon=":material/delete:",
                    type="tertiary",
                    help="Recept törlése",
                    key=f"remove_saved_recipe_{recipe['id']}",
                ):
                    try:
                        delete_saved_recipe(recipe["id"])
                        # Sikeres törlés toast üzenet alul középen
                        st.toast("A recept sikeresen törölve! 🗑️", icon="✅")
                        time.sleep(0.8)
                        st.rerun()
                    except Exception as delete_error:
                        st.error(f"Sikertelen törlés: {delete_error}")

except Exception as e:
    st.error(f"Nem sikerült betölteni a mentett recepteket: {e}")