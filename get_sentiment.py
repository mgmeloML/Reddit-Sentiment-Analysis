import pandas as pd
from transformers import pipeline
import torch
import re


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = pipeline(
    "text-classification",
    model="MarieAngeA13/Sentiment-Analysis-BERT",
    device=device
)

def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"u/[A-Za-z0-9_-]+", "", text)
    text = re.sub(r"r/[A-Za-z0-9_-]+", "", text)
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def sentiment(df, batch_size=2, max_length=512):
    filtered_df = df.dropna(subset=["Text"]).copy()

    filtered_df["Title + Text"] = (filtered_df["Title"] + " " + filtered_df["Text"]).apply(clean_text)

    texts = filtered_df["Title + Text"].astype(str).tolist()
    all_results = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        results = model(batch, truncation=True, max_length=max_length)
        all_results.extend(results)

    filtered_df["Sentiment"] = [r["label"] for r in all_results]

    return filtered_df

if __name__ == "__main__":
    test = pd.read_csv("working.csv")
    result_df = sentiment(test, batch_size=2) 
    result_df.to_csv("sentiment.csv", index=False)
