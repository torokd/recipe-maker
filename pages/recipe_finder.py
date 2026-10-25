# Imports
import json
import os
import streamlit as st
from google import genai
from google.genai import types
from recipe_storage import save_recipe


# API key setup
try:
    API_KEY = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    API_KEY = ""

API_KEY = API_KEY or os.getenv("GEMINI_API_KEY", "")

@st.cache_resource
def get_client(api_key):
    return genai.Client(api_key=api_key)


# Streamlit page configuration
# Page title and icon
st.set_page_config(
    page_title="Mit egyek ma?",
    page_icon="🍳🤔"
)

# Title
st.title("👩‍🍳 Le petit sous-chef d'Adèle")

if "recipe_finder_recipes" not in st.session_state:
    st.session_state.recipe_finder_recipes = []

# Dietary preferences
st.text("Válaszd ki az étrendi preferenciáidat:")
is_vegetarian = st.checkbox("Vegetáriánus")
is_fish_free = st.checkbox("Halmentes", value=True)

# Cooking speed
st.text("Válaszd ki a főzési sebességet:")
speed = st.radio(
    "Milyen gyorsan szeretnél főzni?",
    ["Gyors (30 perc alatt)", "Ráérek"],
)

# Cooking type preferencies
st.text("Válaszd ki a főzési preferenciáidat:")
is_oven = st.checkbox("Sütőben süthető")
is_stove = st.checkbox("Tűzhelyen főzhető")
is_noCook = st.checkbox("Nem igényel főzést")

# Food types
food_type = st.selectbox(
    "Milyen ételt szeretnél enni?",
    ["Szendvics", "Főzelék", "Leves", "Saláta", "Tészta", "Desszert", "Egyéb"],
)

# At home storage
use_storage = st.checkbox("Szeretném az itthoni alapanyagokat használni")
storage = st.text_area("Írd be mi van otthon:", height=100) if use_storage else ""

# Generate recipes button
if st.button("👀 Mutasd a recepteket", type="primary"):
    if not API_KEY:
        st.error(
            "Add meg a GEMINI_API_KEY értékét "
            "a Streamlit secrets vagy a környezeti változók között!"
        )
    else:
        try:
            client = get_client(API_KEY)

            match (is_vegetarian, is_fish_free):
                                case (True, True):
                                        diet_pref = "Vegetáriánus és húsmentes + halmentes"
                                case (True, False):
                                        diet_pref = "Vegetáriánus és húsmentes"
                                case (False, True):
                                        diet_pref = "Nem tartalmaz seafoodot pl. hal, kagyló, rák, egyéb tenger gyümölcsei, egyéb vizi élőlény"
                                case _:
                                        diet_pref = "Nincs külön étrendi igény"

            prompt = f"""
Adj pontosan 3 egyszerű, rövid receptet magyarul a street kitchen oldaláról (https://streetkitchen.hu/).

Étrendi igény: {diet_pref}
Elkészítési sebesség: {"30 perc alatt" if speed == "Gyors (30 perc alatt)" else "Ráérek nincs időkorlát"}
Étel típusa: {food_type}
Mi van itthon: {storage}
Elkészítési mód: {"Sütőben süthető" if is_oven else ""} {"Tűzhelyen süthető (serpenyőben, lábosban, fazékban)" if is_stove else ""} {"Nem igényel főzést" if is_noCook else ""}

Receptenként:
- Legfeljebb 5 rövid elkészítési lépés.
- Hétköznapi boltban beszerezhető alapanyagok.
- Vedd számításba a felhasználó által megadott hozzávalókat amennyiben kapsz hozzá adatokat a "Mi van itthon: {storage}" részben.

Kizárólag az alábbi szerkezetű JSON-t add vissza:
{{
  "recipes": [
    {{
      "name": "Recept neve",
      "ingredients": ["hozzávaló 1", "hozzávaló 2"],
      "instructions": ["1. lépés", "2. lépés"],
      "street_kitchen_url": "street kitchen recept URL",
      "is_favorite": false
    }}
  ]
}}
"""

            with st.spinner("Máris érkeznek a receptek"):
                response = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.7,
                        max_output_tokens=1500,
                    ),
                )

            data = json.loads(response.text)
            recipes = data.get("recipes", [])

            if not recipes:
                st.warning("😢 Nem érkezett recept. Próbáld újra!")
            else:
                st.session_state.recipe_finder_recipes = recipes
                st.success("✅ Elkészültek a receptek!")

        except json.JSONDecodeError:
            st.error("⚠️ A válasz nem érvényes JSON. Próbáld újra!")
        except Exception as e:
            st.error(f"‼️ Hiba történt: {e}")

for i, recipe in enumerate(st.session_state.recipe_finder_recipes):
    with st.expander(
        f"📖 {recipe.get('name', 'Recept')}",
        expanded=False,
    ):
        st.markdown("**Hozzávalók:**")
        for ing in recipe.get("ingredients", []):
            st.write(f"- {ing}")

        st.markdown("**Elkészítés:**")
        for step in recipe.get("instructions", []):
            st.write(f"- {step}")

        st.markdown("**Street Kitchen URL:**")
        for url in recipe.get("street_kitchen_url", []):
            st.write(f"- [{url}]({url})")

        if st.button("Mentés későbbre", key=f"save_recipe_{i}"):
            try:
                if save_recipe(recipe):
                    st.success("A recept el lett mentve a közös mentett listába.")
                else:
                    st.info("Ez a recept már el van mentve.")
            except Exception as e:
                st.error(f"Nem sikerült elmenteni a receptet: {e}")