
# Express
Python scripts to analyze articles from [exxpress](https://exxpress.at/) with basic stylometric features, possibly identifying stylistic changes over time (e.g., from generative AI use).

## Features
- Retrieve all articles from `exxpress.at` via the WordPress REST API.
- Count articles per year.
- Extract and analyze all "Native Ad" articles.
- Perform stylometric analysis on categories (e.g., average word count, sentence count, sentence length, and lexical diversity) by month.

## Setup
You'll need [Python](https://www.python.org/downloads/) (version 3.7 or higher recommended). Install dependencies within a virtual environment (venv) for easy management.

### Step 1: Clone this repository
First, download or clone the repository to your computer.

```bash
git clone https://github.com/yourusername/express.git
cd express
```

### Step 2: Set up and activate a virtual environment
Set up a Python virtual environment (venv) to manage dependencies.

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install dependencies
With the virtual environment activated, install the necessary packages.

```bash
pip install -r requirements.txt
```

Or manually install the packages:
```bash
pip install requests nltk pandas matplotlib
```

### Step 4: Download NLTK resources
Some NLTK resources are required for tokenizing and stopwords. Run the script below to ensure all resources are downloaded.

```python
python3 -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('punkt_tab')"
```

## Usage

### 1. Download and Save Articles
Run the `crawl.py` script to download all articles up to the current date from the exxpress API. This saves a JSON file named `express.json` with the downloaded articles.

```bash
python3 crawl.py
```

### 2. Count Articles per Year
Run the `count.py` script to output the number of articles published each year.

```bash
python3 count.py
```

### 3. Extract Native Ads
To extract all articles tagged as "Native Ad" into a separate JSON file, run `nativead.py`. This will create a file called `native-ad.json` with only Native Ad articles.

```bash
python3 nativead.py
```

### 4. Analyze Stylometry
Run the `analyze.py` script to analyze each article's stylometric features per category per month. This outputs:
- `category_monthly_stats.xlsx` – An Excel file with monthly statistics for each category.
- Line charts for each stylometric feature saved as `.png` files.

```bash
python3 analyze.py
```

## Output
1. **category_monthly_stats.xlsx**: Monthly statistics for each category, with features like average word count, sentence count, sentence length, and lexical diversity.
2. **Feature Plots**: PNG images, each plotting a stylometric feature over time for different categories.
3. **native-ad.json**: A JSON file containing only Native Ad articles.

## License
This project is licensed under the MIT License.
