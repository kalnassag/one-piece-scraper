"""
One Piece Character Scraper
============================
A robust web scraper for extracting character data from the One Piece Fandom Wiki.
Supports both Selenium (anti-bot) and Requests-based scraping methods.

Author: Portfolio Project
License: MIT
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import os
from datetime import datetime
from urllib.parse import unquote

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("Warning: Selenium not available. Install with: pip install selenium webdriver-manager")


class OnePieceScraper:
    """Main scraper class for One Piece character data."""

    def __init__(self, use_selenium=False, headless=True):
        """
        Initialize the scraper.

        Args:
            use_selenium (bool): Use Selenium instead of requests (bypasses bot detection)
            headless (bool): Run browser in headless mode (Selenium only)
        """
        self.use_selenium = use_selenium
        self.headless = headless
        self.driver = None
        self.session = requests.Session()

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }

        if use_selenium:
            if not SELENIUM_AVAILABLE:
                raise ImportError("Selenium is required but not installed")
            self._setup_selenium()

    def _setup_selenium(self):
        """Setup Selenium WebDriver with anti-detection measures."""
        options = Options()

        if self.headless:
            options.add_argument('--headless=new')

        # Anti-detection settings
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        # Browser-like settings
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument(f'user-agent={self.headers["User-Agent"]}')

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def fetch_character_page(self, character_name, max_retries=3):
        """
        Fetch a character page from the wiki.

        Args:
            character_name (str): Character name (URL format)
            max_retries (int): Number of retry attempts

        Returns:
            BeautifulSoup: Parsed HTML or None if failed
        """
        if self.use_selenium:
            return self._fetch_with_selenium(character_name, max_retries)
        else:
            return self._fetch_with_requests(character_name, max_retries)

    def _fetch_with_requests(self, character_name, max_retries):
        """Fetch using requests library."""
        url = f"https://onepiece.fandom.com/wiki/{character_name}"

        for attempt in range(1, max_retries + 1):
            try:
                response = self.session.get(url, headers=self.headers, timeout=30)

                # Check for bot challenge
                if len(response.content) < 5000 or 'Client Challenge' in response.text:
                    if attempt < max_retries:
                        wait_time = attempt * 2
                        print(f"  🔄 Bot detection, retry {attempt}/{max_retries} after {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    return None

                response.raise_for_status()
                return BeautifulSoup(response.content, 'lxml')

            except requests.exceptions.RequestException as e:
                if attempt < max_retries:
                    wait_time = attempt * 2
                    print(f"  🔄 Error, retry {attempt}/{max_retries} after {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"  ❌ Request failed: {e}")
                    return None

        return None

    def _fetch_with_selenium(self, character_name, max_retries):
        """Fetch using Selenium."""
        url = f"https://onepiece.fandom.com/wiki/{character_name}"

        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "portable-infobox"))
            )
            time.sleep(2)  # Let page fully render

            html = self.driver.page_source
            if 'Client Challenge' in html or len(html) < 5000:
                return None

            return BeautifulSoup(html, 'lxml')

        except (TimeoutException, WebDriverException) as e:
            print(f"  ❌ Selenium error: {e}")
            return None

    def extract_character_data(self, soup, character_name):
        """
        Extract character data from infobox.

        Args:
            soup (BeautifulSoup): Parsed HTML
            character_name (str): Character name for metadata

        Returns:
            dict: Character data or None if extraction failed
        """
        if not soup:
            return None

        infobox = soup.find('aside', class_='portable-infobox')
        if not infobox:
            return None

        character_data = {
            'source_name': character_name,
            'source_url': f"https://onepiece.fandom.com/wiki/{character_name}"
        }

        # Find Statistics and Portrayal sections
        sections = infobox.find_all('h2', class_='pi-header')
        target_sections = ['Statistics', 'Portrayal']

        for section in sections:
            section_name = section.get_text(strip=True)

            if section_name in target_sections:
                current_element = section.find_next_sibling()

                while current_element:
                    # Stop at next section header
                    if current_element.name == 'h2' and 'pi-header' in current_element.get('class', []):
                        break

                    # Process data items
                    if current_element.name == 'div' and 'pi-item' in current_element.get('class', []):
                        label = current_element.find('h3', class_='pi-data-label')
                        value = current_element.find('div', class_='pi-data-value')

                        if label and value:
                            label_text = label.get_text(strip=True).replace(':', '')
                            value_text = value.get_text(strip=True)
                            character_data[label_text] = value_text

                    current_element = current_element.find_next_sibling()

        # Return None if no data was extracted
        if len(character_data) <= 2:
            return None

        return character_data

    def discover_canon_characters(self):
        """
        Discover all canon characters from the master list page.

        Returns:
            list: Character names in URL format
        """
        list_url = "https://onepiece.fandom.com/wiki/List_of_Canon_Characters"

        print("Fetching canon character list...")

        try:
            response = self.session.get(list_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'lxml')

            content = soup.find('div', class_='mw-parser-output')
            if not content:
                print("Could not find main content")
                return []

            table = content.find('table', class_='sortable')
            if not table:
                print("Could not find character table")
                return []

            character_names = []
            rows = table.find_all('tr')[1:]  # Skip header

            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    link = cells[1].find('a', href=True)
                    if link:
                        href = link.get('href')
                        if href.startswith('/wiki/'):
                            page_name = unquote(href.replace('/wiki/', ''))
                            if ':' not in page_name and page_name not in character_names:
                                character_names.append(page_name)

            print(f"✅ Discovered {len(character_names)} canon characters")
            return character_names

        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching character list: {e}")
            return []

    def scrape_multiple(self, character_list, output_file='output/characters.json',
                       delay=3, batch_size=50, progress_dir='output/progress'):
        """
        Scrape multiple characters with progress tracking.

        Args:
            character_list (list): List of character names to scrape
            output_file (str): Path to consolidated output file
            delay (int): Delay between requests in seconds
            batch_size (int): Characters per batch file
            progress_dir (str): Directory for batch progress files
        """
        os.makedirs(progress_dir, exist_ok=True)
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # Load already scraped characters
        already_scraped = self._load_progress(progress_dir, output_file)
        to_scrape = [c for c in character_list if c not in already_scraped]

        print(f"\n{'='*60}")
        print(f"📋 Total characters: {len(character_list)}")
        print(f"✅ Already scraped: {len(already_scraped)}")
        print(f"🎯 Need to scrape: {len(to_scrape)}")
        print(f"{'='*60}\n")

        if not to_scrape:
            print("Nothing to scrape! All characters already collected.")
            return

        current_batch = []
        batch_num = len(already_scraped) // batch_size
        success_count = 0
        fail_count = 0
        failures = []
        start_time = time.time()

        try:
            for i, character_name in enumerate(to_scrape, 1):
                elapsed = time.time() - start_time
                rate = i / elapsed if elapsed > 0 else 0
                eta_minutes = ((len(to_scrape) - i) / rate / 60) if rate > 0 else 0

                print(f"\n[{i}/{len(to_scrape)}] {character_name}")
                print(f"  ⏱️  {elapsed/60:.1f}m elapsed | ~{eta_minutes:.1f}m remaining")

                soup = self.fetch_character_page(character_name)
                data = self.extract_character_data(soup, character_name) if soup else None

                if data:
                    current_batch.append(data)
                    success_count += 1
                    print(f"  ✅ Success ({len(data) - 2} fields)")
                else:
                    fail_count += 1
                    failures.append({'name': character_name, 'reason': 'Extraction failed'})
                    print(f"  ❌ Failed")

                # Save batch
                if len(current_batch) >= batch_size:
                    batch_num += 1
                    self._save_batch(current_batch, batch_num, progress_dir)
                    print(f"  💾 Saved batch {batch_num}")
                    current_batch = []

                # Rate limiting
                if i < len(to_scrape):
                    time.sleep(delay)

        finally:
            if self.driver:
                self.driver.quit()

        # Save final batch
        if current_batch:
            batch_num += 1
            self._save_batch(current_batch, batch_num, progress_dir)

        # Consolidate all batches
        self._consolidate_batches(progress_dir, output_file)

        # Save failures
        if failures:
            with open('output/scraping_failures.json', 'w', encoding='utf-8') as f:
                json.dump(failures, f, ensure_ascii=False, indent=2)

        # Summary
        total_time = time.time() - start_time
        print(f"\n{'='*60}")
        print(f"🎉 SCRAPING COMPLETE")
        print(f"{'='*60}")
        print(f"✅ Success: {success_count}")
        print(f"❌ Failed:  {fail_count}")
        print(f"⏱️  Total time: {total_time/60:.1f} minutes")
        print(f"📊 Success rate: {100*success_count/(success_count + fail_count):.1f}%")

    def _load_progress(self, progress_dir, consolidated_file):
        """Load already scraped character names."""
        scraped = set()

        if os.path.exists(progress_dir):
            for filename in os.listdir(progress_dir):
                if filename.endswith('.json'):
                    try:
                        with open(os.path.join(progress_dir, filename), 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            for char in data.get('characters', []):
                                scraped.add(char['source_name'])
                    except Exception:
                        pass

        if os.path.exists(consolidated_file):
            try:
                with open(consolidated_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for char in data.get('characters', []):
                        scraped.add(char['source_name'])
            except Exception:
                pass

        return scraped

    def _save_batch(self, characters, batch_num, progress_dir):
        """Save a batch of characters to file."""
        filename = os.path.join(progress_dir, f'batch_{batch_num:04d}.json')
        output = {
            'scraped_at': datetime.now().isoformat(),
            'batch_number': batch_num,
            'character_count': len(characters),
            'characters': characters
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

    def _consolidate_batches(self, progress_dir, output_file):
        """Merge all batch files into one consolidated file."""
        all_characters = []

        if os.path.exists(progress_dir):
            for filename in sorted(os.listdir(progress_dir)):
                if filename.endswith('.json'):
                    with open(os.path.join(progress_dir, filename), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        all_characters.extend(data.get('characters', []))

        output = {
            'scraped_at': datetime.now().isoformat(),
            'character_count': len(all_characters),
            'characters': all_characters
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"\n✅ Consolidated {len(all_characters)} characters → {output_file}")


def main():
    """Example usage."""
    import argparse

    parser = argparse.ArgumentParser(description='One Piece Character Scraper')
    parser.add_argument('--selenium', action='store_true', help='Use Selenium (bypasses bot detection)')
    parser.add_argument('--discover', action='store_true', help='Discover canon characters')
    parser.add_argument('--delay', type=int, default=3, help='Delay between requests (seconds)')
    parser.add_argument('--batch-size', type=int, default=50, help='Characters per batch')

    args = parser.parse_args()

    scraper = OnePieceScraper(use_selenium=args.selenium)

    if args.discover:
        characters = scraper.discover_canon_characters()
        with open('data/raw/canon_character_list.txt', 'w', encoding='utf-8') as f:
            for char in characters:
                f.write(f"{char}\n")
        print(f"✅ Saved {len(characters)} characters to data/raw/canon_character_list.txt")
    else:
        # Load character list
        try:
            with open('data/raw/canon_character_list.txt', 'r', encoding='utf-8') as f:
                characters = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print("❌ Character list not found. Run with --discover first.")
            return

        scraper.scrape_multiple(
            characters,
            output_file='output/characters.json',
            delay=args.delay,
            batch_size=args.batch_size
        )


if __name__ == "__main__":
    main()
