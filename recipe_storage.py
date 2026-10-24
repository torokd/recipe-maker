import streamlit as st
from supabase import Client, create_client


@st.cache_resource
def _create_supabase_client(url: str, key: str) -> Client:
    return create_client(url, key)


def get_supabase_client() -> Client:
    try:
        settings = st.secrets["supabase"]
        url = settings["url"]
        key = settings["key"]
    except (KeyError, FileNotFoundError) as error:
        raise RuntimeError(
            "Configure the Supabase url and key in Streamlit secrets."
        ) from error

    return _create_supabase_client(url, key)


def get_saved_recipes() -> list[dict]:
    response = (
        get_supabase_client()
        .table("saved_recipes")
        .select("id, name, ingredients, instructions")
        .order("created_at", desc=True)
        .execute()
    )
    return response.data


def save_recipe(recipe: dict) -> bool:
    client = get_supabase_client()
    existing = (
        client.table("saved_recipes")
        .select("ingredients, instructions")
        .eq("name", recipe.get("name", "Recept"))
        .execute()
    )
    if any(
        row["ingredients"] == recipe.get("ingredients", [])
        and row["instructions"] == recipe.get("instructions", [])
        for row in existing.data
    ):
        return False

    client.table("saved_recipes").insert(
        {
            "name": recipe.get("name", "Recept"),
            "ingredients": recipe.get("ingredients", []),
            "instructions": recipe.get("instructions", []),
        }
    ).execute()
    return True


def delete_saved_recipe(recipe_id: str) -> None:
    get_supabase_client().table("saved_recipes").delete().eq("id", recipe_id).execute()
