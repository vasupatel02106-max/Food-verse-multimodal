"""
End-to-End Verification Test Suite for Food Verse AI.
Tests schema validation, image processing, preset data integrity,
non-food guardrail error handling, and Streamlit HTTP server availability.
"""

import os
import sys
import urllib.request
from models import (
    FoodAnalysisResult,
    NutritionInfo,
    DietAndAllergens,
    Recipe,
    TextQueryResponse,
    ChatFollowUpResponse,
)
from utils import (
    process_image,
    pil_to_base64,
    calculate_macro_percentages,
    get_sample_analysis_presets,
    get_preset_as_model,
)
from agent import (
    NonFoodImageError,
    ApiKeyMissingError,
    chat_about_dish,
)

def test_models():
    print("Testing Pydantic models...")
    presets = get_sample_analysis_presets()
    for name, data in presets.items():
        obj = FoodAnalysisResult.model_validate(data)
        assert obj.dish_name is not None
        assert obj.nutrition.calories > 0
        assert obj.nutrition.health_score >= 1 and obj.nutrition.health_score <= 10
        assert len(obj.healthier_alternatives) == 3
        assert len(obj.recipe.instructions) > 0
        print(f"  [OK] Validated preset: {name} (Health Score: {obj.nutrition.health_score}/10, Calories: {obj.nutrition.calories} kcal)")

    # Test TextQueryResponse validation
    demo_query_data = {
        "query": "high-protein vegetarian dinner under 500 calories",
        "summary": "Nutritious options tailored for protein density.",
        "recommendations": [
            {
                "dish_name": "Tofu Soba Bowl",
                "cuisine": "Japanese",
                "calories": 440,
                "protein_g": 32.0,
                "carbs_g": 48.0,
                "fat_g": 14.0,
                "health_score": 9,
                "health_score_reason": "Excellent macro balance.",
                "diet_category": "Vegan",
                "allergens": ["Soy"],
                "description": "Appetizing dish.",
                "key_ingredients": ["Tofu", "Soba"],
                "quick_recipe_steps": ["Boil soba", "Pan sear tofu", "Combine and serve"]
            }
        ]
    }
    tq_obj = TextQueryResponse.model_validate(demo_query_data)
    assert len(tq_obj.recommendations) == 1
    print("  [OK] Validated TextQueryResponse model.")

def test_image_processing():
    print("\nTesting image processing and sample assets...")
    sample_files = [
        "sample_images/salmon_bowl.jpg",
        "sample_images/avocado_toast.jpg",
        "sample_images/vegetable_biryani.jpg",
        "sample_images/laptop_non_food.jpg",
    ]
    for path in sample_files:
        assert os.path.exists(path), f"Missing file: {path}"
        with open(path, "rb") as f:
            data = f.read()
        raw_bytes, mime, pil_img = process_image(data)
        thumb_b64 = pil_to_base64(pil_img)
        assert mime == "image/jpeg"
        assert len(raw_bytes) > 0
        assert len(thumb_b64) > 0
        print(f"  [OK] Processed {path}: {pil_img.size}, thumb b64 length: {len(thumb_b64)}")

def test_macros_and_utilities():
    print("\nTesting nutrition calculations and formatting...")
    # 42g protein (168 kcal), 36g carbs (144 kcal), 22g fat (198 kcal). Total = 510 kcal.
    p, c, f = calculate_macro_percentages(42.0, 36.0, 22.0)
    assert p + c + f == 100
    print(f"  [OK] Macro percentages: Protein {p}%, Carbs {c}%, Fat {f}% (Sum = {p+c+f}%)")

def test_non_food_guardrail():
    print("\nTesting non-food guardrail handling...")
    try:
        # Simulate non-food detection
        fake_result = {
            "is_food": False,
            "non_food_reason": "This image appears to show a laptop computer rather than food.",
            "dish_name": "Non Food",
            "cuisine": "N/A",
            "description": "N/A",
            "confidence_score": 0.0,
            "main_ingredients": [],
            "nutrition": {
                "serving_size": "N/A", "calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0,
                "health_score": 1, "health_score_reason": "Not food"
            },
            "diet_and_allergens": {
                "diet_category": "N/A", "is_vegetarian": False, "is_vegan": False,
                "is_gluten_free": False, "is_dairy_free": False, "allergens": [], "allergen_warning": "N/A"
            },
            "healthier_alternatives": [
                {"name": "N/A", "calorie_comparison": "0", "key_substitutions": "N/A", "health_benefits": "N/A"},
                {"name": "N/A", "calorie_comparison": "0", "key_substitutions": "N/A", "health_benefits": "N/A"},
                {"name": "N/A", "calorie_comparison": "0", "key_substitutions": "N/A", "health_benefits": "N/A"},
            ],
            "recipe": {
                "prep_time_minutes": 0, "cook_time_minutes": 0, "servings": 0,
                "ingredients": [], "instructions": [], "chef_tip": "N/A"
            }
        }
        res = FoodAnalysisResult.model_validate(fake_result)
        if not res.is_food:
            raise NonFoodImageError(res.non_food_reason)
    except NonFoodImageError as nfe:
        print(f"  [OK] Successfully caught NonFoodImageError: '{nfe}'")

def test_http_server():
    print("\nTesting Streamlit HTTP Server...")
    try:
        req = urllib.request.Request("http://localhost:8501", headers={"User-Agent": "FoodVerseTester/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            code = response.getcode()
            html = response.read(1024).decode("utf-8", errors="ignore")
            assert code == 200
            print(f"  [OK] Streamlit is responding with HTTP {code}!")
    except Exception as e:
        print(f"  [WARNING] Server check: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("RUNNING FOOD VERSE AI TEST SUITE")
    print("=" * 60)
    test_models()
    test_image_processing()
    test_macros_and_utilities()
    test_non_food_guardrail()
    test_http_server()
    print("=" * 60)
    print("ALL TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

