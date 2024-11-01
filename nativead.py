import json
import re
from collections import defaultdict
from datetime import datetime

def load_articles(filename):
    print("Loading articles...")
    with open(filename, 'r') as f:
        posts = json.load(f)
    print(f"Loaded {len(posts)} articles.")
    return posts

def clean_text(html_content):
    # Remove HTML tags
    return re.sub('<[^<]+?>', '', html_content)

def extract_native_ads(posts):
    native_ads = []
    native_ads_per_year = defaultdict(int)

    for post in posts:
        # Check if "Native Ad" is in the category names based on class_list
        categories = [cls.replace("category-", "") for cls in post.get('class_list', []) if cls.startswith("category-")]
        if "native-ad" in [category.lower() for category in categories]:  # Ensure case-insensitivity
            # Clean the content text
            post['content']['rendered'] = clean_text(post['content']['rendered'])
            native_ads.append(post)

            # Count Native Ad by year
            year = datetime.fromisoformat(post['date']).year
            native_ads_per_year[year] += 1

    print(f"Extracted {len(native_ads)} Native Ad articles.")
    print("Native Ad articles per year:")
    for year, count in sorted(native_ads_per_year.items()):
        print(f"  {year}: {count}")

    return native_ads, native_ads_per_year

def save_native_ads(filename, native_ads):
    with open(filename, 'w') as f:
        json.dump(native_ads, f, indent=4)
    print(f"Native Ad articles saved to {filename}")

def main():
    input_file = "express.json"
    output_file = "native-ad.json"

    posts = load_articles(input_file)
    native_ads, native_ads_per_year = extract_native_ads(posts)
    save_native_ads(output_file, native_ads)

if __name__ == "__main__":
    main()
