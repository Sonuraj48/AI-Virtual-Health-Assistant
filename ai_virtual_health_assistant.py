import streamlit as st
import google.generativeai as genai
import time

# --- App Configuration ---
st.set_page_config(
    page_title="AI Virtual Health Assistant",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- System Prompt ---
# This prompt defines the AI's role, personality, and instructions.
SYSTEM_PROMPT = """
You are a professional and empathetic virtual health assistant. Your primary goal is to help users understand their health concerns better.

Follow this process strictly:
1.  Start by introducing yourself and asking the user about their symptoms or health concerns.
2.  Based on the user's initial input, ask relevant and necessary follow-up questions to gather more specific information. Ask one question at a time. Do not overwhelm the user.
3.  Continue this questioning process until you have sufficient information to form a preliminary assessment.
4.  Once you have gathered enough details, provide a structured response with the following sections:
    - **Probable Diagnosis:** List 1-3 possible conditions that might align with the symptoms. Use clear, simple language.
    - **Recommendation:** Clearly state whether a doctor's visit is necessary (e.g., "Immediate visit recommended," "Consult a doctor soon," or "Monitor symptoms at home for now").
    - **Lifestyle & Dietary Tips:** Provide actionable advice related to lifestyle (e.g., rest, exercise) and diet that could help alleviate the symptoms.
    - **Ayurvedic & Home Remedies:** Suggest simple, safe, and widely known Ayurvedic or home remedies that could offer relief.

**Crucial Safety Instructions:**
- **Always include a disclaimer:** Start and end every single response with a clear disclaimer: "I am an AI assistant and not a medical professional. This is not a substitute for professional medical advice. Please consult a doctor for an accurate diagnosis."
- **Never pretend to be a doctor.**
- **If symptoms sound severe (e.g., chest pain, difficulty breathing, severe bleeding), immediately advise the user to seek emergency medical help.**
"""

# --- UI Styling ---
st.markdown("""
<style>
    .stApp {
        background-color: #F0F2F6;
    }
    .stChatMessage {
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .st-emotion-cache-1c7y2kd {
        border-radius: 10px;
        border: 1px solid #E0E0E0;
    }
    .st-emotion-cache-janbn0 {
        border-radius: 0.5rem;
    }
    h1 {
        color: #1E3A8A; /* Dark Blue */
        text-align: center;
    }
    .disclaimer {
        font-size: 0.8rem;
        text-align: center;
        color: #666;
        background-color: #FFFBEB; /* Light Yellow */
        padding: 0.5rem;
        border-radius: 5px;
        border: 1px solid #FBBF24; /* Amber */
    }
</style>
""", unsafe_allow_html=True)


# --- Main App Logic ---
st.title("🩺 AI Virtual Health Assistant")

st.markdown(
    "<div class='disclaimer'><strong>Disclaimer:</strong> This is an AI-powered assistant and is not a substitute for professional medical advice. Always consult with a qualified healthcare provider for any health concerns.</div>",
    unsafe_allow_html=True
)

# --- Sidebar for API Key ---
with st.sidebar:
    st.header("Configuration")
    st.markdown("Please enter your Google AI API key to begin.")
    api_key = st.text_input("Google AI API Key", type="password", key="api_key_input")
    st.markdown("[Get your API key here](https://aistudio.google.com/app/apikey)")
    st.markdown("---")
    st.markdown("Built with [Streamlit](https://streamlit.io) & [Gemini](https://ai.google.dev/)")


# --- Chat Initialization ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "chat_model" not in st.session_state:
    st.session_state.chat_model = None

# Function to initialize the chat model
def initialize_chat_model(key):
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        # Start a new chat with the system prompt
        chat = model.start_chat(
            history=[
                {"role": "user", "parts": [SYSTEM_PROMPT]},
                {"role": "model", "parts": ["I am an AI assistant and not a medical professional. This is not a substitute for professional medical advice. Please consult a doctor for an accurate diagnosis. \n\nHello! I'm your virtual health assistant. How are you feeling today? Please tell me about your symptoms."]}
            ]
        )
        return chat
    except Exception as e:
        st.error(f"Error initializing the AI model: {e}")
        return None

if api_key:
    if st.session_state.chat_model is None:
        st.session_state.chat_model = initialize_chat_model(api_key)
else:
    st.warning("Please enter your API key in the sidebar to start the chat.")
    st.stop()

# --- Display Chat History ---
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- User Input ---
if prompt := st.chat_input("Describe your symptoms..."):
    if not api_key:
        st.info("Please add your API key to continue.")
        st.stop()

    # Add user message to history and display it
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                chat_session = st.session_state.chat_model
                if chat_session:
                    response = chat_session.send_message(prompt)
                    # The actual response text is in response.text
                    full_response = response.text
                    
                    # Add AI response to history
                    st.session_state.chat_history.append({"role": "assistant", "content": full_response})
                    
                    # Simulate typing effect
                    message_placeholder = st.empty()
                    display_text = ""
                    for char in full_response:
                        display_text += char
                        message_placeholder.markdown(display_text + "▌")
                        time.sleep(0.01)
                    message_placeholder.markdown(full_response)
                else:
                    st.error("Chat session not initialized. Please check your API key.")

            except Exception as e:
                st.error(f"An error occurred: {e}")
