import streamlit as st
import utlity 
from get_sentiment import sentiment
from fetch_data import fetch_data 

# Set the main title and description for the dashboard
st.title("Reddit Sentiment Analysis Dashboard")
st.markdown("Analyse Reddit posts sentiment by keyword, subreddit, and time range.")

# Configure page layout to use wide mode for better visualization space
st.set_page_config(layout="wide")


# ===== SIDEBAR: DATA FETCHING SECTION =====
with st.sidebar:
    st.header("Search Settings")

    # Input field for user to enter search keyword
    keyword = st.text_input("Enter a keyword to analyse sentiment")
    
    # Number input to specify how many posts to fetch per subreddit
    limit = st.number_input("Enter the number of posts you want from each subreddit", value=20, step=1)
    
    # Button to trigger data fetching and sentiment analysis
    if st.button("Fetch & Analyse"):
        # Validate that keyword is not empty or just whitespace
        if not keyword.strip():
            st.warning("Please enter a keyword.")
        else:
            # Show loading spinner while processing
            with st.spinner("Fetching Reddit data and analysing sentiment..."):
                try:
                    # Fetch Reddit posts and perform sentiment analysis in one pipeline
                    df = sentiment(fetch_data(keyword, limit))
                    
                    # Store the resulting DataFrame in Streamlit's session state
                    # This persists data across reruns without refetching
                    st.session_state.df = df
                    
                    st.success("Data fetched and analysed successfully!")
                except Exception as e:
                    # Display error message if fetching or analysis fails
                    st.error(f"Error fetching data: {e}")


# ===== MAIN DASHBOARD: ONLY DISPLAYS IF DATA EXISTS =====
# Check if DataFrame exists in session state (i.e., data has been fetched)
if "df" in st.session_state:
    # Retrieve the DataFrame from session state
    df = st.session_state.df

    # ===== SIDEBAR: FILTER CONTROLS =====
    with st.sidebar:
        st.divider()  # Visual separator
        st.header("Filters")

        # Multi-select dropdown for choosing which subreddits to analyze
        subreddits = st.multiselect(
            "Select Subreddits",
            options=utlity.subreddit_list(df)  # Populate with unique subreddits from data
        )

        # Get valid date range from selected subreddits
        min_date, max_date = utlity.valid_time_range(utlity.subreddit_range(df, subreddits))
        
        # Only show date picker if valid dates exist
        if min_date and max_date:
            # Date range picker with min/max constraints based on available data
            start_date, end_date = st.date_input(
                "Select Date Range",
                value=(min_date, max_date),  # Default to full range
                min_value=min_date,
                max_value=max_date,
            )
        else:
            # Show warning if no valid dates found
            st.warning("No valid dates found in the data.")
            start_date = end_date = None

    # ===== MAIN CONTENT: ONLY DISPLAYS IF SUBREDDITS ARE SELECTED =====
    if subreddits:
        # ===== KEY METRICS SECTION =====
        st.subheader("Key Metrics")
        
        # Calculate summary statistics for selected filters
        total_posts, pos, neu, neg = utlity.key_metrics(df, subreddits, start_date, end_date)
        
        # Display metrics in 4 columns for clean layout
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Posts", total_posts)
        col2.metric("Positive", pos)
        col3.metric("Neutral", neu)
        col4.metric("Negative", neg)

        # ===== SENTIMENT DISTRIBUTION SECTION =====
        st.divider()  # Visual separator
        st.subheader("Sentiment Distribution")

        # Display pie chart and bar chart side-by-side
        col1, col2 = st.columns(2)
        with col1:
            # Pie chart showing proportion of each sentiment
            st.plotly_chart(
                utlity.sentiment_pie_chart(df, subreddits, start_date, end_date),
                use_container_width=True  # Chart fills column width
            )
        with col2:
            # Bar chart showing count of each sentiment
            st.plotly_chart(
                utlity.sentiment_bar_chart(df, subreddits, start_date, end_date),
                use_container_width=True
            )

        # ===== SENTIMENT OVER TIME SECTION =====
        st.divider()
        st.subheader("Sentiment Over Time")
        
        # Line chart showing how sentiment changes over the date range
        st.plotly_chart(
            utlity.sentiment_line_chart(df, subreddits, start_date, end_date),
            use_container_width=True
        )

        # ===== SUBREDDIT CONTRIBUTION SECTION =====
        st.divider()
        st.subheader("Subreddit Contribution")
        
        # Display two charts comparing subreddit activity
        col1, col2 = st.columns(2)
        with col1:
            # Pie chart showing proportion of posts from each subreddit
            st.plotly_chart(
                utlity.contribution_pie_chart(df, subreddits, start_date, end_date),
                use_container_width=True
            )
        with col2:
            # Stacked bar chart showing sentiment breakdown per subreddit
            st.plotly_chart(
                utlity.contribution_bar_chart(df, subreddits, start_date, end_date),
                use_container_width=True
            )

        # ===== EXAMPLE POSTS SECTION =====
        st.divider()
        st.subheader("Example Post data")
        
        # Create three columns for displaying example posts by sentiment
        col1, col2, col3 = st.columns(3)
        
        # Split data into three DataFrames by sentiment type
        df_pos, df_neu, df_neg = utlity.show_examples(df, subreddits, start_date, end_date)

        # Display top 5 posts from each sentiment category
        with col1:
            st.text("Positive Posts")
            st.dataframe(df_pos.head())  # Show first 5 positive posts
        with col2:
            st.text("Neutral Posts")
            st.dataframe(df_neu.head())  # Show first 5 neutral posts
        with col3:
            st.text("Negative Posts")
            st.dataframe(df_neg.head())  # Show first 5 negative posts

    else:
        # Prompt user to select subreddits if none are selected
        st.info("Select at least one subreddit")