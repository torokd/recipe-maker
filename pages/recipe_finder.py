# Imports
import json
import os
import streamlit as st
from google import genai
from google.genai import types

# API Key retrieval
try:
    API_KEY = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    API_KEY = ""
API_KEY = API_KEY or os.getenv("GEMINI_API_KEY", "")

@st.cache_resource
def get_client(api_key):
    return genai.Client(api_key=api_key)

# Initialize recipe list
if "recipe_finder_recipes" not in st.session_state:
    st.session_state.recipe_finder_recipes = []

# Page title and icon
st.set_page_config(
    page_title="Le petit Adèle",
    page_icon="👩‍🍳"
)

# Title
st.title("👩‍🍳 Le petit Adèle")

# Dietary preferences
st.text("Válaszd ki az étrendi preferenciáidat:")
is_vegetarian = st.checkbox("Vegetáriánus")

# Cooking speed
cooking_speed = st.radio(
    "Mennyi időd van főzni?",
    ["Gyors (30 perc alatt)", "Ráérek"],
)

# Food types
dish_main_type = st.selectbox(
    "Milyen ételt szeretnél enni?",
    ["Leves", "Főétel"],
)

main_sub_type = st.selectbox(
    "Milyen ételt szeretnél enni?",
    ["Nincs kiválasztva", "Tészta", "Leves", "Saláta", "Sütemény", "Egyéb"], 
) if dish_main_type == "Főétel" else ""

# At home storage
use_storage = st.checkbox("Szeretném az itthoni alapanyagokat használni")
storage = st.text_area("Írd be mi van otthon:", height=100) if use_storage else ""

# Recipe counter
recipe_count = st.selectbox(
    "Hány receptet szeretnél generálni?",
    [1, 2, 3, 4, 5],
)

# Generate recipes button
if st.button("Recept generálása"):
    # Replace the previous results instead of accumulating recipe history.
    st.session_state.recipe_finder_recipes = []
    prompt_conditions = [
        f"Az étel típusa: {dish_main_type}.",
        f"Elkészítési idő: {'legfeljebb 30 perc' if cooking_speed == 'Gyors (30 perc alatt)' else 'az idő nem korlátozott'}.",
    ]
    if is_vegetarian:
        prompt_conditions.append("Kizárólag vegetáriánus receptet ajánlj.")
    if dish_main_type == "Főétel" and main_sub_type != "Nincs kiválasztva":
        prompt_conditions.append(f"A főétel kategóriája: {main_sub_type}.")
    if use_storage:
        if storage.strip():
            prompt_conditions.append(
                f"Használj minnél többet az otthoni alapanyagokból, nem kell mindet felhasználni: {storage.strip()}."
            )
        else:
            prompt_conditions.append("A felhasználó nem sorolt fel otthoni alapanyagokat, így nem kell figyelembe venni azokat.")

    prompt = (
        f"Javasolj {recipe_count} darab receptet magyarul az alábbi feltételek szerint. "
        "Kizárólag érvényes JSON-t adj vissza, az alábbi szerkezettel: "
        '{"recipes":[{"name":"recept neve","source_url":"az eredeti recept URL-je",'
        '"ingredients":[{"name":"hozzávaló","amount":"mennyiség"}],'
        '"steps":["elkészítési lépés"]}]}. '
        "A source_url mezőben add meg az eredeti forrásoldal teljes URL-jét, ahol a receptet találtad; ne találj ki URL-t. Csak akkor adj meg url-t ha az valoban latogathato es elo URL még."
        + "\n".join(prompt_conditions)
    )

    if not API_KEY:
        st.error("A Gemini API-kulcs nincs beállítva.")
    else:
        try:
            with st.spinner("Receptek generálása..."):
                response = get_client(API_KEY).models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.7,
                        max_output_tokens=5000,
                    ),
                )
            recipe_data = json.loads(response.text or "{}")
            recipes = recipe_data.get("recipes", [])
            if not isinstance(recipes, list) or not recipes:
                st.info("Nem érkezett recept a Geminitől.")
            else:
                st.session_state.recipe_finder_recipes = [recipe_data]
        except Exception as error:
            st.error(f"A recept generálása nem sikerült: {error}")

# Search results list
for recipe_batch in st.session_state.recipe_finder_recipes:
    for recipe in recipe_batch.get("recipes", []):
        if not isinstance(recipe, dict):
            continue

        recipe_name = recipe.get("name", "Névtelen recept")
        with st.expander(recipe_name):

            st.subheader("Hozzávalók")
            ingredients = recipe.get("ingredients", [])
            if ingredients:
                for ingredient in ingredients:
                    if isinstance(ingredient, dict):
                        name = ingredient.get("name", "")
                        amount = ingredient.get("amount", "")
                        st.write(f"- {name}: {amount}" if amount else f"- {name}")
                    else:
                        st.write(f"- {ingredient}")
            else:
                st.write("Nincsenek megadva hozzávalók.")

            st.subheader("Elkészítés")
            steps = recipe.get("steps", [])
            if steps:
                for index, step in enumerate(steps, start=1):
                    st.write(f"{index}. {step}")
            else:
                st.write("Nincsenek megadva elkészítési lépések.")

            source_url = recipe.get("source_url", "")
            st.subheader("Recept linkje")
            if source_url:
                st.markdown(f"[{source_url}]({source_url})")
