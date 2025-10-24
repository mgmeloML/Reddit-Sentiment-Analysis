import pandas as pd
from transformers import pipeline
import torch
import re


# Determine if GPU (CUDA) is available, otherwise use CPU
# Using GPU significantly speeds up sentiment analysis
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load pre-trained BERT sentiment analysis model from Hugging Face
# This model classifies text into sentiment categories (positive/negative/neutral)
model = pipeline(
    "text-classification",
    model="MarieAngeA13/Sentiment-Analysis-BERT",
    device=device
)


def clean_text(text):
    """
    Clean and normalize text data for sentiment analysis.
    Removes URLs, Reddit-specific formatting, and non-ASCII characters.
    
    Args:
        text (str): Raw text to be cleaned
    
    Returns:
        str: Cleaned and normalized text
    """
    # Convert all text to lowercase for consistency
    text = text.lower()
    
    # Remove HTTP/HTTPS URLs and www links
    text = re.sub(r"http\S+|www\S+", "", text)
    
    # Remove Reddit username mentions (e.g., u/username)
    text = re.sub(r"u/[A-Za-z0-9_-]+", "", text)
    
    # Remove Reddit subreddit mentions (e.g., r/subreddit)
    text = re.sub(r"r/[A-Za-z0-9_-]+", "", text)
    
    # Remove non-ASCII characters (emojis, special symbols, etc.)
    # Replaces them with a single space
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    
    # Collapse multiple whitespace characters into a single space
    # and remove leading/trailing whitespace
    text = re.sub(r"\s+", " ", text).strip()
    
    return text


def sentiment(df, batch_size=2, max_length=512):
    """
    Perform sentiment analysis on a DataFrame containing Reddit posts.
    Processes posts in batches for efficiency.
    
    Args:
        df (pd.DataFrame): DataFrame with "Title" and "Text" columns
        batch_size (int): Number of texts to process simultaneously (default: 2)
        max_length (int): Maximum token length for BERT model (default: 512)
    
    Returns:
        pd.DataFrame: Original DataFrame with added "Sentiment" column
    """
    # Remove rows with missing text data and create a copy to avoid modifying original
    filtered_df = df.dropna(subset=["Text"]).copy()

    # Combine title and text, then clean the combined text
    # This provides more context for sentiment analysis
    filtered_df["Title + Text"] = (filtered_df["Title"] + " " + filtered_df["Text"]).apply(clean_text)

    # Convert combined text to list for batch processing
    texts = filtered_df["Title + Text"].astype(str).tolist()
    all_results = []

    # Process texts in batches to manage memory and improve efficiency
    for i in range(0, len(texts), batch_size):
        # Extract current batch of texts
        batch = texts[i:i + batch_size]
        
        # Run sentiment analysis on the batch
        # truncation=True ensures texts longer than max_length are cut off
        results = model(batch, truncation=True, max_length=max_length)
        
        # Accumulate results from all batches
        all_results.extend(results)

    # Extract sentiment labels and add as new column to DataFrame
    filtered_df["Sentiment"] = [r["label"] for r in all_results]

    return filtered_df


# Main execution block - only runs when script is executed directly
if __name__ == "__main__":
    # Load the CSV file created by the Reddit scraper
    test = pd.read_csv("working.csv")
    
    # Perform sentiment analysis with batch size of 2
    # Small batch size is conservative for memory management
    result_df = sentiment(test, batch_size=2) 
    
    # Save results to new CSV file with sentiment labels
    result_df.to_csv("sentiment.csv", index=False)