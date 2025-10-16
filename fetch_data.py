import praw
import pandas as pd
import time
from datetime import datetime
from prawcore.exceptions import Forbidden

reddit = praw.Reddit(
    client_id="wj7PoB3ttKVVo5_GWuOTKg",
    client_secret="RxFAlKUfMVIbMkn9hs_Rh05KZQb6SQ",
    user_agent="mgmeloML.reddit_sentiment:v4.3 (by /u/Dazzling_Papaya821; +https://github.com/mgmeloML)"
)

def get_subreddits(query):
    searched = reddit.subreddits.search(query)
    return [i.display_name for i in searched]

def get_posts(subreddit_name, query):
    subreddit = reddit.subreddit(subreddit_name)
    title, text, post_time, url = [], [], [], []
    
    for submission in subreddit.search(query, limit=None):
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

def fetch_data(query):
    subreddits = get_subreddits(query)
    all_data = []
    
    for subreddit in subreddits:
        try:
            df = get_posts(subreddit, query)
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