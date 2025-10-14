import streamlit as st
from get_sentiment import sentiment
from fetch_data import fetch_data
import utlity
import datetime

st.title("Reddit Sentiment Analysis")
st.set_page_config(layout="wide")

if 'button' not in st.session_state:
    st.session_state.button = False

def click_button():
    st.session_state.button = not st.session_state.button

@st.cache_data
def do(keyword):
    return sentiment(fetch_data(keyword))

keyword = st.text_input("Enter a keyword to analyse sentiment", on_change=click_button)
analyse = st.button("Analyse", on_click=click_button)

if keyword and st.session_state.button:
    df = do(keyword)
    with st.sidebar:
        subreddit_options = st.multiselect("Select subreddits to analyse", utlity.subreddit_list(df))
        min_date, max_date = utlity.valid_time_range(df)
        data_time_range = st.date_input("Input date range to analyse", min_value=min_date, max_value=max_date)


st.session_state.button