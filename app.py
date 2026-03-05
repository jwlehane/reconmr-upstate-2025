import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# --- 1. Database Setup & Data Loading ---
# Securely load the Neon connection string from Streamlit Secrets
engine = create_engine(st.secrets["NEON_URI"])

def setup_database():
    """Initializes the database with sample parsed data from the NY CEO Survey."""
    data = [
        {"Question": "Q2. Current Business Conditions", "Response": "Better", "Segment": "Total", "Percentage": 11},
        {"Question": "Q2. Current Business Conditions", "Response": "About the same", "Segment": "Total", "Percentage": 24},
        {"Question": "Q2. Current Business Conditions", "Response": "A little worse", "Segment": "Total", "Percentage": 43},
        {"Question": "Q2. Current Business Conditions", "Response": "Considerably worse", "Segment": "Total", "Percentage": 22},
        {"Question": "Q6. Revenue Expectations", "Response": "Grow", "Segment": "Total", "Percentage": 33},
        {"Question": "Q6. Revenue Expectations", "Response": "Stay the same", "Segment": "Total", "Percentage": 39},
        {"Question": "Q6. Revenue Expectations", "Response": "Decrease", "Segment": "Total", "Percentage": 27},
        {"Question": "Q15. Gov Focus Areas", "Response": "Business Income Tax Reform", "Segment": "Total", "Percentage": 57},
        {"Question": "Q15. Gov Focus Areas", "Response": "Personal Income Tax Reform", "Segment": "Total", "Percentage": 50},
        {"Question": "Q15. Gov Focus Areas", "Response": "Spending Cuts", "Segment": "Total", "Percentage": 50},
    ]
    
    df = pd.DataFrame(data)
    # Write to Neon Postgres
    df.to_sql("survey_data", engine, if_exists="replace", index=False)

def load_data():
    """Fetches data from the Neon database."""
    query = "SELECT * FROM survey_data"
    return pd.read_sql(query, engine)

# Initialize DB (Writes the sample data to Neon)
setup_database()
df = load_data()

# --- 2. Streamlit User Interface ---
st.set_page_config(page_title="NY CEO Survey Dashboard", layout="wide")
st.title("📊 NY CEO 2025 Survey Dashboard")
st.markdown("Interactive filtering and charting for the Siena Research Institute NY CEO Survey.")

# --- 3. Filter Interface ---
st.sidebar.header("Filter Options")

questions = df['Question'].unique()
selected_question = st.sidebar.selectbox("Select a Question", questions)

segments = df[df['Question'] == selected_question]['Segment'].unique()
selected_segment = st.sidebar.selectbox("Select Segment/Demographic", segments)

filtered_df = df[(df['Question'] == selected_question) & (df['Segment'] == selected_segment)]

# --- 4. Graphing and Charting ---
st.subheader(f"{selected_question} ({selected_segment})")

if not filtered_df.empty:
    fig = px.bar(
        filtered_df, 
        x="Percentage", 
        y="Response", 
        orientation='h',
        text="Percentage",
        color="Response",
        title=f"Responses for {selected_segment}",
        labels={"Percentage": "Percentage (%)", "Response": "Survey Response"}
    )
    
    fig.update_traces(texttemplate='%{text}%', textposition='outside')
    fig.update_layout(showlegend=False, xaxis=dict(range=[0, 100]))
    
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("View Raw Data"):
        st.dataframe(filtered_df, use_container_width=True)
else:
    st.warning("No data available for this selection.")



