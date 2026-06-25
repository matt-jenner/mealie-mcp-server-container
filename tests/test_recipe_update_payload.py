from __future__ import annotations

from tools.recipe_tools import recipe_update_payload


def test_recipe_update_payload_preserves_raw_mealie_metadata() -> None:
    recipe = {
        "slug": "stifado",
        "totalTime": "2 hours 30 minutes",
        "prepTime": "30 minutes",
        "performTime": "2 hours",
        "recipeCategory": [{"name": "Weekend Dinners", "slug": "weekend-dinners"}],
        "tags": [{"name": "Greek", "slug": "greek"}],
        "recipeIngredient": [{"note": "old ingredient"}],
        "recipeInstructions": [{"text": "old instruction"}],
    }

    payload = recipe_update_payload(
        recipe,
        ["2 tablespoons tomato purée"],
        ["Keep heating while adding tomato purée."],
    )

    assert payload["totalTime"] == "2 hours 30 minutes"
    assert payload["recipeCategory"] == [{"name": "Weekend Dinners", "slug": "weekend-dinners"}]
    assert payload["tags"] == [{"name": "Greek", "slug": "greek"}]
    assert payload["recipeIngredient"] == [
        {"note": "2 tablespoons tomato purée", "isFood": True, "disableAmount": False}
    ]
    assert payload["recipeInstructions"] == [
        {"text": "Keep heating while adding tomato purée.", "ingredientReferences": []}
    ]
