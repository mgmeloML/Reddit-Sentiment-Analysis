import praw
import pandas as pd
import time
from datetime import datetime
from prawcore.exceptions import Forbidden
import os
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
user_agent = os.getenv("USER_AGENT")


reddit = praw.Reddit(
    client_id = client_id,
    client_secret = client_secret,
    user_agent = user_agent
)

def get_subreddits(query):
    searched = reddit.subreddits.search(query)
    return [i.display_name for i in searched]

def get_posts(subreddit_name, query, limit):
    subreddit = reddit.subreddit(subreddit_name)
    title, text, post_time, url = [], [], [], []
    
    for submission in subreddit.search(query, limit=limit):
        title.append(submission.title)
        text.append(submission.selftext)
        post_time.append(datetime.fromtimestamp(submission.created_utc))
        url.append(submission.url)

    return pd.DataFrame({
        "Title": title,
        "Subreddit": subreddit_name,
        "Post Time": post_time,
        "Text": text,
        "Link": url
    })

def fetch_data(query, limit):
    subreddits = get_subreddits(query)
    all_data = []
    
    for subreddit in subreddits:
        try:
            df = get_posts(subreddit, query, limit)
            all_data.append(df)
            print(f"Fetched {len(df)} posts from r/{subreddit}")

            limits = reddit.auth.limits
            remaining = limits.get('remaining')
            reset_time = limits.get('reset_timestamp')

            if remaining is not None and remaining < 2:
                sleep_time = max(0, reset_time - time.time())
                print(f"Approaching rate limit. Sleeping {sleep_time:.1f} seconds...")
                time.sleep(sleep_time)
            else:
                time.sleep(0.5)

        except Forbidden:
            print(f"Forbidden: Skipping subreddit '{subreddit}'")
            continue

    if all_data:
        df = pd.concat(all_data, ignore_index=True)
        df["Post Time"] = df["Post Time"].dt.strftime('%m/%Y')
        return df
    else:
        return pd.DataFrame(columns=["Title", "Subreddit", "Post Time", "Text"])

if __name__ == "__main__":
    test = fetch_data("hsr")
    test.to_csv("working.csv", index=False)