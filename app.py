"""
Food Verse AI – Multimodal Food Intelligence Agent
A modern Streamlit application providing multimodal food analysis,
nutrition breakdown, allergen safety checks, smart recipe suggestions,
text query meal discovery, and grounded conversational follow-ups.
"""

import os
import time
from datetime import datetime
from typing import Optional, List, Dict, Any
from PIL import Image
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()

from models import (
    FoodAnalysisResult,
    TextQueryResponse,
    ChatFollowUpResponse,
)
from utils import (
    process_image,
    pil_to_base64,
    calculate_macro_percentages,
    get_health_score_color,
    get_sample_analysis_presets,
    get_preset_as_model,
)
from agent import (
    analyze_food_image,
    recommend_dishes_from_query,
    chat_about_dish,
    ApiKeyMissingError,
    NonFoodImageError,
    ModelGenerationError,
)

# Page Configuration
st.set_page_config(
    page_title="Food Verse AI – Multimodal Food Intelligence",
    page_icon="🥑",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Design System CSS
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Outfit:wght@500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

h1, h2, h3, h4 {
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
}

/* Hero Branding */
.hero-container {
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F2D25 100%);
    border: 1px solid rgba(16, 185, 129, 0.25);
    border-radius: 20px;
    padding: 2.2rem 2.4rem;
    margin-bottom: 2rem;
    box-shadow: 0 12px 30px -10px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.hero-title {
    font-size: 2.4rem;
    font-weight: 800;
    background: linear-gradient(90deg, #38BDF8, #34D399, #FACC15);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
}

.hero-subtitle {
    color: #94A3B8;
    font-size: 1.05rem;
    line-height: 1.6;
    margin-bottom: 1.2rem;
}

.hero-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem;
}

.hero-pill {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.12);
    color: #E2E8F0;
    padding: 0.35rem 0.85rem;
    border-radius: 50px;
    font-size: 0.82rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}

/* Card Containers */
.fv-card {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
    transition: transform 0.2s ease, border-color 0.2s ease;
}

.fv-card:hover {
    border-color: rgba(56, 189, 248, 0.4);
}

.fv-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.2rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    padding-bottom: 0.8rem;
}

.fv-card-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: #F8FAFC;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 0;
}

/* Nutrition Metrics Grid */
.macro-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.8rem;
    margin-bottom: 1.2rem;
}

.macro-box {
    background: rgba(15, 23, 42, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 1rem 0.6rem;
    text-align: center;
}

.macro-label {
    font-size: 0.75rem;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 600;
    margin-bottom: 0.3rem;
}

.macro-val {
    font-size: 1.5rem;
    font-weight: 800;
    color: #F8FAFC;
}

.macro-unit {
    font-size: 0.8rem;
    color: #64748B;
    font-weight: 500;
}

/* Health Score Badge */
.score-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 68px;
    height: 68px;
    border-radius: 50%;
    font-size: 1.8rem;
    font-weight: 800;
    box-shadow: 0 0 20px rgba(16, 185, 129, 0.25);
}

/* Pills & Tags */
.ingredient-tag {
    display: inline-block;
    background: rgba(56, 189, 248, 0.12);
    border: 1px solid rgba(56, 189, 248, 0.3);
    color: #7DD3FC;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.82rem;
    margin: 0.2rem;
    font-weight: 500;
}

.allergen-pill {
    display: inline-block;
    background: rgba(239, 68, 68, 0.15);
    border: 1px solid rgba(239, 68, 68, 0.4);
    color: #FCA5A5;
    padding: 0.3rem 0.85rem;
    border-radius: 20px;
    font-size: 0.85rem;
    margin: 0.25rem;
    font-weight: 600;
}

.diet-pill {
    display: inline-block;
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.4);
    color: #6EE7B7;
    padding: 0.35rem 0.95rem;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: 700;
}

/* Macro Bar */
.macro-bar-container {
    height: 12px;
    width: 100%;
    background: #0F172A;
    border-radius: 6px;
    display: flex;
    overflow: hidden;
    margin: 0.8rem 0;
}

/* Alternatives Box */
.alt-card {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 1.1rem;
    margin-bottom: 0.8rem;
    border-left: 4px solid #10B981;
}

/* History item */
.history-card {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 0.8rem;
    margin-bottom: 0.8rem;
}

/* Chat bubble styling */
.chat-ai {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 0.8rem;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# Initialize Session State
def init_session_state():
    if "history" not in st.session_state:
        st.session_state["history"] = []
    if "current_analysis" not in st.session_state:
        st.session_state["current_analysis"] = None
    if "current_image" not in st.session_state:
        st.session_state["current_image"] = None
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    if "text_results" not in st.session_state:
        st.session_state["text_results"] = None
    if "api_key" not in st.session_state:
        st.session_state["api_key"] = os.environ.get("GEMINI_API_KEY", "")
    if "model_name" not in st.session_state:
        st.session_state["model_name"] = "gemini-2.5-flash"

init_session_state()


# Sidebar Navigation & Settings
with st.sidebar:
    st.markdown("### 🥑 Food Verse AI")
    st.caption("Multimodal Culinary & Nutritional Intelligence")
    st.divider()

    # API Key Configuration
    st.markdown("#### 🔑 Gemini API Key")
    saved_key = st.session_state.get("api_key", "")
    has_env_key = bool(os.environ.get("GEMINI_API_KEY"))

    api_key_input = st.text_input(
        "API Key",
        value=saved_key,
        type="password",
        placeholder="Paste your Gemini API key...",
        help="Get your key for free from https://aistudio.google.com/app/apikey",
    )

    if api_key_input != saved_key:
        st.session_state["api_key"] = api_key_input
        st.rerun()

    if st.session_state["api_key"]:
        st.success("✅ API Key configured", icon="🛡️")
    else:
        st.warning("⚠️ No API Key found. You can paste your key above, or use **Demo Mode** to test presets immediately!", icon="💡")

    # Model Selection
    selected_model = st.selectbox(
        "Gemini Model",
        options=["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"],
        index=0,
        help="gemini-2.5-flash provides the fastest and most accurate multimodal reasoning.",
    )
    st.session_state["model_name"] = selected_model

    st.divider()

    # Session History Section
    st.markdown(f"#### 📜 Session History ({len(st.session_state['history'])})")
    
    if st.session_state["history"]:
        if st.button("🗑️ Clear All History", use_container_width=True):
            st.session_state["history"] = []
            st.session_state["current_analysis"] = None
            st.session_state["chat_history"] = []
            st.rerun()

        for idx, item in enumerate(reversed(st.session_state["history"])):
            with st.container():
                cols = st.columns([1, 2.5])
                with cols[0]:
                    if item.get("thumb_b64"):
                        st.markdown(
                            f'<img src="data:image/jpeg;base64,{item["thumb_b64"]}" style="width:100%; border-radius:8px; aspect-ratio:1; object-fit:cover;"/>',
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown("🍽️")
                with cols[1]:
                    st.markdown(f"**{item['dish_name']}**")
                    st.caption(f"{item.get('calories', 'N/A')} kcal · {item.get('timestamp', '')}")
                    if st.button("View", key=f"hist_btn_{len(st.session_state['history']) - 1 - idx}", use_container_width=True):
                        st.session_state["current_analysis"] = item["analysis"]
                        st.session_state["current_image"] = item.get("image")
                        st.session_state["chat_history"] = item.get("chat_history", [])
                        st.rerun()
                st.markdown("<hr style='margin: 0.5rem 0; border-color: #334155;'/>", unsafe_allow_html=True)
    else:
        st.info("No past analyses yet. Upload an image or run a demo to populate your history!", icon="🌱")

    st.divider()
    st.caption("Powered by Google Gemini 2.5 Flash & Streamlit")


# Header Hero Section
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🥑 Food Verse AI</div>
    <div class="hero-subtitle">
        Your multimodal food intelligence agent. Snap or upload any food photo to reveal deep nutritional breakdowns, 
        allergen alerts, culinary secrets, healthier substitutions, and grounded chat guidance powered by Gemini Multimodal AI.
    </div>
    <div class="hero-badges">
        <span class="hero-pill">⚡ Gemini 2.5 Multimodal</span>
        <span class="hero-pill">🔬 Deep Macro & Micro Breakdown</span>
        <span class="hero-pill">🛡️ Allergen Guard</span>
        <span class="hero-pill">💡 3 Healthier Alternatives</span>
        <span class="hero-pill">👨‍🍳 Authentic Home Recipes</span>
        <span class="hero-pill">💬 Grounded Interactive Chat</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Main Navigation Tabs
tab_image, tab_text = st.tabs(["📸 Multimodal Image Analysis", "🔍 Smart Meal Text Query"])


# TAB 1: Multimodal Image Analysis
with tab_image:
    col_input, col_preset = st.columns([1.6, 1.4])

    with col_input:
        st.markdown("### 📤 Upload Food Photo")
        uploaded_file = st.file_uploader(
            "Upload an image of a meal, snack, or ingredient (JPG, PNG, WEBP)",
            type=["jpg", "jpeg", "png", "webp"],
            help="High-resolution, well-lit photos give the highest nutritional accuracy.",
        )

    with col_preset:
        st.markdown("### ⚡ Quick Demo & Presets")
        st.caption("Test full intelligence instantly with sample dishes or test non-food guardrails:")
        
        preset_cols = st.columns(2)
        with preset_cols[0]:
            if st.button("🐟 Salmon Bowl", use_container_width=True):
                if os.path.exists("sample_images/salmon_bowl.jpg"):
                    with open("sample_images/salmon_bowl.jpg", "rb") as f:
                        img_bytes = f.read()
                    _, _, pil_img = process_image(img_bytes)
                    st.session_state["uploaded_img_bytes"] = img_bytes
                    st.session_state["uploaded_pil_img"] = pil_img
                    st.session_state["loaded_preset_name"] = "Mediterranean Grilled Salmon Bowl"
                    st.rerun()
            if st.button("🥑 Avocado Toast", use_container_width=True):
                if os.path.exists("sample_images/avocado_toast.jpg"):
                    with open("sample_images/avocado_toast.jpg", "rb") as f:
                        img_bytes = f.read()
                    _, _, pil_img = process_image(img_bytes)
                    st.session_state["uploaded_img_bytes"] = img_bytes
                    st.session_state["uploaded_pil_img"] = pil_img
                    st.session_state["loaded_preset_name"] = "Artisanal Avocado Sourdough Toast"
                    st.rerun()

        with preset_cols[1]:
            if st.button("🍚 Veg Biryani", use_container_width=True):
                if os.path.exists("sample_images/vegetable_biryani.jpg"):
                    with open("sample_images/vegetable_biryani.jpg", "rb") as f:
                        img_bytes = f.read()
                    _, _, pil_img = process_image(img_bytes)
                    st.session_state["uploaded_img_bytes"] = img_bytes
                    st.session_state["uploaded_pil_img"] = pil_img
                    st.session_state["loaded_preset_name"] = "Traditional Vegetable Biryani"
                    st.rerun()
            if st.button("💻 Non-Food Test", use_container_width=True):
                if os.path.exists("sample_images/laptop_non_food.jpg"):
                    with open("sample_images/laptop_non_food.jpg", "rb") as f:
                        img_bytes = f.read()
                    _, _, pil_img = process_image(img_bytes)
                    st.session_state["uploaded_img_bytes"] = img_bytes
                    st.session_state["uploaded_pil_img"] = pil_img
                    st.session_state["loaded_preset_name"] = "NON_FOOD_TEST"
                    st.rerun()

    # Active Image Preview & Action Trigger
    active_img_bytes = None
    active_pil_img = None

    if uploaded_file is not None:
        active_img_bytes, _, active_pil_img = process_image(uploaded_file)
        st.session_state["loaded_preset_name"] = None
    elif "uploaded_img_bytes" in st.session_state and st.session_state["uploaded_img_bytes"]:
        active_img_bytes = st.session_state["uploaded_img_bytes"]
        active_pil_img = st.session_state.get("uploaded_pil_img")

    if active_pil_img:
        st.markdown("---")
        preview_col, action_col = st.columns([1, 1.8])
        with preview_col:
            st.image(active_pil_img, caption="Ready for Multimodal Analysis", use_container_width=True)
        with action_col:
            st.markdown("#### Ready to Analyze")
            preset_name = st.session_state.get("loaded_preset_name")
            if preset_name == "NON_FOOD_TEST":
                st.caption("💻 Testing Non-Food Guardrails (Image of a laptop computer).")
            elif preset_name:
                st.caption(f"✨ Preset selected: **{preset_name}**")
            else:
                st.caption("📷 Custom user food photo ready for processing.")

            analyze_clicked = st.button("🚀 Analyze Food with Multimodal AI", type="primary", use_container_width=True)

            # If user has no API key and selected a preset, offer offline Instant Demo button
            if not st.session_state["api_key"] and preset_name and preset_name != "NON_FOOD_TEST":
                if st.button("⚡ Run Instant Demo (Offline Preset)", use_container_width=True):
                    preset_model = get_preset_as_model(preset_name)
                    if preset_model:
                        st.session_state["current_analysis"] = preset_model
                        st.session_state["current_image"] = active_pil_img
                        st.session_state["chat_history"] = []
                        # Add to history
                        thumb = pil_to_base64(active_pil_img)
                        st.session_state["history"].append({
                            "dish_name": preset_model.dish_name,
                            "calories": preset_model.nutrition.calories,
                            "timestamp": datetime.now().strftime("%H:%M"),
                            "thumb_b64": thumb,
                            "analysis": preset_model,
                            "image": active_pil_img,
                            "chat_history": [],
                        })
                        st.rerun()

            if analyze_clicked:
                api_key = st.session_state.get("api_key")
                
                # Check for non-food test shortcut if no API key provided
                if preset_name == "NON_FOOD_TEST" and not api_key:
                    st.error("⚠️ This doesn't look like food. Please upload an image of a meal, snack, or ingredient.", icon="🚫")
                elif not api_key:
                    st.error("⚠️ Gemini API key is missing. Please provide your API key in the sidebar, or click 'Run Instant Demo' above to test without a key.", icon="🔑")
                else:
                    with st.spinner("🤖 Food Verse Multimodal Agent is inspecting ingredients, calculating macros, and generating recipes..."):
                        try:
                            analysis_result = analyze_food_image(
                                image_bytes=active_img_bytes,
                                api_key=api_key,
                                model_name=st.session_state.get("model_name", "gemini-2.5-flash"),
                            )

                            st.session_state["current_analysis"] = analysis_result
                            st.session_state["current_image"] = active_pil_img
                            st.session_state["chat_history"] = []

                            # Add to session history
                            thumb = pil_to_base64(active_pil_img)
                            st.session_state["history"].append({
                                "dish_name": analysis_result.dish_name,
                                "calories": analysis_result.nutrition.calories,
                                "timestamp": datetime.now().strftime("%H:%M"),
                                "thumb_b64": thumb,
                                "analysis": analysis_result,
                                "image": active_pil_img,
                                "chat_history": [],
                            })
                            st.success("Analysis complete!")
                            st.rerun()

                        except NonFoodImageError as nfe:
                            st.error(f"⚠️ This doesn't look like food: {str(nfe)}", icon="🚫")
                        except ApiKeyMissingError as ake:
                            st.error(f"⚠️ {str(ake)}", icon="🔑")
                        except ModelGenerationError as mge:
                            st.error(f"⚠️ Analysis Error: {str(mge)}", icon="❌")
                        except Exception as e:
                            st.error(f"Unexpected error: {str(e)}", icon="💥")

    # Render Active Analysis Results
    analysis: Optional[FoodAnalysisResult] = st.session_state.get("current_analysis")
    
    if analysis:
        st.markdown("---")
        st.markdown(f"## 🍽️ Food Intelligence: **{analysis.dish_name}**")

        # Top Row: Dish Overview & Nutrition Score
        col_dish, col_score = st.columns([2.3, 1.2])

        with col_dish:
            st.markdown(f"""
            <div class="fv-card">
                <div class="fv-card-header">
                    <h3 class="fv-card-title">📖 Dish Overview</h3>
                    <span class="diet-pill">{analysis.diet_and_allergens.diet_category}</span>
                </div>
                <div style="font-size: 1.05rem; color: #E2E8F0; margin-bottom: 0.8rem; line-height: 1.6;">
                    {analysis.description}
                </div>
                <div style="margin-bottom: 0.8rem;">
                    <span style="color: #94A3B8; font-size: 0.85rem; font-weight: 600;">CUISINE:</span>
                    <span style="color: #38BDF8; font-weight: 700; margin-left: 0.4rem;">{analysis.cuisine}</span>
                    <span style="color: #64748B; margin: 0 0.5rem;">•</span>
                    <span style="color: #94A3B8; font-size: 0.85rem; font-weight: 600;">CONFIDENCE:</span>
                    <span style="color: #34D399; font-weight: 700; margin-left: 0.4rem;">{int(analysis.confidence_score * 100)}%</span>
                </div>
                <div>
                    <span style="color: #94A3B8; font-size: 0.85rem; font-weight: 600; display: block; margin-bottom: 0.3rem;">KEY IDENTIFIED INGREDIENTS:</span>
                    {''.join([f'<span class="ingredient-tag">{ing}</span>' for ing in analysis.main_ingredients])}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_score:
            health_color = get_health_score_color(analysis.nutrition.health_score)
            st.markdown(f"""
            <div class="fv-card" style="text-align: center;">
                <div class="fv-card-header" style="justify-content: center;">
                    <h3 class="fv-card-title">🎯 Health Score</h3>
                </div>
                <div style="margin: 0.8rem 0;">
                    <div class="score-badge" style="background: {health_color}22; color: {health_color}; border: 3px solid {health_color}; margin: 0 auto;">
                        {analysis.nutrition.health_score}
                    </div>
                    <div style="color: #94A3B8; font-size: 0.8rem; margin-top: 0.4rem; font-weight: 600;">OUT OF 10</div>
                </div>
                <div style="font-size: 0.88rem; color: #CBD5E1; line-height: 1.5; font-style: italic; background: rgba(0,0,0,0.25); padding: 0.6rem 0.8rem; border-radius: 8px;">
                    "{analysis.nutrition.health_score_reason}"
                </div>
            </div>
            """, unsafe_allow_html=True)

        # CARD 2: Nutrition Estimate
        p_pct, c_pct, f_pct = calculate_macro_percentages(
            analysis.nutrition.protein_g,
            analysis.nutrition.carbs_g,
            analysis.nutrition.fat_g,
        )

        st.markdown(f"""
        <div class="fv-card">
            <div class="fv-card-header">
                <h3 class="fv-card-title">📊 Nutrition Breakdown <span style="font-size:0.85rem; color:#94A3B8; font-weight:normal;">({analysis.nutrition.serving_size})</span></h3>
            </div>
            <div class="macro-grid">
                <div class="macro-box">
                    <div class="macro-label">Calories</div>
                    <div class="macro-val" style="color: #FACC15;">{analysis.nutrition.calories}</div>
                    <div class="macro-unit">kcal</div>
                </div>
                <div class="macro-box">
                    <div class="macro-label">Protein</div>
                    <div class="macro-val" style="color: #38BDF8;">{analysis.nutrition.protein_g}</div>
                    <div class="macro-unit">grams ({p_pct}%)</div>
                </div>
                <div class="macro-box">
                    <div class="macro-label">Carbs</div>
                    <div class="macro-val" style="color: #34D399;">{analysis.nutrition.carbs_g}</div>
                    <div class="macro-unit">grams ({c_pct}%)</div>
                </div>
                <div class="macro-box">
                    <div class="macro-label">Fats</div>
                    <div class="macro-val" style="color: #F43F5E;">{analysis.nutrition.fat_g}</div>
                    <div class="macro-unit">grams ({f_pct}%)</div>
                </div>
            </div>

            <!-- Caloric Distribution Bar -->
            <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:#94A3B8; margin-top:0.4rem;">
                <span>Protein ({p_pct}%)</span>
                <span>Carbs ({c_pct}%)</span>
                <span>Fat ({f_pct}%)</span>
            </div>
            <div class="macro-bar-container">
                <div style="width: {p_pct}%; background: #38BDF8;" title="Protein {p_pct}%"></div>
                <div style="width: {c_pct}%; background: #34D399;" title="Carbs {c_pct}%"></div>
                <div style="width: {f_pct}%; background: #F43F5E;" title="Fat {f_pct}%"></div>
            </div>

            <div style="display:flex; flex-wrap:wrap; gap:1.5rem; margin-top:1rem; padding-top:0.8rem; border-top:1px solid rgba(255,255,255,0.06); font-size:0.85rem; color:#94A3B8;">
                <div>🌾 Fiber: <strong style="color:#E2E8F0;">{analysis.nutrition.fiber_g or 0}g</strong></div>
                <div>🍬 Sugar: <strong style="color:#E2E8F0;">{analysis.nutrition.sugar_g or 0}g</strong></div>
                <div>🧂 Sodium: <strong style="color:#E2E8F0;">{analysis.nutrition.sodium_mg or 0}mg</strong></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # CARD 3: Diet & Allergens Check
        allergens_html = "".join([f'<span class="allergen-pill">⚠️ {a}</span>' for a in analysis.diet_and_allergens.allergens]) if analysis.diet_and_allergens.allergens else '<span style="color:#34D399; font-weight:600;">✅ No major allergens detected</span>'
        
        status_badges = []
        if analysis.diet_and_allergens.is_vegetarian:
            status_badges.append("🌱 Vegetarian")
        if analysis.diet_and_allergens.is_vegan:
            status_badges.append("🌿 100% Vegan")
        if analysis.diet_and_allergens.is_gluten_free:
            status_badges.append("🌾 Gluten-Free")
        if analysis.diet_and_allergens.is_dairy_free:
            status_badges.append("🥛 Dairy-Free")

        st.markdown(f"""
        <div class="fv-card">
            <div class="fv-card-header">
                <h3 class="fv-card-title">🛡️ Diet & Allergen Safety Check</h3>
            </div>
            <div style="margin-bottom: 1rem;">
                <div style="color: #94A3B8; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.4rem;">DIETARY CLASSIFICATIONS:</div>
                <div style="display:flex; flex-wrap:wrap; gap:0.5rem;">
                    {''.join([f'<span class="hero-pill" style="background:#064E3B; border-color:#059669; color:#A7F3D0;">{b}</span>' for b in status_badges])}
                </div>
            </div>
            <div style="margin-bottom: 1rem;">
                <div style="color: #94A3B8; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.4rem;">DETECTED ALLERGENS:</div>
                <div>{allergens_html}</div>
            </div>
            <div style="background: rgba(239, 68, 68, 0.08); border-left: 3px solid #EF4444; padding: 0.8rem 1rem; border-radius: 6px; font-size: 0.9rem; color: #FCA5A5;">
                <strong>Allergen Summary:</strong> {analysis.diet_and_allergens.allergen_warning}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # CARD 4: Smart Healthier Suggestions
        st.markdown("""
        <div class="fv-card">
            <div class="fv-card-header">
                <h3 class="fv-card-title">💡 Smart Suggestions – 3 Healthier Alternatives</h3>
            </div>
        """, unsafe_allow_html=True)

        alt_cols = st.columns(3)
        for i, alt in enumerate(analysis.healthier_alternatives):
            with alt_cols[i % 3]:
                st.markdown(f"""
                <div class="alt-card">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.5rem;">
                        <h4 style="margin:0; font-size:1.05rem; color:#F8FAFC;">{alt.name}</h4>
                    </div>
                    <div style="display:inline-block; background:rgba(16,185,129,0.15); color:#34D399; font-size:0.8rem; font-weight:700; padding:0.2rem 0.5rem; border-radius:6px; margin-bottom:0.6rem;">
                        {alt.calorie_comparison}
                    </div>
                    <div style="font-size:0.85rem; color:#CBD5E1; margin-bottom:0.5rem;">
                        <strong style="color:#94A3B8;">Substitutions:</strong> {alt.key_substitutions}
                    </div>
                    <div style="font-size:0.85rem; color:#6EE7B7;">
                        <strong style="color:#94A3B8;">Benefits:</strong> {alt.health_benefits}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # CARD 5: Authentic Home Recipe
        recipe = analysis.recipe
        st.markdown(f"""
        <div class="fv-card">
            <div class="fv-card-header">
                <h3 class="fv-card-title">👨‍🍳 Authentic Home Recipe</h3>
                <div style="display:flex; gap:0.6rem;">
                    <span class="hero-pill">⏱️ Prep: {recipe.prep_time_minutes} min</span>
                    <span class="hero-pill">🍳 Cook: {recipe.cook_time_minutes} min</span>
                    <span class="hero-pill">👥 Servings: {recipe.servings}</span>
                    <span class="hero-pill" style="border-color:#38BDF8; color:#7DD3FC;">⚡ {recipe.difficulty}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        rec_col1, rec_col2 = st.columns([1.1, 1.9])
        with rec_col1:
            st.markdown("##### 🛒 Ingredients")
            for item in recipe.ingredients:
                notes_text = f" *({item.notes})*" if item.notes else ""
                st.markdown(f"- **{item.amount}** {item.item}{notes_text}")

        with rec_col2:
            st.markdown("##### 📝 Step-by-Step Instructions")
            for step_num, step_desc in enumerate(recipe.instructions, 1):
                st.markdown(f"**Step {step_num}:** {step_desc}")

        st.markdown(f"""
        <div style="background: rgba(56, 189, 248, 0.08); border-left: 3px solid #38BDF8; padding: 0.8rem 1rem; border-radius: 6px; font-size: 0.9rem; color: #BAE6FD; margin-top: 1rem;">
            <strong>👨‍🍳 Executive Chef Tip:</strong> {recipe.chef_tip}
        </div>
        </div>
        """, unsafe_allow_html=True)

        # CARD 6: Interactive Grounded Chat Follow-Up
        st.markdown("---")
        st.markdown(f"### 💬 Ask Food Verse AI About **{analysis.dish_name}**")
        st.caption("Ask questions about custom modifications, portion control, cooking secrets, or ingredient swaps. The agent answers with your dish context.")

        # Quick prompt suggestion chips
        chip_col1, chip_col2, chip_col3 = st.columns(3)
        quick_prompt = None
        with chip_col1:
            if st.button("🥦 How can I lower calories further?", key="chip1", use_container_width=True):
                quick_prompt = "How can I lower calories further in this dish without losing flavor?"
        with chip_col2:
            if st.button("🧊 How do I store and reheat leftovers?", key="chip2", use_container_width=True):
                quick_prompt = "How should I store and reheat leftovers to maintain crispness and taste?"
        with chip_col3:
            if st.button("🍷 What side or beverage pairs with this?", key="chip3", use_container_width=True):
                quick_prompt = "What healthy side dish or beverage pairs best with this meal?"

        # Display Existing Chat Messages
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state["chat_history"]:
                role = msg.get("role", "user")
                if role == "user":
                    with st.chat_message("user"):
                        st.markdown(msg.get("content", ""))
                else:
                    with st.chat_message("assistant"):
                        st.markdown(msg.get("content", ""))

        # Chat Input
        user_chat_input = st.chat_input("Ask any culinary or nutritional follow-up about this dish...") or quick_prompt

        if user_chat_input:
            # Append user message
            st.session_state["chat_history"].append({"role": "user", "content": user_chat_input})
            
            with st.chat_message("user"):
                st.markdown(user_chat_input)

            api_key = st.session_state.get("api_key")
            with st.chat_message("assistant"):
                with st.spinner("Consulting culinary intelligence..."):
                    if not api_key:
                        # Demo response if offline
                        reply = (
                            f"**Culinary Note regarding {analysis.dish_name}:**\n\n"
                            f"Regarding *\"{user_chat_input}\"*: With {analysis.nutrition.protein_g}g of protein and {analysis.nutrition.calories} kcal, "
                            f"you can easily customize this recipe. For lower carbs, swap any grain elements for cauliflower or extra roasted vegetables. "
                            f"To preserve texture when reheating, use an air-fryer or dry skillet for 3-4 minutes.\n\n"
                            f"*(Running in Demo Mode. Connect your Gemini API key in the sidebar for full conversational reasoning!)*"
                        )
                        st.markdown(reply)
                        st.session_state["chat_history"].append({"role": "assistant", "content": reply})
                    else:
                        try:
                            chat_res: ChatFollowUpResponse = chat_about_dish(
                                chat_history=st.session_state["chat_history"],
                                dish_context=analysis,
                                user_message=user_chat_input,
                                api_key=api_key,
                                model_name=st.session_state.get("model_name", "gemini-2.5-flash"),
                            )
                            st.markdown(chat_res.answer)
                            st.session_state["chat_history"].append({"role": "assistant", "content": chat_res.answer})

                            if chat_res.suggested_followups:
                                st.caption("💡 Follow-up suggestions: " + " • ".join(chat_res.suggested_followups))

                        except Exception as e:
                            err_msg = f"Sorry, I encountered an issue: {str(e)}"
                            st.error(err_msg)
                            st.session_state["chat_history"].append({"role": "assistant", "content": err_msg})
            st.rerun()


# TAB 2: Smart Meal Text Query Mode
with tab_text:
    st.markdown("### 🔍 Query-Based Meal Recommendations")
    st.caption("Tell Food Verse AI what you crave or specify strict macro/diet constraints (e.g., *'high-protein vegetarian dinner under 500 calories'*).")

    # Example Query Chips
    st.markdown("**Quick Query Inspiration:**")
    tcol1, tcol2, tcol3 = st.columns(3)
    text_preset_query = None

    with tcol1:
        if st.button("💪 High-Protein Veg Dinner < 500 kcal", key="tq1", use_container_width=True):
            text_preset_query = "high-protein vegetarian dinner under 500 calories"
    with tcol2:
        if st.button("🥑 Low-Carb Keto Lunch < 400 kcal", key="tq2", use_container_width=True):
            text_preset_query = "low-carb keto lunch under 400 calories"
    with tcol3:
        if st.button("🌱 15-Min Vegan Post-Workout", key="tq3", use_container_width=True):
            text_preset_query = "15-minute quick vegan post-workout meal with 30g protein"

    text_query = st.text_input(
        "Enter your food or dietary query:",
        value=text_preset_query or "",
        placeholder="e.g. high-protein vegetarian dinner under 500 calories",
    )

    query_button = st.button("✨ Discover Recommended Dishes", type="primary")

    if (query_button or text_preset_query) and text_query:
        api_key = st.session_state.get("api_key")
        
        # Check if offline demo mode can answer
        if not api_key:
            st.warning("⚠️ No Gemini API key provided. Showing an offline culinary synthesis for demonstration. Paste your key in the sidebar for live dynamic AI recommendations!", icon="💡")
            # Create a rich demo response
            st.session_state["text_results"] = TextQueryResponse(
                query=text_query,
                summary=f"Here are 3 optimized, nutrient-dense dishes formulated to meet: '{text_query}'. Each recipe is rich in bioavailable micronutrients, plant/lean proteins, and balanced healthy fats.",
                recommendations=[
                    {
                        "dish_name": "Tofu & Edamame Soba Power Bowl",
                        "cuisine": "Japanese Inspired",
                        "calories": 440,
                        "protein_g": 32.0,
                        "carbs_g": 48.0,
                        "fat_g": 14.0,
                        "health_score": 9,
                        "health_score_reason": "High plant protein density, complex buckwheat carbs, and anti-inflammatory ginger dressing.",
                        "diet_category": "Vegan / High-Protein",
                        "allergens": ["Soy", "Sesame"],
                        "description": "Crisp pan-seared sesame tofu over 100% buckwheat soba noodles, steamed edamame, and bok choy.",
                        "key_ingredients": ["Firm Tofu", "Edamame", "Soba Noodles", "Tamari", "Sesame Oil"],
                        "quick_recipe_steps": [
                            "Boil soba noodles for 4 minutes and rinse under cold water.",
                            "Press and cube firm tofu, pan-sear in sesame oil until golden.",
                            "Steam edamame and baby bok choy for 2 minutes.",
                            "Toss noodles in ginger-tamari sauce and arrange in a bowl."
                        ]
                    },
                    {
                        "dish_name": "Spiced Paneer & Spinach Stuffed Bell Peppers",
                        "cuisine": "Indian / Continental",
                        "calories": 410,
                        "protein_g": 26.0,
                        "carbs_g": 22.0,
                        "fat_g": 24.0,
                        "health_score": 8,
                        "health_score_reason": "Low glycemic index, rich in calcium and iron with minimal refined carbs.",
                        "diet_category": "Vegetarian / Low-Carb",
                        "allergens": ["Dairy"],
                        "description": "Roasted bell pepper halves filled with crumbled low-fat paneer, garlic wilted spinach, and warm cumin spices.",
                        "key_ingredients": ["Bell Peppers", "Low-Fat Paneer", "Baby Spinach", "Cumin & Garam Masala"],
                        "quick_recipe_steps": [
                            "Halve and deseed bell peppers; roast at 400°F (200°C) for 10 mins.",
                            "Sauté onions, garlic, and spinach until wilted, then fold in crumbled paneer and spices.",
                            "Stuff mixture into peppers and bake for 15 minutes until bubbly.",
                            "Garnish with chopped cilantro and squeeze fresh lemon juice."
                        ]
                    },
                    {
                        "dish_name": "Mediterranean Chickpea & Lentil Greek Salad",
                        "cuisine": "Mediterranean",
                        "calories": 390,
                        "protein_g": 22.0,
                        "carbs_g": 46.0,
                        "fat_g": 12.0,
                        "health_score": 9,
                        "health_score_reason": "High dietary fiber (14g) promoting gut microbiome diversity and heart health.",
                        "diet_category": "Vegetarian",
                        "allergens": ["Dairy"],
                        "description": "Hearty brown lentils and chickpeas tossed with diced cucumbers, Kalamata olives, cherry tomatoes, and crumbled feta.",
                        "key_ingredients": ["Cooked Brown Lentils", "Chickpeas", "Cucumbers", "Cherry Tomatoes", "Feta Cheese"],
                        "quick_recipe_steps": [
                            "Rinse and drain canned brown lentils and chickpeas.",
                            "Dice cucumbers, tomatoes, and red onion into uniform bite-sized pieces.",
                            "Whisk lemon juice, oregano, olive oil, and sea salt in a salad bowl.",
                            "Combine all ingredients, toss well, and top with crumbled feta."
                        ]
                    }
                ]
            )
        else:
            with st.spinner("Searching culinary universe for the best matching dishes..."):
                try:
                    res = recommend_dishes_from_query(
                        query=text_query,
                        api_key=api_key,
                        model_name=st.session_state.get("model_name", "gemini-2.5-flash"),
                    )
                    st.session_state["text_results"] = res
                except Exception as e:
                    st.error(f"Failed to fetch recommendations: {str(e)}")

    # Display Text Query Recommendations
    text_res: Optional[TextQueryResponse] = st.session_state.get("text_results")
    if text_res:
        st.markdown("---")
        st.markdown(f"#### 💡 Recommendations for: *\"{text_res.query}\"*")
        st.info(f"**Agent Synthesis:** {text_res.summary}", icon="🥑")

        for idx, rec in enumerate(text_res.recommendations, 1):
            h_col = get_health_score_color(rec.health_score)
            allergens_str = ", ".join(rec.allergens) if rec.allergens else "None detected"
            
            with st.container():
                st.markdown(f"""
                <div class="fv-card">
                    <div class="fv-card-header">
                        <div>
                            <span style="font-size:0.85rem; color:#38BDF8; font-weight:700;">#{idx} RECOMMENDATION</span>
                            <h3 class="fv-card-title">{rec.dish_name} <span style="font-size:0.9rem; color:#94A3B8;">({rec.cuisine})</span></h3>
                        </div>
                        <div style="text-align:right;">
                            <span class="diet-pill">{rec.diet_category}</span>
                            <div style="font-size:0.8rem; color:{h_col}; font-weight:700; margin-top:0.3rem;">Score: {rec.health_score}/10</div>
                        </div>
                    </div>
                    <div style="color:#CBD5E1; font-size:0.95rem; margin-bottom:1rem; line-height:1.5;">
                        {rec.description}
                    </div>

                    <!-- Macro Row -->
                    <div class="macro-grid" style="margin-bottom:0.8rem;">
                        <div class="macro-box">
                            <div class="macro-label">Calories</div>
                            <div class="macro-val" style="color:#FACC15; font-size:1.2rem;">{rec.calories}</div>
                            <div class="macro-unit">kcal</div>
                        </div>
                        <div class="macro-box">
                            <div class="macro-label">Protein</div>
                            <div class="macro-val" style="color:#38BDF8; font-size:1.2rem;">{rec.protein_g}g</div>
                        </div>
                        <div class="macro-box">
                            <div class="macro-label">Carbs</div>
                            <div class="macro-val" style="color:#34D399; font-size:1.2rem;">{rec.carbs_g}g</div>
                        </div>
                        <div class="macro-box">
                            <div class="macro-label">Fats</div>
                            <div class="macro-val" style="color:#F43F5E; font-size:1.2rem;">{rec.fat_g}g</div>
                        </div>
                    </div>

                    <div style="font-size:0.85rem; color:#94A3B8; margin-bottom:0.6rem;">
                        <strong>Ingredients:</strong> {', '.join(rec.key_ingredients)}<br/>
                        <strong>Allergens:</strong> {allergens_str}
                    </div>

                    <div style="background:rgba(0,0,0,0.25); padding:0.8rem 1rem; border-radius:8px; font-size:0.85rem; color:#E2E8F0;">
                        <strong style="color:#38BDF8;">Quick Cooking Steps:</strong>
                        <ol style="margin-top:0.4rem; margin-bottom:0; padding-left:1.2rem;">
                            {''.join([f'<li>{s}</li>' for s in rec.quick_recipe_steps])}
                        </ol>
                    </div>
                </div>
                """, unsafe_allow_html=True)
