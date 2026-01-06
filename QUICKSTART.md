# Quick Start Guide

Get up and running with the One Piece Character Scraper in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- Chrome browser (for Selenium mode)
- Internet connection

## Installation

### 1. Clone or Download
```bash
git clone https://github.com/yourusername/onepiece-scraper.git
cd onepiece-scraper
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Basic Usage

### Option 1: Quick Test (10 characters)

```python
from src.onepiece_scraper import OnePieceScraper

# Initialize scraper
scraper = OnePieceScraper(use_selenium=False)

# Test with a few characters
test_characters = ["Monkey_D._Luffy", "Roronoa_Zoro", "Nami"]

# Scrape
scraper.scrape_multiple(
    character_list=test_characters,
    output_file='output/test_output.json',
    delay=2
)
```

### Option 2: Full Scraping (1500+ characters)

```bash
# Step 1: Discover all canon characters
python src/onepiece_scraper.py --discover

# Step 2: Scrape with Selenium (recommended)
python src/onepiece_scraper.py --selenium --delay 3 --batch-size 50
```

### Option 3: Resume Interrupted Scrape

The scraper automatically resumes from where it left off:

```bash
# Just run the same command again
python src/onepiece_scraper.py --selenium --delay 3
```

## Understanding the Output

After scraping, you'll find:

```
output/
├── characters_raw.json          # All scraped data
├── scraping_failures.json       # Any failed characters
└── progress/
    ├── batch_0001.json          # Incremental saves
    ├── batch_0002.json
    └── ...
```

## Sample Output

Each character looks like this:

```json
{
  "source_name": "Monkey_D._Luffy",
  "source_url": "https://onepiece.fandom.com/wiki/Monkey_D._Luffy",
  "Japanese Name": "モンキー・D・ルフィ",
  "Romanized Name": "Monkī Dī Rufi",
  "Debut": "Chapter 1; Episode 1",
  "Affiliations": "Straw Hat Pirates",
  "Age": "19",
  "Birthday": "May 5th",
  "Bounty": "3,000,000,000"
}
```

## Customization

Edit `config.py` to change defaults:

```python
# Adjust these values
DEFAULT_DELAY = 3              # Seconds between requests
DEFAULT_BATCH_SIZE = 50        # Characters per batch
USE_SELENIUM = True            # Use Selenium by default
```

## Common Issues

### Issue: Bot Detection
**Solution:** Use Selenium mode
```bash
python src/onepiece_scraper.py --selenium
```

### Issue: Slow Scraping
**Solution:** Reduce delay (but be respectful!)
```bash
python src/onepiece_scraper.py --delay 2
```

### Issue: Chrome Driver Error
**Solution:** Install Chrome or update `webdriver-manager`
```bash
pip install --upgrade webdriver-manager
```

## Next Steps

1. ✅ Review scraped data: `output/characters_raw.json`
2. ✅ Explore data cleaning: `notebooks/data-prep.ipynb`
3. ✅ Check failures: `output/scraping_failures.json`
4. ✅ Customize scraper: Edit `config.py`

## Resources

- 📖 [Full Documentation](README.md)
- 🤝 [Contributing Guide](CONTRIBUTING.md)
- 📊 [Project Summary](PROJECT_SUMMARY.md)

## Need Help?

Open an issue on GitHub or check the FAQ in the main README.

---

Happy scraping! 🏴‍☠️
