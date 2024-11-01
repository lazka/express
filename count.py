import json
import sys
from collections import Counter
from datetime import datetime

def count_articles_by_year(filename):
    with open(filename, 'r') as f:
        posts = json.load(f)

    # Sort posts by date to get the first article by date
    # posts.sort(key=lambda x: datetime.fromisoformat(x['date']))

    years = [datetime.fromisoformat(post['date']).year for post in posts]
    year_counts = Counter(years)

    for year, count in sorted(year_counts.items()):
        print(f"{year}: {count}")

    # Save the first article by date to "first.json"
    if posts:
        with open("first.json", "w") as first_file:
            json.dump(posts[0], first_file, indent=4)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <filename>")
    else:
        count_articles_by_year(sys.argv[1])
