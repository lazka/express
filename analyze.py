import json
import re
import requests
from bs4 import BeautifulSoup
import html
from collections import defaultdict
from datetime import datetime
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Ensure necessary NLTK resources are downloaded
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')

# Set German stopwords
stop_words = set(stopwords.words("german"))

# Cache for category ID to name mapping
category_id_to_name = {}

def load_articles(filename):
    print("Loading articles...")
    with open(filename, 'r') as f:
        posts = json.load(f)
    print(f"Loaded {len(posts)} articles.")
    return posts

def clean_text(html_content):
    # Remove HTML tags and decode HTML entities
    text = BeautifulSoup(html_content, "html.parser").get_text()
    text = html.unescape(text)
    text = re.sub(r'\[.*?\]', '', text)  # Remove shortcodes
    return text

def fetch_category_name(category_id):
    if category_id not in category_id_to_name:
        print(f"Fetching category name for ID {category_id}...")
        try:
            response = requests.get(f"https://exxpress.at/api/wp/v2/categories/{category_id}")
            response.raise_for_status()
            category_data = response.json()
            category_name = category_data.get("name", f"Unknown-{category_id}")
            category_id_to_name[category_id] = category_name
        except requests.RequestException:
            category_id_to_name[category_id] = f"Unknown-{category_id}"
    return category_id_to_name[category_id]

def get_categories(category_ids):
    return [fetch_category_name(cat_id) for cat_id in category_ids]

def analyze_text(text):
    words = word_tokenize(text)  # No language specified
    sentences = sent_tokenize(text)  # No language specified
    filtered_words = [word.lower() for word in words if word.isalnum() and word.lower() not in stop_words]

    word_count = len(filtered_words)
    sentence_count = len(sentences)
    avg_sentence_length = word_count / sentence_count if sentence_count else 0
    lexical_diversity = len(set(filtered_words)) / word_count if word_count else 0

    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "avg_sentence_length": avg_sentence_length,
        "lexical_diversity": lexical_diversity
    }

def analyze_articles_by_category_and_month(posts):
    stats = defaultdict(lambda: defaultdict(list))  # {month: {category: [metrics]}}

    print("Analyzing articles by category and month...")
    for idx, post in enumerate(posts, start=1):
        date = datetime.fromisoformat(post['date'])
        month = f"{date.year}-{date.month:02d}"
        categories = get_categories(post['categories'])
        text = clean_text(post['content']['rendered'])

        if text:
            metrics = analyze_text(text)
            for category in categories:
                stats[month][category].append(metrics)

        if idx % 100 == 0:
            print(f"Processed {idx} articles...")

    print("Calculating statistics by category and month...")
    monthly_stats = defaultdict(dict)
    for month, categories in stats.items():
        for category, articles in categories.items():
            monthly_stats[month][category] = {
                "avg_word_count": np.mean([a["word_count"] for a in articles]),
                "avg_sentence_count": np.mean([a["sentence_count"] for a in articles]),
                "avg_sentence_length": np.mean([a["avg_sentence_length"] for a in articles]),
                "avg_lexical_diversity": np.mean([a["lexical_diversity"] for a in articles])
            }
            print(f"Month {month}, Category {category} statistics calculated.")

    return monthly_stats

def save_stats_to_excel(stats, filename="category_monthly_stats.xlsx"):
    # Flatten the dictionary and save as DataFrame
    rows = []
    for month, categories in stats.items():
        for category, data in categories.items():
            rows.append({"month": month, "category": category, **data})

    df = pd.DataFrame(rows)
    df.to_excel(filename, index=False)
    print(f"Saved monthly statistics to {filename}")

def plot_stylometric_features(stats):
    # Generate line plots for each stylometric feature
    features = ["avg_word_count", "avg_sentence_count", "avg_sentence_length", "avg_lexical_diversity"]

    for feature in features:
        plt.figure()
        for category in set(cat for cats in stats.values() for cat in cats):
            data = {
                month: values[category][feature]
                for month, values in stats.items()
                if category in values
            }
            plt.plot(list(data.keys()), list(data.values()), label=category)

        plt.xlabel("Month")
        plt.ylabel(feature.replace("_", " ").title())
        plt.title(f"{feature.replace('_', ' ').title()} Over Time by Category")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"{feature}_plot.png")
        print(f"Saved plot {feature}_plot.png")

def main(filename):
    posts = load_articles(filename)
    monthly_stats = analyze_articles_by_category_and_month(posts)
    save_stats_to_excel(monthly_stats)
    plot_stylometric_features(monthly_stats)

if __name__ == "__main__":
    main("express.json")
