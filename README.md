# One Piece Character Scraper

A robust and production-ready web scraper for extracting character data from the One Piece Fandom Wiki. This project demonstrates web scraping best practices, anti-bot detection handling, and clean data pipeline architecture.

## Features

- **Dual Scraping Methods**: Supports both `requests` (lightweight) and `Selenium` (anti-bot detection)
- **Progress Tracking**: Batch-based saving with automatic resume capability
- **Rate Limiting**: Configurable delays to respect server resources
- **Error Handling**: Comprehensive retry logic and failure logging
- **Clean Architecture**: Modular, object-oriented design

## Project Structure

```
onepiece-scraper/
├── src/
│   └── onepiece_scraper.py    # Main scraper class
├── data/
│   ├── raw/                   # Raw input data
│   │   ├── canon_character_list.txt
│   │   └── all-characters-api.json
│   └── processed/             # Cleaned/processed data
│       ├── onepiece_cleaned_stage1.csv
│       └── onepiecedataset.parquet
├── output/
│   ├── characters_raw.json    # Final scraped data
│   └── progress/              # Batch progress files, can also be use for sampling
├── notebooks/
│   └── data-prep.ipynb        # Data exploration & cleaning
├── requirements.txt           # Python dependencies
├── .gitignore                # Git ignore patterns
└── README.md                 # This file
```

## Installation

### Prerequisites

- Python 3.8+
- Chrome browser (for Selenium mode)

### Setup

1. Clone this repository:
```bash
git clone https://github.com/yourusername/onepiece-scraper.git
cd onepiece-scraper
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

**Discover canon characters** (first-time setup):
```bash
python src/onepiece_scraper.py --discover
```

**Scrape using requests** (lightweight, may hit bot detection):
```bash
python src/onepiece_scraper.py --delay 3 --batch-size 50
```

**Scrape using Selenium** (bypasses bot detection, recommended):
```bash
python src/onepiece_scraper.py --selenium --delay 3 --batch-size 50
```

### Python API

```python
from src.onepiece_scraper import OnePieceScraper

# Initialize scraper
scraper = OnePieceScraper(use_selenium=True, headless=True)

# Discover characters
characters = scraper.discover_canon_characters()

# Scrape multiple characters
scraper.scrape_multiple(
    character_list=characters,
    output_file='output/characters.json',
    delay=3,
    batch_size=50
)
```

## Data Output

### Character Data Format

Each character entry contains:

```json
{
  "source_name": "Monkey_D._Luffy",
  "source_url": "https://onepiece.fandom.com/wiki/Monkey_D._Luffy",
  "Japanese Name": "モンキー・D・ルフィ",
  "Romanized Name": "Monkī Dī Rufi",
  "Official English Name": "Monkey D. Luffy",
  "Debut": "Chapter 1; Episode 1",
  "Affiliations": "Straw Hat Pirates",
  "Occupations": "Pirate Captain",
  "Age": "19",
  "Birthday": "May 5th",
  "Status": "Alive",
  "Bounty": "3,000,000,000"
}
```

## Technical Highlights

### Anti-Bot Detection

- **User-Agent Rotation**: Mimics real browser requests
- **Selenium Integration**: Uses real Chrome browser to bypass JavaScript challenges
- **Rate Limiting**: Configurable delays between requests
- **Exponential Backoff**: Automatic retry with increasing delays

### Robust Error Handling

- Connection timeout handling
- HTTP error status detection
- Malformed HTML handling
- Progress checkpointing (resume from failure)

### Scalability

- Batch-based processing (memory efficient)
- Progress tracking (resume interrupted scrapes)
- Concurrent request support (requests.Session)
- Modular design (easy to extend)

## Performance

- **Scraping Speed**: ~15-20 characters/minute (with 3s delay)
- **Success Rate**: ~95% with Selenium, ~70% with requests
- **Memory Usage**: <100MB (batch processing)
- **Data Volume**: Successfully scraped 1,500+ characters

## Development

### Project Evolution

1. **Initial Exploration**: Simple requests-based scraper
2. **Bot Detection**: Implemented Selenium for bypass
3. **Progress Tracking**: Added batch saving and resume
4. **Modularization**: Refactored into clean OOP design
5. **Production Ready**: Error handling, logging, CLI interface

### Data Processing Pipeline

1. **Discovery**: Scrape character list from wiki index
2. **Extraction**: Parse character infoboxes (Statistics + Portrayal)
3. **Batch Saving**: Save in chunks for progress tracking
4. **Consolidation**: Merge batches into final dataset
5. **Cleaning**: Process and standardize data (see `notebooks/data-prep.ipynb`)

## Lessons Learned

- **Respect robots.txt**: Always check and honor website policies
- **Handle Bot Detection**: Modern sites use sophisticated challenges
- **Progressive Enhancement**: Start simple, add complexity as needed
- **Fail Gracefully**: Comprehensive error handling is crucial
- **Track Progress**: Long-running scrapes need checkpointing

## Future Improvements

- [ ] Async scraping with `aiohttp` for better performance
- [ ] Database integration
- [ ] API endpoint for querying scraped data
- [ ] Docker containerization
- [ ] Automated testing suite
- [ ] Cloud deployment (AWS Lambda/Google Cloud Functions)

## Legal & Ethics

This scraper is for educational purposes only. When using:

- Review and respect the website's `robots.txt`
- Use reasonable rate limiting
- Don't overload the server
- Give proper attribution to data sources
- Consider using official APIs when available

## License

MIT License - See LICENSE file for details

## Contact

**Author**: Kareem Alnassag
**GitHub**: https://github.com/kalnassag
**LinkedIn**: https://www.linkedin.com/in/kareemnassag/
**Email**: kalnassag@proton.me

## Acknowledgments

- Data source: [One Piece Fandom Wiki](https://onepiece.fandom.com/)
- Built with: BeautifulSoup, Selenium, Requests and Claude Code
- Inspiration: Love for One Piece and data science

---

*Made with ❤️ for the One Piece community*
