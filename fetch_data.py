import praw
import pandas as pd
import time
from datetime import datetime
from prawcore.exceptions import Forbidden
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve Reddit API credentials from environment variables
# These credentials are obtained from Reddit's app registration
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
user_agent = os.getenv("USER_AGENT")

# Initialize Reddit API client with credentials
# This creates a read-only instance (no username/password needed)
reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent=user_agent
)


def get_subreddits(query):
    """
    Search for subreddits matching a query string.
    
    Args:
        query (str): Search term to find relevant subreddits
    
    Returns:
        list: List of subreddit display names matching the query
    """
    searched = reddit.subreddits.search(query)
    return [i.display_name for i in searched]


def get_posts(subreddit_name, query, limit):
    """
    Fetch posts from a specific subreddit based on a search query.
    
    Args:
        subreddit_name (str): Name of the subreddit to search in
        query (str): Search term to find relevant posts
        limit (int): Maximum number of posts to retrieve
    
    Returns:
        pd.DataFrame: DataFrame containing post titles, text, timestamps, and URLs
    """
    subreddit = reddit.subreddit(subreddit_name)
    
    # Initialize lists to store post data
    title, text, post_time, url = [], [], [], []
    
    # Search subreddit and collect post information
    for submission in subreddit.search(query, limit=limit):
        title.append(submission.title)
        text.append(submission.selftext)  # Self-text content (empty for link posts)
        post_time.append(datetime.fromtimestamp(submission.created_utc))  # Convert Unix timestamp to datetime
        url.append(submission.url)  # URL of the post or linked content

    # Return organized data as a DataFrame
    return pd.DataFrame({
        "Title": title,
        "Subreddit": subreddit_name,
        "Post Time": post_time,
        "Text": text,
        "Link": url
    })


def fetch_data(query, limit):
    """
    Main data collection function that searches multiple subreddits and aggregates results.
    Implements rate limiting and error handling.
    
    Args:
        query (str): Search term to find subreddits and posts
        limit (int): Maximum number of posts to retrieve per subreddit
    
    Returns:
        pd.DataFrame: Consolidated DataFrame with all collected posts
    """
    # Find all subreddits matching the query
    subreddits = get_subreddits(query)
    all_data = []
    
    # Iterate through each subreddit and collect posts
    for subreddit in subreddits:
        try:
            # Fetch posts from current subreddit
            df = get_posts(subreddit, query, limit)
            all_data.append(df)
            print(f"Fetched {len(df)} posts from r/{subreddit}")

            # Check Reddit API rate limits
            limits = reddit.auth.limits
            remaining = limits.get('remaining')
            reset_time = limits.get('reset_timestamp')

            # If approaching rate limit, pause until reset
            if remaining is not None and remaining < 2:
                sleep_time = max(0, reset_time - time.time())
                print(f"Approaching rate limit. Sleeping {sleep_time:.1f} seconds...")
                time.sleep(sleep_time)
            else:
                # Small delay to be respectful to Reddit's servers
                time.sleep(0.5)

        except Forbidden:
            # Skip private or banned subreddits that return Forbidden errors
            print(f"Forbidden: Skipping subreddit '{subreddit}'")
            continue

    # Combine all collected data into a single DataFrame
    if all_data:
        df = pd.concat(all_data, ignore_index=True)
        # Format post timestamps as MM/YYYY for easier readability
        df["Post Time"] = df["Post Time"].dt.strftime('%m/%Y')
        return df
    else:
        # Return empty DataFrame with correct columns if no data collected
        return pd.DataFrame(columns=["Title", "Subreddit", "Post Time", "Text"])


# Main execution block - only runs when script is executed directly
if __name__ == "__main__":
    # Test the data fetching with "hsr" query (likely "Honkai: Star Rail")
    test = fetch_data("hsr")
    # Export results to CSV file
    test.to_csv("working.csv", index=False)