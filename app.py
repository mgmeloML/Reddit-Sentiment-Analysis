import streamlit as st
import utlity 
from get_sentiment import sentiment
from fetch_data import fetch_data 

st.title("Reddit Sentiment Analysis Dashboard")
st.markdown("Analyse Reddit posts sentiment by keyword, subreddit, and time range.")
st.set_page_config(layout="wide")


with st.sidebar:
    st.header("Search Settings")

    keyword = st.text_input("Enter a keyword to analyse sentiment")
    limit = st.number_input("Enter the number of posts you want from each subreddit", value=20, step=1)
    if st.button("Fetch & Analyse"):
        if not keyword.strip():
            st.warning("Please enter a keyword.")
        else:
            with st.spinner("Fetching Reddit data and analysing sentiment..."):
                try:
                    df = sentiment(fetch_data(keyword, limit))
                    st.session_state.df = df
                    st.success("Data fetched and analysed successfully!")
                except Exception as e:
                    st.error(f"Error fetching data: {e}")

if "df" in st.session_state:
    df = st.session_state.df

    with st.sidebar:
        st.divider()
        st.header("Filters")

        subreddits = st.multiselect(
            "Select Subreddits",
            options=utlity.subreddit_list(df)
        )

        min_date, max_date = utlity.valid_time_range(utlity.subreddit_range(df,subreddits))
        if min_date and max_date:
            start_date, end_date = st.date_input(
                "Select Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,

            )
        else:
            st.warning("No valid dates found in the data.")
            start_date = end_date = None

    if subreddits:
        st.subheader("Key Metrics")
        total_posts, pos, neu, neg = utlity.key_metrics(df, subreddits, start_date, end_date)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Posts", total_posts)
        col2.metric("Positive", pos)
        col3.metric("Neutral", neu)
        col4.metric("Negative", neg)

        st.divider()
        st.subheader("Sentiment Distribution")

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(
                utlity.sentiment_pie_chart(df, subreddits, start_date, end_date),
                use_container_width=True
            )
        with col2:
            st.plotly_chart(
                utlity.sentiment_bar_chart(df, subreddits, start_date, end_date),
                use_container_width=True
            )

        st.divider()
        st.subheader("Sentiment Over Time")
        st.plotly_chart(
            utlity.sentiment_line_chart(df, subreddits, start_date, end_date),
            use_container_width=True
        )

        st.divider()
        st.subheader("Subreddit Contribution")
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(
                utlity.contribution_pie_chart(df, subreddits, start_date, end_date),
                use_container_width=True
            )
        with col2:
            st.plotly_chart(
                utlity.contribution_bar_chart(df, subreddits, start_date, end_date),
                use_container_width=True
            )

        st.divider()
        st.subheader("Example Post data")
        col1, col2, col3 = st.columns(3)
        df_pos, df_neu, df_neg = utlity.show_examples(df, subreddits, start_date, end_date)


        with col1:
            st.text("Positive Posts")
            st.dataframe(df_pos.head())
        with col2:
            st.text("Neutral Posts")
            st.dataframe(df_neu.head())
        with col3:
            st.text("Negative Posts")
            st.dataframe(df_neg.head())

    else:
        st.info("Select at least one subreddit")