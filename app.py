
import json
import os
import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(
    page_title="Gyors Recept Ajánló",
    page_icon="🍳"
)

st.title("🍳 Gyors AI Recept Ajánló")

# API-kulcs beállítása Streamlit secretsből vagy környezeti változóból
try:
    API_KEY = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    API_KEY = ""

API_KEY = API_KEY or os.getenv("GEMINI_API_KEY", "")


@st.cache_resource
def get_client(api_key):
    return genai.Client(api_key=api_key)


is_vegetarian = st.checkbox("Vegetáriánus")

food_type = st.selectbox(
    "Milyen ételt szeretnél enni?",
    ["Szendvics", "Főzelék", "Sült étel"]
)

if st.button("Kérem a receptet ✨", type="primary"):
    if not API_KEY:
        st.error(
            "Add meg a GEMINI_API_KEY értékét "
            "a Streamlit secrets vagy a környezeti változók között!"
        )
    else:
        try:
            client = get_client(API_KEY)

            diet_pref = (
                "vegetáriánus, húsmentes"
                if is_vegetarian
                else "bármilyen"
            )

            prompt = f"""
Adj pontosan 3 egyszerű, rövid receptet magyarul.

Étel típusa: {food_type}
Étrendi igény: {diet_pref}

Receptenként:
- Legfeljebb 5 hozzávaló.
- Legfeljebb 3 rövid elkészítési lépés.
- Egyszerű, hétköznapi alapanyagok.
- Vegetáriánus választásnál ne használj húst vagy halat.

Kizárólag az alábbi szerkezetű JSON-t add vissza:
{{
  "recipes": [
    {{
      "name": "Recept neve",
      "ingredients": ["hozzávaló 1", "hozzávaló 2"],
      "instructions": ["1. lépés", "2. lépés"]
    }}
  ]
}}
"""

            with st.spinner("Gyors receptgenerálás... ⚡"):
                response = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.7,
                        max_output_tokens=500,
                    ),
                )

            data = json.loads(response.text)
            recipes = data.get("recipes", [])

            if not recipes:
                st.warning("Nem érkezett recept. Próbáld újra!")
            else:
                st.success("Elkészültek a receptek! 🍽️")

                for i, recipe in enumerate(recipes, 1):
                    with st.expander(
                        f"📖 {i}. {recipe.get('name', 'Recept')}",
                        expanded=True,
                    ):
                        st.markdown("**Hozzávalók:**")
                        for ing in recipe.get("ingredients", []):
                            st.write(f"- {ing}")

                        st.markdown("**Elkészítés:**")
                        for step in recipe.get("instructions", []):
                            st.write(f"- {step}")

        except json.JSONDecodeError:
            st.error("A válasz nem érvényes JSON. Próbáld újra!")
        except Exception as e:
            st.error(f"Hiba történt: {e}")