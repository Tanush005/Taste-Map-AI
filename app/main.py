# import streamlit as st
# import pandas as pd
# import requests
# import json
# import google.generativeai as genai
#
# # --- PAGE CONFIGURATION ---
# st.set_page_config(
#     page_title="TasteMap AI",
#     page_icon="🍽️",
#     layout="wide",
#     initial_sidebar_state="collapsed"
# )
#
# # --- API CONFIGURATION ---
# try:
#     GOOGLE_API_KEY = st.secrets["google"]["api_key"]
#     genai.configure(api_key=st.secrets["gemini"]["api_key"])
#     llm = genai.GenerativeModel('gemini-1.5-flash')
# except (KeyError, AttributeError):
#     st.error("🚨 API key not found. Please ensure 'google' and 'gemini' keys are in your secrets.toml.")
#     st.stop()
#
# # --- UI STYLING (TOP-NOTCH) ---
# st.markdown("""
#     <style>
#         @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
#
#         html, body, [class*="st-"] {
#             font-family: 'Inter', sans-serif;
#         }
#
#         /* Main App Styling */
#         .stApp {
#             background-color: #0B090C; /* Even darker background */
#             color: #EAE6F0;
#         }
#
#         /* Hide Streamlit elements */
#         #MainMenu, footer, header { visibility: hidden; }
#         .stDeployButton { display: none !important; }
#
#         /* Custom Title */
#         .title {
#             text-align: center;
#             font-size: 3.5rem;
#             font-weight: 700;
#             padding-top: 2rem;
#         }
#         .subtitle {
#             text-align: center;
#             font-size: 1.2rem;
#             color: #A99EB8;
#             padding-bottom: 2rem;
#         }
#
#         /* Tabs Styling */
#         .stTabs [data-baseweb="tab-list"] {
#             gap: 24px;
#             justify-content: center;
#         }
#         .stTabs [data-baseweb="tab"] {
#             height: 50px;
#             background-color: transparent;
#             padding: 0 10px;
#             border-radius: 8px;
#         }
#         .stTabs [data-baseweb="tab"]:hover {
#             background-color: rgba(255, 255, 255, 0.05);
#         }
#         .stTabs [data-baseweb="tab"][aria-selected="true"] {
#             background-color: #7f5af0; /* A nice purple for selection */
#             color: white;
#         }
#
#         /* Detailed Results Card Styling */
#         .result-card {
#             background-color: #16161a;
#             border: 1px solid #242629;
#             border-radius: 12px;
#             padding: 1.5rem;
#             margin-bottom: 1.5rem;
#             transition: all 0.2s ease-in-out;
#         }
#         .result-card:hover {
#             border-color: #7f5af0;
#         }
#         .card-header {
#             display: flex;
#             justify-content: space-between;
#             align-items: center;
#             margin-bottom: 0.5rem;
#         }
#         .card-title {
#             font-size: 1.5rem;
#             font-weight: 700;
#             color: #fffffe;
#             margin: 0;
#         }
#         .card-rating {
#             background-color: #2cb67d; /* Green for rating */
#             color: #fffffe;
#             padding: 0.3rem 0.8rem;
#             border-radius: 1rem;
#             font-weight: 600;
#             font-size: 0.9rem;
#         }
#         .card-status-open {
#             color: #2cb67d;
#         }
#         .card-status-closed {
#             color: #ef4565;
#         }
#         .card-details {
#             font-size: 1rem;
#             color: #94a1b2;
#             margin: 0.5rem 0;
#         }
#         .card-links a {
#             color: #7f5af0;
#             text-decoration: none;
#             margin-right: 1.5rem;
#             font-weight: 600;
#         }
#         .card-links a:hover {
#             text-decoration: underline;
#         }
#     </style>
# """, unsafe_allow_html=True)
#
#
# # --- API & HELPER FUNCTIONS ---
#
# @st.cache_data(ttl=3600)
# def get_llm_params(query):
#     """Uses Gemini to parse a query into structured search parameters."""
#     prompt = f"""
#     You are an expert restaurant recommendation assistant. From the user's query: "{query}", extract the following entities:
#     - "keyword": The main food, cuisine, or type of place.
#     - "vibe": Any specific ambiance or occasion (e.g., "romantic", "casual", "instagram-worthy").
#     - "diet": Specifically identify if the user asks for "veg" or "non-veg". Default to "any".
#     - "location": The city or area to search in.
#     Return ONLY a single, compact JSON object. If a value isn't mentioned, set it to null.
#     Example: "Find a romantic veg italian place in New York" -> {{"keyword": "italian restaurant", "vibe": "romantic", "diet": "veg", "location": "New York"}}
#     """
#     try:
#         response = llm.generate_content(prompt)
#         json_str = response.text.strip().replace("```json", "").replace("```", "").strip()
#         return json.loads(json_str)
#     except Exception:
#         return {"keyword": query, "location": None, "vibe": None, "diet": "any"}
#
#
# @st.cache_data(ttl=600)
# def search_and_get_details(params):
#     """Searches Google Places and gets rich details for each result."""
#     if not params.get("location"):
#         return "NO_LOCATION", None
#
#     geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
#     geo_res = requests.get(geocode_url, params={"address": params["location"], "key": GOOGLE_API_KEY})
#     geo_data = geo_res.json()
#     if geo_data.get("status") != "OK":
#         return "GEOCODE_FAILED", None
#     loc = geo_data["results"][0]["geometry"]["location"]
#     lat_lon = f"{loc['lat']},{loc['lng']}"
#
#     search_keyword = f"{params.get('diet') or ''} {params.get('vibe') or ''} {params.get('keyword') or 'restaurant'}".strip()
#
#     places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
#     places_params = {"location": lat_lon, "radius": 5000, "keyword": search_keyword, "key": GOOGLE_API_KEY}
#     places_res = requests.get(places_url, params=places_params)
#     restaurants_found = places_res.json().get("results", [])
#
#     detailed_results = []
#     place_fields = "name,rating,user_ratings_total,price_level,opening_hours,formatted_phone_number,website,geometry"
#     for place in restaurants_found[:5]:
#         details_url = "https://maps.googleapis.com/maps/api/place/details/json"
#         details_params = {"place_id": place['place_id'], "fields": place_fields, "key": GOOGLE_API_KEY}
#         details_res = requests.get(details_url, params=details_params)
#         details = details_res.json().get("result", {})
#
#         if details:
#             detailed_results.append({
#                 "name": details.get("name"),
#                 "rating": details.get("rating", "N/A"),
#                 "total_ratings": details.get("user_ratings_total", 0),
#                 "address": details.get("vicinity"),
#                 "price": "$" * details.get("price_level", 0) if details.get("price_level") else "N/A",
#                 "open_now": details.get("opening_hours", {}).get("open_now"),
#                 "phone": details.get("formatted_phone_number"),
#                 "website": details.get("website"),
#                 "lat": details.get("geometry", {}).get("location", {}).get("lat"),
#                 "lon": details.get("geometry", {}).get("location", {}).get("lng"),
#             })
#
#     return "OK", detailed_results
#
#
# def display_result_card(result):
#     """Renders a single, detailed result card."""
#     open_status = "Open" if result.get('open_now') else "Closed" if result.get('open_now') is not None else "N/A"
#     status_class = "card-status-open" if open_status == "Open" else "card-status-closed"
#
#     st.markdown(f"""
#         <div class="result-card">
#             <div class="card-header">
#                 <p class="card-title">{result['name']}</p>
#                 <div class="card-rating">⭐ {result['rating']} ({result['total_ratings']})</div>
#             </div>
#             <p class="card-details">
#                 <span class="card-price" style="font-weight: bold;">{result['price']}</span> • {result['address']}
#             </p>
#             <p class="card-details">
#                 Status: <span class="{status_class}">{open_status}</span>
#             </p>
#             <div class="card-links">
#                 {'<a href="' + result['website'] + '" target="_blank">🌐 Website</a>' if result.get('website') else ''}
#                 {'<span>📞 ' + result['phone'] + '</span>' if result.get('phone') else ''}
#             </div>
#         </div>
#     """, unsafe_allow_html=True)
#
#
# # --- MAIN APP LAYOUT ---
#
# st.markdown('<p class="title">TasteMap AI</p>', unsafe_allow_html=True)
# st.markdown('<p class="subtitle">Your intelligent guide to the world of food</p>', unsafe_allow_html=True)
#
# ai_tab, classic_tab = st.tabs(["🤖 AI Chat Search", "Classic Search"])
#
# # --- AI CHATBOT TAB ---
# with ai_tab:
#     if "messages" not in st.session_state:
#         st.session_state.messages = [
#             {"role": "assistant", "content": "What are you craving today? For example, 'a cozy veg cafe in Mandi'."}]
#
#     for message in st.session_state.messages:
#         with st.chat_message(message["role"]):
#             st.markdown(message["content"])
#
#     if prompt := st.chat_input("Your request..."):
#         st.session_state.messages.append({"role": "user", "content": prompt})
#         with st.chat_message("user"):
#             st.markdown(prompt)
#
#         with st.chat_message("assistant"):
#             with st.spinner("Let me think..."):
#                 params = get_llm_params(prompt)
#                 status, results = search_and_get_details(params)
#
#                 if status == "NO_LOCATION":
#                     st.markdown("Sounds delicious! Where should I look?")
#                     st.session_state.messages.append(
#                         {"role": "assistant", "content": "Sounds delicious! Where should I look?"})
#                 elif status == "GEOCODE_FAILED" or not results:
#                     st.markdown("Sorry, I couldn't find any spots matching that. Could you try a different search?")
#                     st.session_state.messages.append({"role": "assistant",
#                                                       "content": "Sorry, I couldn't find any spots matching that. Could you try a different search?"})
#                 else:
#                     st.markdown(
#                         f"Here are the top spots I found for **'{params.get('keyword')}'** in **{params.get('location')}**:")
#                     for r in results:
#                         display_result_card(r)
#
#                     map_df = pd.DataFrame(results)
#                     st.map(map_df, latitude='lat', longitude='lon')
#
# # --- CLASSIC SEARCH TAB ---
# with classic_tab:
#     with st.form("classic_search"):
#         st.subheader("Find Restaurants with Precision")
#         col1, col2 = st.columns(2)
#         with col1:
#             keyword = st.text_input("Cuisine or Food Type", placeholder="e.g., Pizza, Cafe, Tandoori")
#         with col2:
#             location = st.text_input("Location", placeholder="e.g., Mandi, Himachal Pradesh")
#
#         diet = st.radio("Dietary Preference", ["Any", "Veg", "Non-Veg"], horizontal=True)
#         vibe = st.text_input("Vibe or Occasion (Optional)", placeholder="e.g., Romantic, Casual, Family-friendly")
#
#         submitted = st.form_submit_button("Search Restaurants")
#
#     if submitted:
#         if not keyword or not location:
#             st.warning("Please enter a food type and location.")
#         else:
#             with st.spinner("Finding the best spots..."):
#                 params = {"keyword": keyword, "location": location, "diet": diet.lower() if diet != "Any" else None,
#                           "vibe": vibe}
#                 status, results = search_and_get_details(params)
#
#                 if status == "OK" and results:
#                     st.success(f"Found {len(results)} great options for you!")
#                     for r in results:
#                         display_result_card(r)
#
#                     map_df = pd.DataFrame(results)
#                     st.map(map_df, latitude='lat', longitude='lon')
#                 else:
#                     st.error("Couldn't find any restaurants matching your criteria. Please try again.")

import streamlit as st
import pandas as pd
import requests
import json
import google.generativeai as genai

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="TasteMap AI",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- API CONFIGURATION ---
try:
    GOOGLE_API_KEY = st.secrets["google"]["api_key"]
    genai.configure(api_key=st.secrets["gemini"]["api_key"])
    llm = genai.GenerativeModel('gemini-1.5-flash')
except (KeyError, AttributeError):
    st.error("🚨 API key not found. Please ensure 'google' and 'gemini' keys are in your secrets.toml.")
    st.stop()

# --- UI STYLING (UPGRADED) ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

        html, body, [class*="st-"] {
            font-family: 'Inter', sans-serif;
        }

        .stApp {
            background-color: #0B090C;
            color: #EAE6F0;
        }

        #MainMenu, footer, header { visibility: hidden; }
        .stDeployButton { display: none !important; }

        .title {
            text-align: center;
            font-size: 3.5rem;
            font-weight: 700;
            padding-top: 2rem;
        }
        .subtitle {
            text-align: center;
            font-size: 1.2rem;
            color: #A99EB8;
            padding-bottom: 2rem;
        }

        /* Upgraded Results Card with Image */
        .result-card {
            background-color: #16161a;
            border: 1px solid #242629;
            border-radius: 16px;
            margin-bottom: 2rem;
            transition: all 0.2s ease-in-out;
            display: grid;
            grid-template-columns: 200px 1fr; /* Column for image and column for text */
            gap: 1.5rem;
            padding: 1.5rem;
        }
        .result-card:hover {
            border-color: #7f5af0;
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .card-image img {
            width: 100%;
            height: 200px;
            object-fit: cover;
            border-radius: 10px;
        }
        .card-info {
            display: flex;
            flex-direction: column;
        }
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }
        .card-title {
            font-size: 1.75rem;
            font-weight: 700;
            color: #fffffe;
            margin: 0;
            line-height: 1.2;
        }
        .card-rating {
            background-color: #2cb67d;
            color: #fffffe;
            padding: 0.3rem 0.8rem;
            border-radius: 1rem;
            font-weight: 600;
            font-size: 1rem;
            flex-shrink: 0;
            margin-left: 1rem;
        }
        .card-details, .card-links {
            font-size: 1rem;
            color: #94a1b2;
            margin: 0.5rem 0;
        }
        .card-links span, .card-links a {
            color: #7f5af0;
            text-decoration: none;
            margin-right: 1.5rem;
            font-weight: 600;
        }
        .card-review {
            border-left: 3px solid #7f5af0;
            padding-left: 1rem;
            margin-top: 1rem;
            font-style: italic;
            color: #94a1b2;
        }
    </style>
""", unsafe_allow_html=True)


# --- API & HELPER FUNCTIONS ---

@st.cache_data(ttl=3600)
def get_llm_params(query):
    # This function remains the same
    prompt = f"""
    You are an expert restaurant recommendation assistant. From the user's query: "{query}", extract the following entities:
    - "keyword": The main food, cuisine, or type of place.
    - "vibe": Any specific ambiance or occasion (e.g., "romantic", "casual", "instagram-worthy").
    - "diet": Specifically identify if the user asks for "veg" or "non-veg". Default to "any".
    - "location": The city or area to search in.
    Return ONLY a single, compact JSON object. If a value isn't mentioned, set it to null.
    """
    try:
        response = llm.generate_content(prompt)
        json_str = response.text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(json_str)
    except Exception:
        return {"keyword": query, "location": None, "vibe": None, "diet": "any"}


@st.cache_data(ttl=600)
def search_and_get_details(params):
    if not params.get("location"): return "NO_LOCATION", None

    geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
    geo_res = requests.get(geocode_url, params={"address": params["location"], "key": GOOGLE_API_KEY})
    geo_data = geo_res.json()
    if geo_data.get("status") != "OK": return "GEOCODE_FAILED", None
    loc = geo_data["results"][0]["geometry"]["location"]
    lat_lon = f"{loc['lat']},{loc['lng']}"

    search_keyword = f"{params.get('diet') or ''} {params.get('vibe') or ''} {params.get('keyword') or 'restaurant'}".strip()

    places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    places_params = {"location": lat_lon, "radius": 5000, "keyword": search_keyword, "key": GOOGLE_API_KEY}
    places_res = requests.get(places_url, params=places_params)
    restaurants_found = places_res.json().get("results", [])

    detailed_results = []
    # **UPDATED**: Added 'review' to fetch reviews
    place_fields = "name,rating,user_ratings_total,price_level,opening_hours,formatted_phone_number,website,geometry,photo,review"
    for place in restaurants_found[:4]:  # Limit to 4 for a cleaner UI
        details_url = "https://maps.googleapis.com/maps/api/place/details/json"
        details_params = {"place_id": place['place_id'], "fields": place_fields, "key": GOOGLE_API_KEY}
        details_res = requests.get(details_url, params=details_params)
        details = details_res.json().get("result", {})

        if details:
            photo_url = ""
            if details.get("photos"):
                photo_ref = details["photos"][0]["photo_reference"]
                photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={GOOGLE_API_KEY}"

            top_review = ""
            if details.get("reviews"):
                top_review = f"\"{details['reviews'][0]['text']}\" - {details['reviews'][0]['author_name']}"

            detailed_results.append({
                "name": details.get("name"),
                "rating": details.get("rating", "N/A"),
                "total_ratings": details.get("user_ratings_total", 0),
                "address": details.get("vicinity"),
                "price": "$" * details.get("price_level", 0) if details.get("price_level") else "N/A",
                "open_now": details.get("opening_hours", {}).get("open_now"),
                "phone": details.get("formatted_phone_number"),
                "website": details.get("website"),
                "lat": details.get("geometry", {}).get("location", {}).get("lat"),
                "lon": details.get("geometry", {}).get("location", {}).get("lng"),
                "photo_url": photo_url,
                "review": top_review,
            })

    return "OK", detailed_results


def display_result_card(result):
    """Renders a single, detailed result card with image and review."""
    open_status = "Open" if result.get('open_now') else "Closed" if result.get('open_now') is not None else "N/A"
    status_class = "card-status-open" if open_status == "Open" else "card-status-closed"

    # **UPDATED**: This HTML structure now includes the image, review, and corrected links.
    st.markdown(f"""
        <div class="result-card">
            <div class="card-image">
                <img src="{result.get('photo_url') or 'https://via.placeholder.com/200'}" alt="{result['name']}">
            </div>
            <div class="card-info">
                <div class="card-header">
                    <p class="card-title">{result['name']}</p>
                    <div class="card-rating">⭐ {result['rating']}</div>
                </div>
                <p class="card-details">
                    <span style="font-weight: bold;">{result['price']}</span> • {result['address']}
                </p>
                <p class="card-details">
                    Status: <span class="{status_class}">{open_status}</span>
                </p>
                <div class="card-links">
                    {'<a href="' + result['website'] + '" target="_blank">🌐 Website</a>' if result.get('website') else ''}
                    {'<span>📞 {phone}</span>'.format(phone=result['phone']) if result.get('phone') else ''}
                </div>
                {'<div class="card-review">' + result['review'] + '</div>' if result.get('review') else ''}
            </div>
        </div>
    """, unsafe_allow_html=True)


# --- MAIN APP LAYOUT ---

st.markdown('<p class="title">TasteMap AI</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Your intelligent guide to the world of food</p>', unsafe_allow_html=True)

ai_tab, classic_tab = st.tabs(["🤖 AI Chat Search", "Classic Search"])

# --- AI CHATBOT TAB ---
with ai_tab:
    # Chat logic remains largely the same, but now it calls the new display function
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "What are you craving? For example, 'a cozy veg cafe in Mandi'."}]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Your request..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Let me think..."):
                params = get_llm_params(prompt)
                status, results = search_and_get_details(params)

                if status == "NO_LOCATION":
                    st.markdown("Sounds delicious! Where should I look?")
                elif status == "GEOCODE_FAILED" or not results:
                    st.markdown("Sorry, I couldn't find any spots matching that. Could you try a different search?")
                else:
                    st.markdown(
                        f"Here are the top spots I found for **'{params.get('keyword')}'** in **{params.get('location')}**:")
                    for r in results: display_result_card(r)
                    map_df = pd.DataFrame(results);
                    st.map(map_df, latitude='lat', longitude='lon')

# --- CLASSIC SEARCH TAB ---
with classic_tab:
    with st.form("classic_search"):
        st.subheader("Find Restaurants with Precision")
        col1, col2 = st.columns(2)
        with col1: keyword = st.text_input("Cuisine or Food Type", placeholder="e.g., Pizza, Cafe")
        with col2: location = st.text_input("Location", placeholder="e.g., Mandi, Himachal Pradesh")
        diet = st.radio("Dietary Preference", ["Any", "Veg", "Non-Veg"], horizontal=True)
        submitted = st.form_submit_button("Search Restaurants")

    if submitted:
        if not keyword or not location:
            st.warning("Please enter a food type and location.")
        else:
            with st.spinner("Finding the best spots..."):
                params = {"keyword": keyword, "location": location, "diet": diet.lower() if diet != "Any" else None}
                status, results = search_and_get_details(params)

                if status == "OK" and results:
                    st.success(f"Found {len(results)} great options for you!")
                    for r in results: display_result_card(r)
                    map_df = pd.DataFrame(results);
                    st.map(map_df, latitude='lat', longitude='lon')
                else:
                    st.error("Couldn't find any restaurants matching your criteria. Please try again.")

