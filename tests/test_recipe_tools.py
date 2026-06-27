from __future__ import annotations

import pytest
from mcp.server.fastmcp.exceptions import ToolError

from tools.recipe_tools import register_recipe_tools


class FakeMCP:
    def __init__(self) -> None:
        self.tools = {}

    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            return func

        return decorator


class FakeMealie:
    def __init__(self) -> None:
        self.created_names = []
        self.updated = []
        self.patched = []
        self.requests = []
        self.recipes = {
            "stifado": {
                "slug": "stifado",
                "totalTime": "2 hours 30 minutes",
                "prepTime": "30 minutes",
                "performTime": "2 hours",
                "recipeCategory": [{"name": "Greek", "slug": "greek"}],
                "tags": [{"name": "Beef", "slug": "beef"}],
                "recipeIngredient": [{"note": "old ingredient"}],
                "recipeInstructions": [{"text": "old instruction"}],
            }
        }

    def get_recipe(self, slug: str):
        return dict(self.recipes[slug])

    def create_recipe(self, name: str):
        self.created_names.append(name)
        return "stifado"

    def update_recipe(self, slug: str, payload: dict):
        self.updated.append((slug, payload))
        return payload

    def patch_recipe(self, slug: str, payload: dict):
        self.patched.append((slug, payload))
        return payload

    def _handle_request(self, method: str, url: str, **kwargs):
        self.requests.append((method, url, kwargs))
        return {"method": method, "url": url, **kwargs}


def registered_tools(mealie: FakeMealie) -> dict:
    mcp = FakeMCP()
    register_recipe_tools(mcp, mealie)
    return mcp.tools


def test_update_recipe_preserves_raw_metadata_shape() -> None:
    mealie = FakeMealie()
    tools = registered_tools(mealie)

    result = tools["update_recipe"](
        "stifado",
        ["2 tablespoons tomato purée"],
        ["Keep heating while adding tomato purée."],
    )

    assert mealie.updated[0][0] == "stifado"
    assert result["totalTime"] == "2 hours 30 minutes"
    assert result["recipeCategory"] == [{"name": "Greek", "slug": "greek"}]
    assert result["tags"] == [{"name": "Beef", "slug": "beef"}]
    assert result["recipeIngredient"] == [
        {"note": "2 tablespoons tomato purée", "isFood": True, "disableAmount": False}
    ]
    assert result["recipeInstructions"] == [
        {"text": "Keep heating while adding tomato purée.", "ingredientReferences": []}
    ]


def test_update_recipe_ingredients_preserves_structured_entries() -> None:
    mealie = FakeMealie()
    tools = registered_tools(mealie)
    ingredients = [
        {
            "quantity": 4,
            "unit": {"name": "tablespoon"},
            "food": {"name": "malt vinegar"},
            "note": "The recipe calls for 2 tbsp twice",
        }
    ]

    result = tools["update_recipe_ingredients"]("stifado", ingredients)

    assert mealie.updated[0][0] == "stifado"
    assert result["totalTime"] == "2 hours 30 minutes"
    assert result["recipeCategory"] == [{"name": "Greek", "slug": "greek"}]
    assert result["tags"] == [{"name": "Beef", "slug": "beef"}]
    assert result["recipeIngredient"] == ingredients
    assert result["recipeInstructions"] == [{"text": "old instruction"}]


def test_create_recipe_updates_new_recipe_with_payload() -> None:
    mealie = FakeMealie()
    tools = registered_tools(mealie)

    result = tools["create_recipe"](
        "Stifado",
        ["1 kilogram beef"],
        ["Cook gently."],
    )

    assert mealie.created_names == ["Stifado"]
    assert mealie.updated[0][0] == "stifado"
    assert result["recipeIngredient"][0]["note"] == "1 kilogram beef"
    assert result["recipeInstructions"][0]["text"] == "Cook gently."


def test_get_foods_searches_food_endpoint() -> None:
    mealie = FakeMealie()
    tools = registered_tools(mealie)

    result = tools["get_foods"]("malt vinegar", page=1, per_page=10)

    assert result["method"] == "GET"
    assert result["url"] == "/api/foods"
    assert result["params"] == {"search": "malt vinegar", "page": 1, "perPage": 10}


def test_create_food_posts_food_name() -> None:
    mealie = FakeMealie()
    tools = registered_tools(mealie)

    result = tools["create_food"]("malt vinegar")

    assert result["method"] == "POST"
    assert result["url"] == "/api/foods"
    assert result["json"] == {"name": "malt vinegar"}


def test_get_units_searches_unit_endpoint() -> None:
    mealie = FakeMealie()
    tools = registered_tools(mealie)

    result = tools["get_units"]("wineglass")

    assert result["method"] == "GET"
    assert result["url"] == "/api/units"
    assert result["params"] == {"search": "wineglass"}


def test_create_unit_posts_unit_name() -> None:
    mealie = FakeMealie()
    tools = registered_tools(mealie)

    result = tools["create_unit"]("wineglass")

    assert result["method"] == "POST"
    assert result["url"] == "/api/units"
    assert result["json"] == {"name": "wineglass"}


def test_patch_recipe_sends_only_provided_fields() -> None:
    mealie = FakeMealie()
    tools = registered_tools(mealie)

    result = tools["patch_recipe"]("stifado", description="Updated", total_time="30 minutes")

    assert result == {"description": "Updated", "totalTime": "30 minutes"}
    assert mealie.patched == [("stifado", {"description": "Updated", "totalTime": "30 minutes"})]


def test_patch_recipe_requires_at_least_one_field() -> None:
    tools = registered_tools(FakeMealie())

    with pytest.raises(ToolError, match="At least one field must be provided"):
        tools["patch_recipe"]("stifado")
