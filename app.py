import streamlit as st
import requests
import google.generativeai as genai

# --- 1. SETUP YOUR KEYS (Hidden securely in Streamlit) ---
WAQI_TOKEN = st.secrets["WAQI_TOKEN"]
GEMINI_KEY = st.secrets["GEMINI_KEY"]

# --- 2. CONFIGURE THE AI ---
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-3.5-flash')

# --- 3. BUILD THE WEBSITE INTERFACE ---
st.title("🌍 Air Quality & Health Precaution Assistant")
st.write("Enter your city to get real-time AQI and AI-generated health advice in English and Telugu.")

city = st.text_input("Enter your city (e.g., Kakinada, Delhi):")

if st.button("Check Air Quality"):
    if city:
        st.info(f"Fetching live data for {city}...")
        
        # --- 4. GET LIVE AQI DATA ---
        url = f"https://api.waqi.info/feed/{city}/?token={WAQI_TOKEN}"
        response = requests.get(url).json()

        if response['status'] == 'ok':
            raw_aqi = response['data']['aqi']
            
            # CHECK IF AQI IS A VALID NUMBER (Not a "-")
            if str(raw_aqi).isdigit():
                aqi = int(raw_aqi)
                st.success(f"**Current AQI in {city}:** {aqi}")

                # --- 5. MATCH WITH HEALTH RULES ---
                if aqi <= 50: rule = "Good: No precautions needed; safe for all outdoor activity."
                elif aqi <= 100: rule = "Satisfactory: Minor breathing discomfort possible for unusually sensitive people."
                elif aqi <= 200: rule = "Moderate: Sensitive groups (asthma, heart conditions) should limit prolonged outdoor exertion."
                elif aqi <= 300: rule = "Poor: General public should limit outdoor exertion; sensitive groups avoid it entirely; masks recommended."
                else: rule = "Severe: Health emergency risk for all; avoid all outdoor exposure."

                # --- 6. ASK THE AI TO GENERATE ADVICE ---
                prompt = f"""
                You are a local Health Precaution Assistant. 
                The live AQI in {city} is {aqi}. 
                The official health rule for this AQI is: '{rule}'. 
                Write a short, caring health warning for the user based ONLY on this rule. 
                Remind them you are an AI and not a doctor. 
                Provide the response clearly in English, followed by a Telugu translation.
                """
                
                with st.spinner("AI is generating your localized advice..."):
                    ai_response = model.generate_content(prompt)
                    st.write("### 🩺 Your Health Precaution:")
                    st.write(ai_response.text)
            else:
                st.warning(f"⚠️ The air quality sensor for {city} is currently offline or returning invalid data. Please try another city.")
        else:
            st.error("Sorry, could not find data for that city. Please try another nearby city.")
