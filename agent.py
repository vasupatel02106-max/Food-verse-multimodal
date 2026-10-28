"""
Agent core for Food Verse AI.
Handles communication with Gemini multimodal models via google-genai SDK,
prompt engineering, structured JSON output validation via Pydantic,
retry logic, error classification, and conversational follow-ups.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional

from google import genai
from google.genai import types
from pydantic import ValidationError

from models import (
    FoodAnalysisResult,
    TextQueryResponse,
    ChatFollowUpResponse,
)
from utils import clean_json_string

logger = logging.getLogger("food_verse_agent")


class FoodVerseAgentException(Exception):
    """Base exception for Food Verse Agent."""
    pass


class ApiKeyMissingError(FoodVerseAgentException):
    """Raised when no Gemini API key is configured."""
    pass


class NonFoodImageError(FoodVerseAgentException):
    """Raised when an uploaded image is not food."""
    pass


class ModelGenerationError(FoodVerseAgentException):
    """Raised when Gemini fails after retries or returns unparsable output."""
    pass


def get_gemini_client(api_key: Optional[str] = None) -> genai.Client:
    """
    Initializes and returns a google-genai Client.
    Prioritizes passed api_key, then GEMINI_API_KEY, then GOOGLE_API_KEY.
    """
    effective_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not effective_key or not effective_key.strip():
        raise ApiKeyMissingError(
            "Gemini API key is missing. Please provide your API key in the sidebar or set GEMINI_API_KEY in your .env file."
        )
    return genai.Client(api_key=effective_key.strip())


def analyze_food_image(
    image_bytes: bytes,
    mime_type: str = "image/jpeg",
    api_key: Optional[str] = None,
    model_name: str = "gemini-2.5-flash",
) -> FoodAnalysisResult:
    """
    Analyzes an uploaded food photo using Gemini multimodal vision.
    Returns a validated FoodAnalysisResult Pydantic object.
    Retries once if JSON parsing or model validation fails.
    Raises NonFoodImageError if image is determined to be non-edible.
    """
    client = get_gemini_client(api_key)

    image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

    system_prompt = (
        "You are Food Verse AI, a world-class multimodal food intelligence agent, certified clinical nutritionist, "
        "and master culinary scientist. You analyze food photographs with precision and scientific rigour.\n\n"
        "INSTRUCTIONS:\n"
        "1. FIRST, inspect whether the image contains recognizable food, a cooked dish, fresh produce, snack, or edible item.\n"
        "   - If the image is NOT food (e.g., electronic gadgets, documents, furniture, pets, vehicles, blank backgrounds, "
        "     or non-edible objects), set 'is_food' to FALSE, specify a clear polite explanation in 'non_food_reason', "
        "     and fill remaining fields with placeholder values.\n"
        "2. If the image IS food:\n"
        "   - Set 'is_food' to TRUE and 'non_food_reason' to null.\n"
        "   - Accurately identify dish name, regional cuisine, confidence score (0.0 to 1.0), appetizing description, "
        "     and list of all prominent ingredients visible or customary in this dish.\n"
        "   - Estimate realistic per-serving nutrition: calories (kcal), protein (g), carbohydrates (g), fat (g), "
        "     fiber (g), sugar (g), sodium (mg), serving size, and an overall health score (1 to 10) with a 1-line reason.\n"
        "   - Categorize dietary status ('Vegetarian', 'Vegan', 'Non-Vegetarian', 'Pescatarian', etc.) and flag all potential "
        "     allergens (Dairy, Gluten, Tree Nuts, Peanuts, Eggs, Soy, Shellfish, Fish, Sesame, etc.) with a helpful warning.\n"
        "   - Provide exactly 3 creative, practical healthier alternatives or smart substitutions with calorie differences.\n"
        "   - Provide an authentic, easy-to-follow home recipe with prep time, cook time, difficulty, ingredients with quantities, "
        "     step-by-step instructions, and a pro chef tip.\n\n"
        "CRITICAL: Output must strictly conform to the JSON schema."
    )

    max_attempts = 2
    last_exception = None

    for attempt in range(max_attempts):
        try:
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=FoodAnalysisResult,
                temperature=0.2 if attempt == 0 else 0.4,
            )

            prompt_text = (
                "Please analyze this food photo comprehensively according to the schema."
                if attempt == 0
                else "Please re-analyze this food photo. Make sure to return strictly valid JSON conforming to the FoodAnalysisResult schema."
            )

            response = client.models.generate_content(
                model=model_name,
                contents=[prompt_text, image_part],
                config=config,
            )

            raw_text = response.text or ""
            cleaned = clean_json_string(raw_text)
            parsed_data = json.loads(cleaned)
            result = FoodAnalysisResult.model_validate(parsed_data)

            # Check for non-food detection
            if not result.is_food:
                reason = result.non_food_reason or "This doesn't look like food. Please upload an image of a meal, snack, or ingredient."
                raise NonFoodImageError(reason)

            return result

        except NonFoodImageError:
            # Re-raise immediately, do not retry non-food detection
            raise
        except (json.JSONDecodeError, ValidationError) as parse_err:
            logger.warning(f"Attempt {attempt + 1} validation failed: {parse_err}")
            last_exception = parse_err
            if attempt == max_attempts - 1:
                raise ModelGenerationError(
                    f"Failed to generate structured food analysis after {max_attempts} attempts: {str(parse_err)}"
                ) from parse_err
        except Exception as e:
            logger.error(f"Error during Gemini API call (attempt {attempt + 1}): {e}")
            last_exception = e
            if attempt == max_attempts - 1:
                # Provide a clean, human-readable error
                msg = str(e)
                if "API_KEY_INVALID" in msg or "400" in msg and "API key" in msg:
                    raise ApiKeyMissingError("Your Gemini API key appears invalid or expired. Please check your key.")
                if "RESOURCE_EXHAUSTED" in msg or "429" in msg:
                    raise ModelGenerationError("Gemini API rate limit or quota exceeded. Please wait a moment or try another model.")
                raise ModelGenerationError(f"Gemini API request failed: {msg}") from e

    raise ModelGenerationError(f"Analysis failed: {last_exception}")


def recommend_dishes_from_query(
    query: str,
    api_key: Optional[str] = None,
    model_name: str = "gemini-2.5-flash",
) -> TextQueryResponse:
    """
    Generates structured meal recommendations based on a user's dietary,
    calorie, or nutritional text query (e.g. 'high-protein vegetarian dinner under 500 calories').
    Retries once if parsing fails.
    """
    client = get_gemini_client(api_key)

    system_prompt = (
        "You are Food Verse AI, an expert culinary dietitian and chef. "
        "You provide personalized, appetizing, and nutritionally verified meal recommendations "
        "matching user dietary preferences, macronutrient goals, calorie restrictions, and cuisines.\n\n"
        "INSTRUCTIONS:\n"
        "1. Recommend at least 3 distinct, delicious dishes that satisfy the user's query.\n"
        "2. For each dish provide accurate macronutrients per serving, health score (1-10) with reason, "
        "   diet category, allergens, key ingredients, and 3-4 quick recipe steps.\n"
        "3. Provide an insightful summary explaining how these recommendations hit the user's targets.\n"
        "CRITICAL: Return strictly valid JSON conforming to TextQueryResponse schema."
    )

    max_attempts = 2
    last_exception = None

    for attempt in range(max_attempts):
        try:
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=TextQueryResponse,
                temperature=0.3 if attempt == 0 else 0.5,
            )

            prompt_text = f"USER QUERY: {query}\nProvide at least 3 recommendations that fit this request."

            response = client.models.generate_content(
                model=model_name,
                contents=[prompt_text],
                config=config,
            )

            raw_text = response.text or ""
            cleaned = clean_json_string(raw_text)
            parsed_data = json.loads(cleaned)
            return TextQueryResponse.model_validate(parsed_data)

        except (json.JSONDecodeError, ValidationError) as parse_err:
            logger.warning(f"Query attempt {attempt + 1} validation failed: {parse_err}")
            last_exception = parse_err
            if attempt == max_attempts - 1:
                raise ModelGenerationError(
                    f"Failed to generate structured recommendations: {str(parse_err)}"
                ) from parse_err
        except Exception as e:
            logger.error(f"Error during query recommendations: {e}")
            last_exception = e
            if attempt == max_attempts - 1:
                msg = str(e)
                if "API_KEY_INVALID" in msg or "400" in msg and "API key" in msg:
                    raise ApiKeyMissingError("Your Gemini API key appears invalid or expired. Please check your key.")
                if "RESOURCE_EXHAUSTED" in msg or "429" in msg:
                    raise ModelGenerationError("Gemini API rate limit or quota exceeded. Please wait a moment or try another model.")
                raise ModelGenerationError(f"Recommendation search failed: {msg}") from e

    raise ModelGenerationError(f"Search failed: {last_exception}")


def chat_about_dish(
    chat_history: List[Dict[str, str]],
    dish_context: FoodAnalysisResult,
    user_message: str,
    api_key: Optional[str] = None,
    model_name: str = "gemini-2.5-flash",
) -> ChatFollowUpResponse:
    """
    Handles conversational follow-up questions about an analyzed dish,
    grounding answers in the previously extracted nutritional, allergen, and recipe data.
    """
    client = get_gemini_client(api_key)

    context_summary = (
        f"CURRENT DISH ANALYSIS CONTEXT:\n"
        f"- Dish: {dish_context.dish_name} ({dish_context.cuisine})\n"
        f"- Description: {dish_context.description}\n"
        f"- Main Ingredients: {', '.join(dish_context.main_ingredients)}\n"
        f"- Nutrition: {dish_context.nutrition.calories} kcal | Protein: {dish_context.nutrition.protein_g}g | "
        f"Carbs: {dish_context.nutrition.carbs_g}g | Fat: {dish_context.nutrition.fat_g}g | Fiber: {dish_context.nutrition.fiber_g}g\n"
        f"- Health Score: {dish_context.nutrition.health_score}/10 ({dish_context.nutrition.health_score_reason})\n"
        f"- Diet Category: {dish_context.diet_and_allergens.diet_category}\n"
        f"- Allergens: {', '.join(dish_context.diet_and_allergens.allergens) or 'None'}\n"
        f"- Chef Tip: {dish_context.recipe.chef_tip}\n"
    )

    system_prompt = (
        "You are Food Verse AI, a helpful culinary assistant and nutritionist.\n"
        "You are answering a user's follow-up question regarding the specific dish described below.\n\n"
        f"{context_summary}\n"
        "GUIDELINES:\n"
        "1. Give a direct, practical, and enthusiastic response formatted in rich markdown with bullet points or bold text.\n"
        "2. Directly address their questions (e.g. substitutions, meal prep tips, wine pairings, calorie cutting, allergy workarounds).\n"
        "3. Provide 2-3 smart, concise suggested follow-up questions they might want to ask next in 'suggested_followups'.\n"
        "CRITICAL: Output must conform to ChatFollowUpResponse schema."
    )

    conversation_contents = []
    # Include up to last 6 chat turns for context
    recent_history = chat_history[-6:] if len(chat_history) > 6 else chat_history
    for turn in recent_history:
        role = turn.get("role", "user")
        text = turn.get("content", "")
        if role == "user":
            conversation_contents.append(f"User: {text}")
        else:
            conversation_contents.append(f"Assistant: {text}")

    conversation_contents.append(f"User: {user_message}")
    full_prompt = "\n".join(conversation_contents)

    try:
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            response_schema=ChatFollowUpResponse,
            temperature=0.3,
        )

        response = client.models.generate_content(
            model=model_name,
            contents=[full_prompt],
            config=config,
        )

        raw_text = response.text or ""
        cleaned = clean_json_string(raw_text)
        parsed = json.loads(cleaned)
        return ChatFollowUpResponse.model_validate(parsed)

    except Exception as e:
        logger.warning(f"Structured chat parse failed ({e}), attempting fallback text generation")
        # Fallback to standard chat response if structured parsing encounters an edge case
        try:
            fallback_response = client.models.generate_content(
                model=model_name,
                contents=[system_prompt + "\n\n" + full_prompt],
            )
            return ChatFollowUpResponse(
                answer=fallback_response.text or "Here is what I found regarding your question.",
                suggested_followups=[
                    "Can you suggest a side dish for this?",
                    "How long can I store leftovers in the fridge?",
                ],
            )
        except Exception as fallback_err:
            raise ModelGenerationError(f"Chat failed: {str(fallback_err)}") from fallback_err
