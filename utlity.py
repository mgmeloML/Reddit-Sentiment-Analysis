import pandas as pd
import plotly.express as px
from datetime import datetime

def subreddit_list(df):
    """
    Extract unique subreddit names from the DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame containing a "Subreddit" column
    
    Returns:
        np.ndarray: Array of unique subreddit names
    """
    return pd.unique(df["Subreddit"])


def valid_time_range(df):
    """
    Determine the earliest and latest post dates in the dataset.
    Useful for setting default date range filters.
    
    Args:
        df (pd.DataFrame): DataFrame containing a "Post Time" column
    
    Returns:
        tuple: (min_date, max_date) as date objects, or (None, None) if no valid dates
    """
    # Convert Post Time to datetime format
    df["Post Time"] = pd.to_datetime(df["Post Time"])
    
    # Remove any null/invalid dates
    valid_dates = df["Post Time"].dropna()
    
    # Return None if no valid dates exist
    if valid_dates.empty:
        return None, None
    
    # Return the minimum and maximum dates as date objects (not datetime)
    return valid_dates.min().date(), valid_dates.max().date()


def subreddit_range(df, subreddits):
    """
    Filter DataFrame to include only specified subreddits.
    
    Args:
        df (pd.DataFrame): DataFrame containing a "Subreddit" column
        subreddits (list): List of subreddit names to include
    
    Returns:
        pd.DataFrame: Filtered DataFrame containing only selected subreddits
    """
    df = df.loc[df["Subreddit"].isin(subreddits)]
    return df


def time_range(df, start_date, end_date):
    """
    Filter DataFrame to include only posts within a specified date range.
    
    Args:
        df (pd.DataFrame): DataFrame containing a "Post Time" column
        start_date (date): Start of date range (inclusive)
        end_date (date): End of date range (inclusive)
    
    Returns:
        pd.DataFrame: Filtered DataFrame containing only posts within the date range
    """
    # Convert Post Time to datetime, coercing errors to NaT (Not a Time)
    df['Post Time'] = pd.to_datetime(df['Post Time'], errors='coerce')
    
    # Convert date objects to datetime at start of day (00:00:00)
    start_date = datetime.combine(start_date, datetime.min.time())
    
    # Convert date objects to datetime at end of day (23:59:59.999999)
    end_date = datetime.combine(end_date, datetime.max.time())
    
    # Create boolean mask for posts within the date range
    df_new = (df["Post Time"] > start_date) & (df["Post Time"] < end_date)
    
    return df.loc[df_new]


def key_metrics(df, subreddits, start_date, end_date):
    """
    Calculate key sentiment metrics for filtered data.
    Returns total post count and breakdown by sentiment category.
    
    Args:
        df (pd.DataFrame): DataFrame with sentiment analysis results
        subreddits (list): List of subreddits to include
        start_date (date): Start of date range
        end_date (date): End of date range
    
    Returns:
        tuple: (total_posts, positive_posts, neutral_posts, negative_posts)
    """
    # Apply subreddit and time filters
    df = subreddit_range(df, subreddits)
    df = time_range(df, start_date, end_date)
    
    # Count total number of posts
    total_posts = len(df.index)
    
    # Group by sentiment and count occurrences
    df = df.groupby("Sentiment").size().reset_index(name="Count")
    
    # Extract counts for each sentiment category
    negative_posts = int(df.loc[df['Sentiment'] == "negative"]["Count"])
    neutral_posts = int(df.loc[df['Sentiment'] == "neutral"]["Count"])
    positive_posts = int(df.loc[df['Sentiment'] == "positive"]["Count"])

    return total_posts, positive_posts, neutral_posts, negative_posts


def contribution_pie_chart(df, subreddits, start_date, end_date):
    """
    Create a pie chart showing the proportion of posts from each subreddit.
    Aggregates all sentiment categories per subreddit.
    
    Args:
        df (pd.DataFrame): DataFrame with sentiment analysis results
        subreddits (list): List of subreddits to include
        start_date (date): Start of date range
        end_date (date): End of date range
    
    Returns:
        plotly.graph_objs.Figure: Interactive pie chart
    """
    # Apply filters
    df = subreddit_range(df, subreddits)
    df = time_range(df, start_date, end_date)
    
    # Count posts by subreddit and sentiment
    df = df.groupby(["Subreddit", "Sentiment"]).size().reset_index(name="count")
    
    # Aggregate across all sentiments to get total posts per subreddit
    df = df.groupby("Subreddit").sum()
    
    # Remove the Sentiment column (now meaningless after aggregation)
    df = df.drop(columns="Sentiment")
    
    return px.pie(df, values="count", names=df.index)


def contribution_bar_chart(df, subreddits, start_date, end_date):
    """
    Create a stacked bar chart showing post counts by subreddit, colored by sentiment.
    
    Args:
        df (pd.DataFrame): DataFrame with sentiment analysis results
        subreddits (list): List of subreddits to include
        start_date (date): Start of date range
        end_date (date): End of date range
    
    Returns:
        plotly.graph_objs.Figure: Interactive stacked bar chart with sentiment breakdown
    """
    # Apply filters
    df = subreddit_range(df, subreddits)
    df = time_range(df, start_date, end_date)
    
    # Count posts by subreddit and sentiment
    df = df.groupby(["Subreddit", "Sentiment"]).size().reset_index(name="count")
    
    # Additional filter (redundant since already filtered above)
    df = df.loc[df["Subreddit"].isin(subreddits)]
    
    # Create bar chart with sentiment-based coloring and value labels
    return px.bar(df, x="Subreddit", y="count", color="Sentiment", text_auto=True)


def sentiment_pie_chart(df, subreddits, start_date, end_date):
    """
    Create a pie chart showing the overall distribution of sentiments.
    
    Args:
        df (pd.DataFrame): DataFrame with sentiment analysis results
        subreddits (list): List of subreddits to include
        start_date (date): Start of date range
        end_date (date): End of date range
    
    Returns:
        plotly.graph_objs.Figure: Interactive pie chart showing sentiment distribution
    """
    # Apply filters
    df = subreddit_range(df, subreddits)
    df = time_range(df, start_date, end_date)
    
    # Count posts by sentiment category
    df = df.groupby(["Sentiment"]).size().reset_index(name="count")
    
    return px.pie(df, values="count", names="Sentiment")


def sentiment_bar_chart(df, subreddits, start_date, end_date):
    """
    Create a bar chart showing post counts by sentiment category.
    
    Args:
        df (pd.DataFrame): DataFrame with sentiment analysis results
        subreddits (list): List of subreddits to include
        start_date (date): Start of date range
        end_date (date): End of date range
    
    Returns:
        plotly.graph_objs.Figure: Interactive bar chart of sentiment counts
    """
    # Apply filters
    df = subreddit_range(df, subreddits)
    df = time_range(df, start_date, end_date)
    
    # Count posts by sentiment category
    df = df.groupby(["Sentiment"]).size().reset_index(name="count")
    
    return px.bar(df, x="Sentiment", y="count")


def sentiment_line_chart(df, subreddits, start_date, end_date):
    """
    Create a line chart showing sentiment trends over time.
    Uses spline interpolation for smooth curves.
    
    Args:
        df (pd.DataFrame): DataFrame with sentiment analysis results
        subreddits (list): List of subreddits to include
        start_date (date): Start of date range
        end_date (date): End of date range
    
    Returns:
        plotly.graph_objs.Figure: Interactive line chart with sentiment trends over time
    """
    # Apply filters
    df = subreddit_range(df, subreddits)
    df = time_range(df, start_date, end_date)
    
    # Group by sentiment and post time to count posts per day
    df = df.groupby(["Sentiment", "Post Time"]).size().reset_index(name="count")
    
    # Create line chart with markers and smooth spline curves
    return px.line(df, x="Post Time", y="count", color="Sentiment", markers=True, line_shape="spline")


def show_examples(df, subreddits, start_date, end_date):
    """
    Split filtered posts into three DataFrames based on sentiment classification.
    Useful for displaying example posts of each sentiment type.
    
    Args:
        df (pd.DataFrame): DataFrame with sentiment analysis results
        subreddits (list): List of subreddits to include
        start_date (date): Start of date range
        end_date (date): End of date range
    
    Returns:
        tuple: (positive_df, neutral_df, negative_df) - Three separate DataFrames
    """
    # Apply filters
    df = subreddit_range(df, subreddits)
    df = time_range(df, start_date, end_date)
    
    # Remove the combined text column (used during sentiment analysis)
    df = df.drop(axis=1, columns="Title + Text")
    
    # Standardize sentiment labels to lowercase for consistent filtering
    df["Sentiment"] = df["Sentiment"].str.lower()
    
    # Split into three DataFrames based on sentiment
    df_pos = df[df["Sentiment"] == "positive"]
    df_neu = df[df["Sentiment"] == "neutral"]
    df_neg = df[df["Sentiment"] == "negative"]
    
    return df_pos, df_neu, df_neg