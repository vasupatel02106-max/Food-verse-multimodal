"""
Pydantic schemas for Food Verse AI - Multimodal Food Intelligence Agent.
Provides strongly typed models for food analysis, nutrition, allergens,
smart suggestions, recipes, text query recommendations, and chat follow-ups.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class NutritionInfo(BaseModel):
    """Nutritional breakdown and health score per serving."""
    serving_size: str = Field(..., description="Estimated serving size (e.g. '1 bowl (approx. 320g)')")
    calories: int = Field(..., description="Total estimated calories (kcal) per serving")
    protein_g: float = Field(..., description="Grams of protein per serving")
    carbs_g: float = Field(..., description="Grams of total carbohydrates per serving")
    fat_g: float = Field(..., description="Grams of total fats per serving")
    fiber_g: Optional[float] = Field(default=0.0, description="Grams of dietary fiber per serving")
    sugar_g: Optional[float] = Field(default=0.0, description="Grams of sugar per serving")
    sodium_mg: Optional[float] = Field(default=0.0, description="Milligrams of sodium per serving")
    health_score: int = Field(..., ge=1, le=10, description="Overall healthiness score from 1 (unhealthy) to 10 (exceptionally wholesome)")
    health_score_reason: str = Field(..., description="Concise one-line justification for the health score")


class DietAndAllergens(BaseModel):
    """Dietary categorization and allergen alerts."""
    diet_category: str = Field(..., description="Primary dietary classification: 'Vegetarian', 'Vegan', 'Non-Vegetarian', 'Pescatarian', or 'Eggetarian'")
    is_vegetarian: bool = Field(..., description="True if free of meat, poultry, and seafood")
    is_vegan: bool = Field(..., description="True if entirely free of animal products including dairy and honey")
    is_gluten_free: bool = Field(..., description="True if naturally gluten-free or typically prepared without gluten")
    is_dairy_free: bool = Field(..., description="True if prepared without milk, butter, cheese, or cream")
    allergens: List[str] = Field(default_factory=list, description="Common food allergens detected (e.g. 'Dairy', 'Gluten', 'Tree Nuts', 'Peanuts', 'Soy', 'Eggs', 'Shellfish', 'Fish', 'Sesame')")
    allergen_warning: str = Field(..., description="Helpful warning summary explaining potential allergen triggers or cross-contact notes")


class HealthierAlternative(BaseModel):
    """A healthier variation or substitution for the dish."""
    name: str = Field(..., description="Name of the healthier alternative dish or modification")
    calorie_comparison: str = Field(..., description="Estimated calories or difference (e.g. '310 kcal (-170 kcal)')")
    key_substitutions: str = Field(..., description="Core ingredient swaps made (e.g. 'Cauliflower mash for potatoes, Greek yogurt for sour cream')")
    health_benefits: str = Field(..., description="Main health benefits gained (e.g. 'Higher fiber, lower glycemic index, 40% less saturated fat')")


class RecipeIngredient(BaseModel):
    """Individual ingredient with amount."""
    item: str = Field(..., description="Ingredient name (e.g. 'Extra Virgin Olive Oil')")
    amount: str = Field(..., description="Quantity and measurement (e.g. '2 tablespoons' or '200g')")
    notes: Optional[str] = Field(default="", description="Preparation notes like 'finely diced' or 'room temperature'")


class Recipe(BaseModel):
    """Simple, practical home recipe to prepare the dish."""
    prep_time_minutes: int = Field(..., description="Preparation time in minutes")
    cook_time_minutes: int = Field(..., description="Cooking or assembly time in minutes")
    servings: int = Field(default=2, description="Number of standard portions this recipe yields")
    difficulty: str = Field(default="Medium", description="Recipe difficulty: 'Easy', 'Medium', or 'Advanced'")
    ingredients: List[RecipeIngredient] = Field(..., description="List of required ingredients with amounts")
    instructions: List[str] = Field(..., description="Sequential step-by-step preparation and cooking instructions")
    chef_tip: str = Field(..., description="A professional culinary tip to elevate taste, texture, or nutrition")


class FoodAnalysisResult(BaseModel):
    """Complete multimodal food intelligence payload."""
    is_food: bool = Field(..., description="Set to true if image contains recognizable food, dish, or edible item. Set to false for non-food items.")
    non_food_reason: Optional[str] = Field(default=None, description="Explanation if image is not recognized as food")
    dish_name: str = Field(default="Unknown Dish", description="Accurate name of the identified dish")
    cuisine: str = Field(default="Global", description="Regional or culinary style (e.g. 'Italian', 'Mexican', 'South Indian', 'Mediterranean')")
    description: str = Field(default="", description="Enticing 1-2 sentence culinary summary of the dish")
    confidence_score: float = Field(default=0.9, ge=0.0, le=1.0, description="Model confidence in food identification (0.0 to 1.0)")
    main_ingredients: List[str] = Field(default_factory=list, description="List of prominent ingredients detected in the food item")
    nutrition: NutritionInfo = Field(..., description="Macronutrient and health score estimation")
    diet_and_allergens: DietAndAllergens = Field(..., description="Diet classification and allergen flags")
    healthier_alternatives: List[HealthierAlternative] = Field(..., description="Exactly 3 nutritious alternatives or smart ingredient swaps")
    recipe: Recipe = Field(..., description="Simple, authentic recipe to cook this dish at home")


class DishRecommendation(BaseModel):
    """A dish suggested from a free-text dietary or calorie query."""
    dish_name: str = Field(..., description="Name of recommended dish")
    cuisine: str = Field(..., description="Cuisine origin")
    calories: int = Field(..., description="Calories per serving")
    protein_g: float = Field(..., description="Protein grams")
    carbs_g: float = Field(..., description="Carbohydrates grams")
    fat_g: float = Field(..., description="Fat grams")
    health_score: int = Field(..., ge=1, le=10, description="Health score (1 to 10)")
    health_score_reason: str = Field(..., description="Why this dish fits the health score and query")
    diet_category: str = Field(..., description="'Vegetarian', 'Vegan', 'Non-Vegetarian', etc.")
    allergens: List[str] = Field(default_factory=list, description="Common allergens present")
    description: str = Field(..., description="Appetizing summary of why it fits the user's criteria")
    key_ingredients: List[str] = Field(default_factory=list, description="Primary ingredients used")
    quick_recipe_steps: List[str] = Field(default_factory=list, description="3-4 quick cooking steps")


class TextQueryResponse(BaseModel):
    """Structured response for text query mode recommendations."""
    query: str = Field(..., description="User's original search or dietary query")
    summary: str = Field(..., description="AI culinary and nutritional synthesis for the query")
    recommendations: List[DishRecommendation] = Field(..., description="List of at least 3 matching dish recommendations")


class ChatFollowUpResponse(BaseModel):
    """Structured response for follow-up chat conversations."""
    answer: str = Field(..., description="Direct, helpful culinary/nutritional response formatted in clean markdown")
    suggested_followups: List[str] = Field(default_factory=list, description="2-3 smart follow-up question chips the user might ask next")
