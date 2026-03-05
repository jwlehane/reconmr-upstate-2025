import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# --- 1. Database Setup ---
# Securely load the Neon connection string from Streamlit Secrets
engine = create_engine(st.secrets["NEON_URI"])

def load_data():
    """Fetches data from the Neon database."""
    try:
        query = "SELECT * FROM survey_data"
        return pd.read_sql(query, engine)
    except Exception:
        # Returns empty dataframe if table doesn't exist yet
        return pd.DataFrame() 

# --- 2. Streamlit User Interface ---
st.set_page_config(page_title="NY CEO Survey Dashboard", layout="wide")
st.title("📊 NY CEO 2025 Survey Dashboard")
st.markdown("Interactive filtering and charting for the Siena Research Institute NY CEO Survey.")

# --- 3. Admin: Data Loader ---
st.sidebar.header("⚙️ Admin: Load Database")
uploaded_file = st.sidebar.file_uploader("Upload Cleaned CSV", type=["csv"])

if uploaded_file is not None:
    if st.sidebar.button("Push to Neon DB"):
        with st.spinner("Uploading to database..."):
            new_df = pd.read_csv(uploaded_file)
            # This overwrites the existing table with your new CSV data
            new_df.to_sql("survey_data", engine, if_exists="replace", index=False)
        st.sidebar.success("Database updated successfully!")
        st.rerun()

st.sidebar.markdown("---")

# --- 4. Main App Logic ---
df = load_data()

if df.empty:
    st.info("👋 Welcome! The database is currently empty. Please upload a CSV using the sidebar to get started.")
    st.stop()

st.sidebar.header("Filter Options")

# Filter by Question
questions = df['Question'].unique()
selected_question = st.sidebar.selectbox("Select a Question", questions)

# Filter by Segment (Region, Industry, Total, etc.)
segments = df[df['Question'] == selected_question]['Segment'].unique()
selected_segment = st.sidebar.selectbox("Select Segment/Demographic", segments)

# Apply filters
filtered_df = df[(df['Question'] == selected_question) & (df['Segment'] == selected_segment)]

# --- 5. Graphing and Charting ---
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