"""
Utility helpers for Food Verse AI.
Handles image processing, base64 encoding/decoding, JSON cleaning,
nutritional calculations, demo presets, and UI formatting.
"""

import io
import re
import base64
from typing import Tuple, Optional, Dict, Any
from PIL import Image, ImageDraw, ImageFont

from models import (
    FoodAnalysisResult,
    NutritionInfo,
    DietAndAllergens,
    HealthierAlternative,
    Recipe,
    RecipeIngredient,
    TextQueryResponse,
    DishRecommendation,
)


def process_image(image_file) -> Tuple[bytes, str, Image.Image]:
    """
    Process an uploaded file or PIL Image.
    Returns: (image_bytes, mime_type, pil_image)
    Normalizes orientation and resizes if larger than 1600x1600.
    """
    if isinstance(image_file, bytes):
        pil_img = Image.open(io.BytesIO(image_file))
        raw_bytes = image_file
    elif hasattr(image_file, "read"):
        raw_bytes = image_file.read()
        pil_img = Image.open(io.BytesIO(raw_bytes))
    elif isinstance(image_file, Image.Image):
        pil_img = image_file
        buf = io.BytesIO()
        pil_img.save(buf, format="JPEG", quality=90)
        raw_bytes = buf.getvalue()
    else:
        raise ValueError("Unsupported image input type")

    # Convert RGBA / P / CMYK to RGB for consistent JPEG encoding
    if pil_img.mode in ("RGBA", "P", "CMYK"):
        pil_img = pil_img.convert("RGB")

    # Resize if excessively large to keep payload snappy
    max_dim = 1600
    if pil_img.width > max_dim or pil_img.height > max_dim:
        pil_img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
        out_buf = io.BytesIO()
        pil_img.save(out_buf, format="JPEG", quality=88)
        raw_bytes = out_buf.getvalue()

    return raw_bytes, "image/jpeg", pil_img


def pil_to_base64(pil_img: Image.Image, max_thumb_size: Tuple[int, int] = (200, 200)) -> str:
    """Creates a lightweight base64 thumbnail string for session history."""
    thumb = pil_img.copy()
    thumb.thumbnail(max_thumb_size, Image.Resampling.LANCZOS)
    if thumb.mode in ("RGBA", "P"):
        thumb = thumb.convert("RGB")
    buf = io.BytesIO()
    thumb.save(buf, format="JPEG", quality=75)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def clean_json_string(raw_text: str) -> str:
    """
    Extracts raw JSON content from markdown code fences or conversational text.
    Handles ```json ... ``` blocks gracefully.
    """
    if not raw_text:
        return "{}"
    
    # Strip markdown block quotes or fences
    text = raw_text.strip()
    
    # Find ```json ... ```
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if match:
        text = match.group(1).strip()
    else:
        # Fallback: look for outermost curly braces { ... }
        first_brace = text.find("{")
        last_brace = text.rfind("}")
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            text = text[first_brace:last_brace + 1]

    return text


def calculate_macro_percentages(protein_g: float, carbs_g: float, fat_g: float) -> Tuple[int, int, int]:
    """
    Computes calorie percentages:
    Protein: 4 kcal/g, Carbs: 4 kcal/g, Fat: 9 kcal/g.
    Returns (protein_pct, carbs_pct, fat_pct).
    """
    p_cal = max(0.0, protein_g * 4.0)
    c_cal = max(0.0, carbs_g * 4.0)
    f_cal = max(0.0, fat_g * 9.0)
    total_cal = p_cal + c_cal + f_cal

    if total_cal <= 0:
        return 33, 33, 34

    p_pct = int(round((p_cal / total_cal) * 100))
    c_pct = int(round((c_cal / total_cal) * 100))
    f_pct = max(0, 100 - (p_pct + c_pct))
    return p_pct, c_pct, f_pct


def get_health_score_color(score: int) -> str:
    """Returns CSS hex color code based on health score."""
    if score >= 8:
        return "#10B981"  # Emerald Green
    elif score >= 5:
        return "#F59E0B"  # Amber Orange
    else:
        return "#EF4444"  # Rose Red


def create_demo_food_image(dish_name: str = "Avocado Toast") -> Image.Image:
    """Generates an attractive placeholder food badge graphic for offline demo/testing."""
    width, height = 640, 480
    img = Image.new("RGB", (width, height), color="#1E293B")
    draw = ImageDraw.Draw(img)

    # Gradient background simulation
    for y in range(height):
        r = int(18 + (34 - 18) * (y / height))
        g = int(30 + (50 - 30) * (y / height))
        b = int(49 + (80 - 49) * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Center plate circle
    draw.ellipse([140, 60, 500, 420], fill="#0F172A", outline="#10B981", width=4)
    draw.ellipse([170, 90, 470, 390], fill="#1E293B", outline="#334155", width=2)

    # Food accent shapes (stylized avocado / toast)
    draw.rounded_rectangle([210, 160, 430, 320], radius=20, fill="#78350F", outline="#92400E", width=3)
    draw.ellipse([230, 180, 410, 300], fill="#65A30D")
    draw.ellipse([290, 210, 350, 270], fill="#FACC15")  # Poached egg yolk

    # Title Banner
    draw.text((width // 2 - 130, 25), "FOOD VERSE AI DEMO", fill="#E2E8F0")
    draw.text((width // 2 - 100, 435), f"{dish_name}", fill="#38BDF8")

    return img


def get_sample_analysis_presets() -> Dict[str, Dict[str, Any]]:
    """
    Returns rich, curated food intelligence presets for instant demonstration,
    testing without API key, or rapid validation.
    """
    presets = {
        "Mediterranean Grilled Salmon Bowl": {
            "is_food": True,
            "non_food_reason": None,
            "dish_name": "Mediterranean Grilled Salmon Bowl",
            "cuisine": "Mediterranean Fusion",
            "description": "Wild-caught grilled salmon fillet resting over fluffy quinoa, crisp Persian cucumbers, kalamata olives, cherry tomatoes, and creamy lemon-tahini drizzle.",
            "confidence_score": 0.98,
            "main_ingredients": [
                "Wild Atlantic Salmon",
                "Tri-color Quinoa",
                "Cherry Tomatoes",
                "Persian Cucumbers",
                "Kalamata Olives",
                "Baby Spinach",
                "Tahini & Lemon Dressing",
                "Extra Virgin Olive Oil"
            ],
            "nutrition": {
                "serving_size": "1 deep bowl (approx. 380g)",
                "calories": 520,
                "protein_g": 42.0,
                "carbs_g": 36.0,
                "fat_g": 22.0,
                "fiber_g": 7.0,
                "sugar_g": 4.5,
                "sodium_mg": 460.0,
                "health_score": 9,
                "health_score_reason": "Superb balance of lean omega-3 fatty acids, complete plant proteins, and dense micronutrients with low refined carbs."
            },
            "diet_and_allergens": {
                "diet_category": "Pescatarian",
                "is_vegetarian": False,
                "is_vegan": False,
                "is_gluten_free": True,
                "is_dairy_free": True,
                "allergens": ["Fish", "Sesame"],
                "allergen_warning": "Contains salmon (finfish) and tahini (sesame seeds). Naturally gluten-free and dairy-free."
            },
            "healthier_alternatives": [
                {
                    "name": "Keto Cauliflower Salmon Bowl",
                    "calorie_comparison": "410 kcal (-110 kcal)",
                    "key_substitutions": "Swap tri-color quinoa for seasoned riced cauliflower",
                    "health_benefits": "Drastically reduces net carbs to under 8g while preserving all healthy omega-3s and protein."
                },
                {
                    "name": "Plant-Powered Tempeh Bowl",
                    "calorie_comparison": "460 kcal (-60 kcal)",
                    "key_substitutions": "Replace salmon with grilled organic smoked tempeh cutlets",
                    "health_benefits": "100% plant-based cholesterol-free protein with added prebiotic gut-health benefits."
                },
                {
                    "name": "Light Herb-Vinaigrette Salmon Bowl",
                    "calorie_comparison": "440 kcal (-80 kcal)",
                    "key_substitutions": "Swap creamy tahini dressing for fresh lemon-dill vinaigrette",
                    "health_benefits": "Cuts 10g of total fat and boosts bioavailable Vitamin C."
                }
            ],
            "recipe": {
                "prep_time_minutes": 15,
                "cook_time_minutes": 15,
                "servings": 2,
                "difficulty": "Easy",
                "ingredients": [
                    {"item": "Salmon Fillets (skin-on)", "amount": "2 fillets (150g each)", "notes": "wild-caught preferred"},
                    {"item": "Quinoa", "amount": "1 cup dry", "notes": "rinsed and cooked in vegetable broth"},
                    {"item": "Cherry Tomatoes", "amount": "1 cup", "notes": "halved"},
                    {"item": "Persian Cucumbers", "amount": "2 medium", "notes": "sliced into half-moons"},
                    {"item": "Kalamata Olives", "amount": "1/3 cup", "notes": "pitted and sliced"},
                    {"item": "Tahini Paste", "amount": "2 tablespoons", "notes": "whisked with 2 tbsp warm water and 1 tbsp lemon juice"},
                    {"item": "Extra Virgin Olive Oil", "amount": "1 tablespoon", "notes": "for searing salmon"},
                    {"item": "Sea Salt & Fresh Pepper", "amount": "To taste", "notes": "cracked"}
                ],
                "instructions": [
                    "Cook quinoa in vegetable broth or salted water according to package directions (approx. 15 minutes), then fluff with a fork.",
                    "Pat salmon fillets dry with paper towels. Season generously with sea salt, black pepper, and oregano.",
                    "Heat olive oil in a cast-iron skillet over medium-high heat. Place salmon skin-side down and sear for 4-5 minutes until crispy. Flip and cook for another 3 minutes.",
                    "In a small ramekin, whisk tahini, fresh lemon juice, minced garlic, a pinch of salt, and warm water until velvety smooth.",
                    "Assemble bowls: layer a warm base of quinoa, arranged with halved cherry tomatoes, cucumber slices, olives, and fresh greens.",
                    "Rest the seared salmon fillet right on top and drizzle generously with the golden lemon-tahini dressing. Garnish with chopped fresh dill."
                ],
                "chef_tip": "For ultra-crispy salmon skin, ensure the skin is thoroughly dry and sear undisturbed on medium-high heat before flipping."
            }
        },
        "Artisanal Avocado Sourdough Toast": {
            "is_food": True,
            "non_food_reason": None,
            "dish_name": "Artisanal Avocado Sourdough Toast with Soft Poached Egg",
            "cuisine": "Modern Californian / Brunch",
            "description": "Toasted rustic whole grain sourdough spread with creamy Hass avocado mash, topped with a farm-fresh soft poached egg, chili flakes, and microgreens.",
            "confidence_score": 0.99,
            "main_ingredients": [
                "Artisan Sourdough Bread",
                "Ripe Hass Avocado",
                "Pasture-Raised Egg",
                "Chili Flakes",
                "Microgreens",
                "Extra Virgin Olive Oil",
                "Flaky Sea Salt"
            ],
            "nutrition": {
                "serving_size": "2 loaded toast slices (approx. 240g)",
                "calories": 420,
                "protein_g": 18.0,
                "carbs_g": 38.0,
                "fat_g": 22.0,
                "fiber_g": 9.5,
                "sugar_g": 2.0,
                "sodium_mg": 380.0,
                "health_score": 9,
                "health_score_reason": "High in heart-healthy monounsaturated fats, gut-friendly sourdough fermentation, and bioavailable lutein & choline from pastured egg."
            },
            "diet_and_allergens": {
                "diet_category": "Eggetarian / Vegetarian",
                "is_vegetarian": True,
                "is_vegan": False,
                "is_gluten_free": False,
                "is_dairy_free": True,
                "allergens": ["Gluten", "Eggs"],
                "allergen_warning": "Contains wheat gluten (sourdough) and whole eggs. Dairy-free naturally."
            },
            "healthier_alternatives": [
                {
                    "name": "Gluten-Free Sweet Potato Toast",
                    "calorie_comparison": "330 kcal (-90 kcal)",
                    "key_substitutions": "Use toasted thick sweet potato planks instead of wheat sourdough",
                    "health_benefits": "Naturally grain-free, loaded with beta-carotene and Vitamin A."
                },
                {
                    "name": "High-Protein Cottage Cheese Avocado Toast",
                    "calorie_comparison": "390 kcal (+12g Protein)",
                    "key_substitutions": "Layer 1/3 cup whipped low-fat cottage cheese beneath the avocado mash",
                    "health_benefits": "Doubles the protein content for superior post-workout muscle repair and sustained fullness."
                },
                {
                    "name": "Vegan Tofu Scramble Avocado Toast",
                    "calorie_comparison": "380 kcal (Zero Cholesterol)",
                    "key_substitutions": "Swap the poached egg for seasoned turmeric-black salt scrambled tofu",
                    "health_benefits": "Completely plant-based and cruelty-free with identical protein profile."
                }
            ],
            "recipe": {
                "prep_time_minutes": 8,
                "cook_time_minutes": 6,
                "servings": 1,
                "difficulty": "Easy",
                "ingredients": [
                    {"item": "Rustic Sourdough Bread", "amount": "2 thick slices", "notes": "artisan boule"},
                    {"item": "Hass Avocado", "amount": "1 ripe", "notes": "mashed with 1 tsp lemon juice"},
                    {"item": "Egg", "amount": "1 large", "notes": "fresh pasture-raised"},
                    {"item": "Red Pepper Flakes", "amount": "1/2 teaspoon", "notes": "coarsely ground"},
                    {"item": "Microgreens or Radish Sprouts", "amount": "Handful", "notes": "washed"},
                    {"item": "Flaky Sea Salt (Maldon)", "amount": "To taste", "notes": "finishing salt"}
                ],
                "instructions": [
                    "Toast the sourdough slices until deeply golden and crunch-crisp.",
                    "In a bowl, coarsely fork-mash the ripe avocado with lemon juice, sea salt, and black pepper.",
                    "Bring a small pot of water to a gentle simmer with 1 tbsp white vinegar. Swirl to create a whirlpool and gently drop in the cracked egg. Poach for 3 minutes until white is set and yolk is runny.",
                    "Spread generous spoonfuls of avocado mash over each toasted slice.",
                    "Top with the warm poached egg, sprinkle with red chili flakes, cracked black pepper, flaky sea salt, and a bouquet of fresh microgreens."
                ],
                "chef_tip": "Add a few drops of white vinegar to your poaching water; it helps the egg white coagulate smoothly without feathering."
            }
        },
        "Traditional Vegetable Biryani": {
            "is_food": True,
            "non_food_reason": None,
            "dish_name": "Dum Vegetable Biryani with Raita",
            "cuisine": "Indian / Mughlai",
            "description": "Fragrant basmati rice layered with spiced cauliflower florets, carrots, french beans, mint, caramelized onions, and saffron milk.",
            "confidence_score": 0.97,
            "main_ingredients": [
                "Aged Basmati Rice",
                "Cauliflower",
                "Green Beans & Carrots",
                "Fried Onions (Birista)",
                "Fresh Mint & Coriander",
                "Saffron Infused Milk",
                "Biryani Masala Spices",
                "Desi Ghee"
            ],
            "nutrition": {
                "serving_size": "1 plate with raita (approx. 350g)",
                "calories": 490,
                "protein_g": 12.5,
                "carbs_g": 72.0,
                "fat_g": 16.0,
                "fiber_g": 6.8,
                "sugar_g": 5.0,
                "sodium_mg": 520.0,
                "health_score": 7,
                "health_score_reason": "Vibrant antioxidant-rich spices (turmeric, saffron, cloves) and fiber from vegetables, though carb-heavy due to polished basmati rice."
            },
            "diet_and_allergens": {
                "diet_category": "Vegetarian",
                "is_vegetarian": True,
                "is_vegan": False,
                "is_gluten_free": True,
                "is_dairy_free": False,
                "allergens": ["Dairy"],
                "allergen_warning": "Contains dairy products (ghee, saffron milk, yogurt raita). Naturally gluten-free."
            },
            "healthier_alternatives": [
                {
                    "name": "Brown Rice & Quinoa Dum Biryani",
                    "calorie_comparison": "390 kcal (-100 kcal)",
                    "key_substitutions": "Swap white basmati rice for 50/50 brown basmati rice and quinoa",
                    "health_benefits": "Cuts glycemic spike significantly and provides double the dietary fiber."
                },
                {
                    "name": "High-Protein Paneer & Soya Biryani",
                    "calorie_comparison": "480 kcal (+18g Protein)",
                    "key_substitutions": "Incorporate pan-seared low-fat paneer cubes and soya chunks into vegetable layers",
                    "health_benefits": "Transforms a carb-dominant dish into an exceptional muscle-building vegetarian meal."
                },
                {
                    "name": "Cauliflower Rice Low-Carb Biryani",
                    "calorie_comparison": "260 kcal (-230 kcal)",
                    "key_substitutions": "Use coarse riced cauliflower steamed with biryani spices instead of grain rice",
                    "health_benefits": "Cuts carbohydrates by over 75% for keto or diabetic-conscious diets."
                }
            ],
            "recipe": {
                "prep_time_minutes": 25,
                "cook_time_minutes": 30,
                "servings": 4,
                "difficulty": "Medium",
                "ingredients": [
                    {"item": "Aged Basmati Rice", "amount": "1.5 cups", "notes": "soaked for 30 minutes"},
                    {"item": "Mixed Vegetables (Cauliflower, Carrots, Peas)", "amount": "2.5 cups", "notes": "diced"},
                    {"item": "Plain Greek Yogurt or Dahi", "amount": "1/2 cup", "notes": "whisked with spices"},
                    {"item": "Biryani Masala & Garam Masala", "amount": "2 tablespoons", "notes": "freshly ground"},
                    {"item": "Fried Onions", "amount": "1 cup", "notes": "golden crisp"},
                    {"item": "Mint and Cilantro Leaves", "amount": "1 cup", "notes": "finely chopped"},
                    {"item": "Ghee or Olive Oil", "amount": "2 tablespoons", "notes": ""},
                    {"item": "Saffron Strands in Warm Milk", "amount": "3 tablespoons", "notes": "fragrant infusion"}
                ],
                "instructions": [
                    "Par-boil soaked basmati rice in salted water with whole spices (cinnamon, cloves, cardamom) until 70% cooked (approx. 5 mins). Drain.",
                    "In a heavy-bottom Dutch oven, sauté onions, ginger-garlic paste, diced vegetables, and biryani spices with yogurt until tender-crisp.",
                    "Layer half of the partially cooked rice over the spiced vegetables. Scatter fresh mint, cilantro, and golden fried onions.",
                    "Add remaining rice layer, drizzle warm saffron milk and a spoonful of ghee over the top.",
                    "Seal with a tight lid or aluminum foil ('dum' method) and cook on lowest flame for 20 minutes to trap the aromatic steam.",
                    "Let rest for 5 minutes, gently fluff with a flat spatula, and serve piping hot with cucumber mint raita."
                ],
                "chef_tip": "Never stir biryani aggressively; use a flat plate or broad spatula from the edges to keep rice grains intact and aromatic."
            }
        }
    }
    return presets


def get_preset_as_model(preset_name: str) -> Optional[FoodAnalysisResult]:
    """Helper to load a preset as a valid FoodAnalysisResult Pydantic object."""
    presets = get_sample_analysis_presets()
    if preset_name in presets:
        return FoodAnalysisResult.model_validate(presets[preset_name])
    return None
