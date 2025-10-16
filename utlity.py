import pandas as pd
import plotly.express as px
from datetime import datetime

def subreddit_list(df):
  return pd.unique(df["Subreddit"])

def valid_time_range(df):
    df["Post Time"] = pd.to_datetime(df["Post Time"])
    valid_dates = df["Post Time"].dropna()
    if valid_dates.empty:
        return None, None
    return valid_dates.min().date(), valid_dates.max().date()

def subreddit_range(df, subreddits):
  df = df.loc[df["Subreddit"].isin(subreddits)]
  return df
  
def time_range(df, start_date, end_date):
  df['Post Time'] = pd.to_datetime(df['Post Time'], errors='coerce')
  start_date = datetime.combine(start_date, datetime.min.time())
  end_date = datetime.combine(end_date, datetime.max.time())
  df_new = (df["Post Time"] > start_date) & (df["Post Time"] < end_date)
  return df.loc[df_new]

def key_metrics(df, subreddits, start_date, end_date):
  df = subreddit_range(df, subreddits)
  df = time_range(df, start_date, end_date)
  total_posts = len(df.index)
  df = df.groupby("Sentiment").size().reset_index(name="Count")
  negative_posts = int(df.loc[df['Sentiment'] == "negative"]["Count"])
  neutral_posts = int(df.loc[df['Sentiment'] == "neutral"]["Count"])
  positive_posts = int(df.loc[df['Sentiment'] == "positive"]["Count"])

  return total_posts, positive_posts, neutral_posts, negative_posts


def contribution_pie_chart(df, subreddits, start_date, end_date):
  df = subreddit_range(df, subreddits)
  df = time_range(df, start_date, end_date)
  df = df.groupby(["Subreddit", "Sentiment"]).size().reset_index(name="count")
  df = df.groupby("Subreddit").sum()
  df = df.drop(columns="Sentiment")
  return px.pie(df, values="count", names=df.index)


def contribution_bar_chart(df, subreddits, start_date, end_date):
  df = subreddit_range(df, subreddits)
  df = time_range(df, start_date, end_date)
  df = df.groupby(["Subreddit", "Sentiment"]).size().reset_index(name="count")
  df = df.loc[df["Subreddit"].isin(subreddits)]
  return px.bar(df, x="Subreddit", y="count", color="Sentiment", text_auto=True)

def sentiment_pie_chart(df, subreddits, start_date, end_date):
  df = subreddit_range(df, subreddits)
  df = time_range(df, start_date, end_date)
  df = df.groupby(["Sentiment"]).size().reset_index(name="count")
  return px.pie(df, values="count", names="Sentiment")

def sentiment_bar_chart(df, subreddits, start_date, end_date):
  df = subreddit_range(df, subreddits)
  df = time_range(df, start_date, end_date)
  df = df.groupby(["Sentiment"]).size().reset_index(name="count")
  return px.bar(df, x="Sentiment", y="count")


def sentiment_line_chart(df, subreddits, start_date, end_date):
  df = subreddit_range(df, subreddits)
  df = time_range(df, start_date, end_date)
  df = df.groupby(["Sentiment", "Post Time"]).size().reset_index(name="count")
  return px.line(df, x="Post Time", y="count", color="Sentiment", markers=True, line_shape="spline")

def show_examples(df, subreddits, start_date, end_date):
  df = subreddit_range(df, subreddits)
  df = time_range(df, start_date, end_date)
  df.drop(axis=1,columns="Title + Text")
  df["Sentiment"] = df["Sentiment"].str.lower()
  df_pos = df[df["Sentiment"] == "positive"]
  df_neu = df[df["Sentiment"] == "neutral"]
  df_neg = df[df["Sentiment"] == "negative"]
  return df_pos, df_neu, df_neg