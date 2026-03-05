import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# --- 1. Database Setup ---
engine = create_engine(st.secrets["NEON_URI"])

def load_data():
    try:
        query = "SELECT * FROM survey_data"
        return pd.read_sql(query, engine)
    except Exception:
        return pd.DataFrame() 

# --- 2. Streamlit User Interface ---
st.set_page_config(page_title="NY CEO Survey Dashboard", layout="wide")
st.title("📊 NY CEO 2025 Survey Dashboard")
st.markdown("Interactive filtering and charting for the Siena Research Institute NY CEO Survey.")

# --- 3. Admin: Data Loader ---
st.sidebar.header("⚙️ Admin: Load Database")
uploaded_file = st.sidebar.file_uploader("Upload cleaned_survey_data.csv", type=["csv"])

if uploaded_file is not None:
    if st.sidebar.button("Push to Neon DB"):
        with st.spinner("Uploading to database..."):
            new_df = pd.read_csv(uploaded_file)
            new_df.to_sql("survey_data", engine, if_exists="replace", index=False)
        st.sidebar.success("Database updated successfully!")
        st.rerun()

st.sidebar.markdown("---")

# --- 4. Main App Logic ---
df = load_data()

if df.empty:
    st.info("👋 Welcome! The database is currently empty. Please upload the cleaned CSV using the sidebar to get started.")
    st.stop()

st.sidebar.header("Filter Options")

# Display Question Text in dropdown, but use Question ID internally if needed
questions = df['question_text'].unique()
selected_question = st.sidebar.selectbox("Select a Question", questions)

# Two-tier filtering for Segments
segment_types = df['segment_type'].unique()
selected_type = st.sidebar.selectbox("Select Demographic Category", segment_types)

# Dynamically populate values based on selected type (e.g., show "Mid-Hudson" if "Region" is selected)
segment_values = df[df['segment_type'] == selected_type]['segment_value'].unique()
selected_value = st.sidebar.selectbox("Select Specific Segment", segment_values)

# Apply filters
filtered_df = df[
    (df['question_text'] == selected_question) & 
    (df['segment_value'] == selected_value)
]

# --- 5. Graphing and Charting ---
st.subheader(f"{selected_question}")
st.markdown(f"**Showing responses for:** {selected_value} ({selected_type})")

if not filtered_df.empty:
    # Sort by percentage descending for better visualization
    filtered_df = filtered_df.sort_values(by="percentage", ascending=True)

    fig = px.bar(
        filtered_df, 
        x="percentage", 
        y="response", 
        orientation='h',
        text="percentage",
        color="response",
        labels={"percentage": "Percentage (%)", "response": "Survey Response"}
    )
    
    fig.update_traces(texttemplate='%{text}%', textposition='outside')
    fig.update_layout(showlegend=False, xaxis=dict(range=[0, 100]))
    
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("View Raw Data"):
        st.dataframe(filtered_df, use_container_width=True)
else:
    st.warning("No data available for this selection.")
