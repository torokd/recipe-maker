import time
import streamlit as st
from recipe_storage import (
    delete_saved_recipe,
    get_saved_recipes,
    set_recipe_favorite,
)

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
            expander_col, favorite_col, btn_col = st.columns([0.84, 0.08, 0.08])

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

                    street_url = recipe.get("street_kitchen_url")
                    if street_url:
                        st.markdown(
                            f"🔗 **Street Kitchen:** [{street_url}]({street_url})"
                        )

            with favorite_col:
                is_favorite = recipe.get("is_favorite", False)
                if st.button(
                    "❤️" if is_favorite else "🤍",
                    type="tertiary",
                    help=(
                        "Eltávolítás a kedvencek közül"
                        if is_favorite
                        else "Hozzáadás a kedvencekhez"
                    ),
                    key=f"toggle_favorite_recipe_{recipe['id']}",
                ):
                    try:
                        set_recipe_favorite(recipe["id"], not is_favorite)
                        st.rerun()
                    except Exception as favorite_error:
                        st.error(
                            "Nem sikerült módosítani a kedvenc állapotot: "
                            f"{favorite_error}"
                        )

            with btn_col:
                if st.button(
                    "🗑️",
                    type="tertiary",
                    help="Recept törlése",
                    key=f"remove_saved_recipe_{recipe['id']}",
                ):
                    try:
                        delete_saved_recipe(recipe["id"])
                        st.toast("A recept sikeresen törölve! 🗑️", icon="✅")
                        time.sleep(0.8)
                        st.rerun()
                    except Exception as delete_error:
                        st.error(f"Sikertelen törlés: {delete_error}")

except Exception as e:
    st.error(f"Nem sikerült betölteni a mentett recepteket: {e}")