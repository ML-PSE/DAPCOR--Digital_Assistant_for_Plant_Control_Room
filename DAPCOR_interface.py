'''
********************************************************************
                  User Interface for DAPCOR
********************************************************************

Current Features:
    -- listens to voice commands; wakes up upon hearing 'OK Digital Assistant'
    -- fetches data from SQL query and verbally answers the user
    -- plots appropriate graphs based on the query

To run:
    -- type streamlit run .\DAPCOR_interface.py in the terminal
'''

#%% import packages
import streamlit as st, sqlalchemy as sql, pandas as pd, string
import plotly.graph_objects as go
import asyncio

import speech_recognition as sr 
import pyttsx3

from openai import OpenAI
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_openai import ChatOpenAI

from DAPCOR.agents import SQLDatabaseAgent, DataVisualizationAgent
from DAPCOR.multiagents import SQLDataAnalyst

#%% -----------------------------------------
#       streamlit interface settings
# -------------------------------------------
TITLE = "Digital Assistant for Plant Control Room"
st.set_page_config(page_title=TITLE, page_icon="📊", )
st.title(TITLE)

st.markdown("""
Welcome to DAPCOR. This Virtual Assistant is designed to help you query your SQL database and provide interactive plots.
""")

with st.expander("Example Questions", expanded=False):
    st.write(
        """
        - give me daily averaged fresh feed flow and furnace temperature
        - make a plot of daily averaged furnace temperature vs fresh feed flow
        - make a time plot of furnace temperature and fresh feed flow. Use distinct colors for each signal.
        """
    )

# Custom CSS for center-aligning the sidebar title and removing top margin
st.sidebar.markdown(
    """
    <style>
    .sidebar-title {
        text-align: center;
        font-size: 36px;
        font-weight: bold;
        margin-bottom: 30px;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.sidebar.markdown('<div class="sidebar-title">DAPCOR</div>', unsafe_allow_html=True) # Add a heading at the top of the sidebar

#%% -----------------------------------------
#               APP inputs
# -------------------------------------------
DB_OPTIONS = {
    "FCCU Dataset": "sqlite:///data/FCCU.db",
}

MODEL_LIST = ['gpt-4o-mini', 'gpt-4o']

# Database Selection
db_option = st.sidebar.selectbox(
    "Select a Database",
    list(DB_OPTIONS.keys()),
)
st.session_state["PATH_DB"] = DB_OPTIONS.get(db_option)

# OpenAI Model Selection
model_option = st.sidebar.selectbox(
    "Choose OpenAI model",
    MODEL_LIST,
    index=0
)

# OpenAI API Key
st.sidebar.header("Enter your OpenAI API Key")
st.session_state["OPENAI_API_KEY"] = st.sidebar.text_input("API Key", type="password", help="Your OpenAI API key is required for the app to function.")

#%% -------------------------------------------
# functions to dynamically update the interface
# ---------------------------------------------
def update_sidebar_theme(color): # This function is called to change the theme color of the sidebar [Green when listening and Maroon when executing].
    style = f"""
        <style>
        [data-testid="stSidebar"] {{
            background-color: {color} !important;
        }}
        </style>
    """
    st.markdown(style, unsafe_allow_html=True)

def auto_scroll(): # This function is called to scroll to the bottom of the chat window.
    js = '''
    <script>
        function scroll() {
            const messages = window.parent.document.querySelectorAll('[data-testid="stChatMessage"]');
            const lastMessage = messages[messages.length - 1];
            if (lastMessage) {
                lastMessage.scrollIntoView({ behavior: "smooth" });
            }
        }
        window.setTimeout(scroll, 50);
    </script>
    '''
    st.components.v1.html(js, height=0)

#%% --------------------------------------------
# functions to handle voice inputs and outputs
#-----------------------------------------------
def text_to_speech(text): # Function to convert text to speech
    converter = pyttsx3.init()
    voices = converter.getProperty('voices')  
    converter.setProperty('voice', voices[1].id)  # to speak in female voice
    converter.say(text)
    converter.runAndWait()

def continuous_speech_input(): # Function to continuously capture speech input
    while True:
        question = get_speech_input()
        if question:
            break
    return question

def get_speech_input(): # Function to capture speech input
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        # Apply green shade to the sidebar while listening
        update_sidebar_theme("#006400")

        st.info("Listening for your question...")
        auto_scroll()

        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source) # capture the audio

        try:
            question = recognizer.recognize_google(audio) # convert audio to text

            # check if 'digital assistant' is in the audio
            if "digital assistant" in question.lower():
                # keep only the portion of question that is after the key phrase 'digital assistant'
                question = question.split("digital assistant", 1)[1].strip()
                question = question.lstrip(string.whitespace + string.punctuation)

                st.success(f"You said: {question}")
                return question
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            st.error(f"Error: Could not request audio conversion to text; {e}")
        finally:
            # Remove green shade after listening
            update_sidebar_theme("maroon")
    return ""

#%% --------------------------------------------------------------------------------------------
# connect to database and test OpenAI API connection; generate LLM model object and the agent
# ----------------------------------------------------------------------------------------------
# database
sql_engine = sql.create_engine(st.session_state["PATH_DB"])
conn = sql_engine.connect()

# OpenAI API
if st.session_state["OPENAI_API_KEY"]:
    client = OpenAI(api_key=st.session_state["OPENAI_API_KEY"])
    
    try:
        # Fetch models to validate the key
        models = client.models.list()
        st.success("API Key is valid!")
    except Exception as e:
        st.error(f"Invalid API Key: {e}")
else:
    st.info("Please enter your OpenAI API Key to proceed.")
    st.stop()

llm = ChatOpenAI(
    model = model_option,
    api_key=st.session_state["OPENAI_API_KEY"]
)

# agent
# Create the SQL Database Agent
sql_data_analyst = SQLDataAnalyst(
    model = llm,
    sql_database_agent = SQLDatabaseAgent(
        model = llm,
        connection = conn,
        n_samples = 1,
        log = False,
    ),
    data_visualization_agent = DataVisualizationAgent(
        model = llm,
        n_samples = 10,
        log = False,
        bypass_explain_code = True,
    )
)

# Handle the question async
async def handle_question(question):
    await sql_data_analyst.ainvoke_agent(
        user_instructions=question,
    )
    return sql_data_analyst

#%% ---------------------------------------------
#             Set up interface memory
# -----------------------------------------------
msgs = StreamlitChatMessageHistory(key="langchain_messages")
if len(msgs.messages) == 0:
    msgs.add_ai_message("Hello! I am your digital assistant. How can I assist you?")
    text_to_speech("Hello! I am your digital assistant. How can I assist you?")

# Initialize dataframe storage in session state
if "dataframes" not in st.session_state:
    st.session_state.dataframes = []

# Function to display chat messages including Plotly charts and dataframes
def display_chat_history():
    for i, msg in enumerate(msgs.messages):
        with st.chat_message(msg.type):
            if "DATAFRAME_INDEX:" in msg.content:
                df_index = int(msg.content.split("DATAFRAME_INDEX:")[1])
                st.dataframe(st.session_state.dataframes[df_index])
            else:
                st.write(msg.content)

# Render current messages from StreamlitChatMessageHistory
display_chat_history()

#%% ---------------------------------------------------------------------
#                        Main Interaction Loop
# -----------------------------------------------------------------------
if st.session_state["PATH_DB"]:
    question = continuous_speech_input()
    while True:
        if len(question) > 0:
            # Check if API key is set
            if not st.session_state["OPENAI_API_KEY"]:
                st.error("Please enter your OpenAI API Key to proceed.")
                st.stop()
            
            with st.spinner("Thinking..."):
                st.chat_message("human").write(question)
                msgs.add_user_message(question)
                auto_scroll()
                
                # Run the app       
                error_occured = False
                try: 
                    print(st.session_state["PATH_DB"])
                    result = asyncio.run(handle_question(question))
                except Exception as e:
                    error_occured = True
                    print(e)
                    
                    response_text = f"""
                    I'm sorry. I am having difficulty answering that question. You can try providing more details and I'll do my best to provide an answer.
                    
                    Error: {e}
                    """
                    msgs.add_ai_message(response_text)
                    st.chat_message("ai").write(response_text)
                    st.error(f"Error: {e}")
                
                # Generate the Results
                if not error_occured:
                    sql_query = result.get_sql_query_code()
                    response_df = result.get_data_sql()
                    fig_dict = result.response.get("plotly_graph")
                    user_answer = result.response.get("user_answer")
                    
                    if sql_query:
                        # write and speak user answer
                        if user_answer is not None:
                            st.chat_message("ai").write(user_answer)
                            msgs.add_ai_message(user_answer)
                            text_to_speech(user_answer)

                        # Store the SQL
                        response_1 = f"### SQL Results:\n\nSQL Query:\n\n```sql\n{sql_query}\n```\n\nResult:"
                        
                        # Store the returned df
                        df_index = len(st.session_state.dataframes)
                        st.session_state.dataframes.append(response_df)

                        # Store response
                        msgs.add_ai_message(response_1)
                        msgs.add_ai_message(f"DATAFRAME_INDEX:{df_index}")
                        
                        # Write Results
                        st.chat_message("ai").write(response_1)
                        st.dataframe(response_df)

                        # display figure
                        if fig_dict is not None:
                            response_2 = 'Your requested plot:'
                            msgs.add_ai_message(response_2)
                            st.chat_message("ai").write(response_2)

                            fig = go.Figure(fig_dict)
                            st.plotly_chart(fig)
                        
                        auto_scroll()

                        # Prompt for another query
                        text_to_speech("What else can I help you with?")  
        
        # Get the next question
        auto_scroll()
        question = continuous_speech_input()