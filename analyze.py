import json
import re
import requests
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
    text = re.sub('<[^<]+?>', '', html_content)  # Remove HTML tags
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
    stats = defaultdict(lambda: defaultdict(list))  # {year-month: {category: [metrics]}}

    print("Analyzing articles by category and month...")
    for idx, post in enumerate(posts, start=1):
        year_month = datetime.fromisoformat(post['date']).strftime("%Y-%m")
        categories = get_categories(post['categories'])
        text = clean_text(post['content']['rendered'])

        if text:
            metrics = analyze_text(text)
            for category in categories:
                stats[year_month][category].append(metrics)

        if idx % 100 == 0:
            print(f"Processed {idx} articles...")

    print("Calculating statistics by category and month...")
    monthly_stats = defaultdict(dict)
    for year_month, categories in stats.items():
        for category, articles in categories.items():
            monthly_stats[year_month][category] = {
                "avg_word_count": np.mean([a["word_count"] for a in articles]),
                "avg_sentence_count": np.mean([a["sentence_count"] for a in articles]),
                "avg_sentence_length": np.mean([a["avg_sentence_length"] for a in articles]),
                "avg_lexical_diversity": np.mean([a["lexical_diversity"] for a in articles])
            }
        print(f"Calculated statistics for {year_month}")

    return monthly_stats

def save_stats_to_excel(monthly_stats, filename="category_monthly_stats.xlsx"):
    print(f"Saving statistics to {filename}...")
    rows = []
    for year_month, categories in monthly_stats.items():
        for category, stats in categories.items():
            row = {"month": year_month, "category": category}
            row.update(stats)
            rows.append(row)
    df = pd.DataFrame(rows)
    df.to_excel(filename, index=False)
    print(f"Statistics saved to {filename}")

def plot_stylometry_features(monthly_stats):
    features = ["avg_word_count", "avg_sentence_count", "avg_sentence_length", "avg_lexical_diversity"]
    monthly_data = defaultdict(lambda: defaultdict(list))

    # Prepare data for plotting
    print("Preparing data for plotting...")
    for year_month, categories in sorted(monthly_stats.items()):
        for category, stats in categories.items():
            for feature in features:
                monthly_data[feature][category].append((year_month, stats[feature]))

    # Generate line charts for each feature
    print("Generating plots for each stylometry feature...")
    for feature, data in monthly_data.items():
        plt.figure(figsize=(10, 6))
        for category, values in data.items():
            months, values = zip(*values)
            plt.plot(months, values, label=category)

        plt.title(f"{feature.replace('_', ' ').title()} Over Time")
        plt.xlabel("Month")
        plt.ylabel(feature.replace('_', ' ').title())
        plt.xticks(rotation=45)
        plt.legend(loc="best")
        plt.tight_layout()
        plt.savefig(f"{feature}_by_category.png")
        plt.close()
        print(f"Plot saved for {feature}")

def main(filename):
    posts = load_articles(filename)
    monthly_stats = analyze_articles_by_category_and_month(posts)
    save_stats_to_excel(monthly_stats)
    plot_stylometry_features(monthly_stats)

if __name__ == "__main__":
    main("express.json")
