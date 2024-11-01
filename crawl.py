import requests
import json

all_posts = []
url = "https://exxpress.at/api/wp/v2/posts/"

for page in range(1, 509):
    response = requests.get(f"{url}?per_page=100&page={page}")
    if response.status_code != 200:
        break
    posts = response.json()
    if not posts:
        break
    all_posts.extend(posts)
    print(f"Processed page {page}")

print(f"Total posts collected: {len(all_posts)}")

with open("express.json", "w") as f:
    json.dump(all_posts, f)