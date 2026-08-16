import requests
from bs4 import BeautifulSoup
import time
import re
from fake_useragent import UserAgent
from urllib.parse import urlencode
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import HEADERS, MAX_RETRIES, REQUEST_TIMEOUT, PAGE_DELAY
from utils.logger import logger

class IMDBScraper:
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.headers = HEADERS.copy()
        self.headers['User-Agent'] = self.ua.random
        self.driver = None
        
    def setup_driver(self):
        """Initialize Selenium WebDriver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument(f"user-agent={self.ua.random}")
            # Don't use headless to avoid detection
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("Chrome WebDriver initialized")
            return self.driver
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            return None
    
    def close_driver(self):
        """Close Selenium WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver closed")
            except:
                pass
        
    def _make_request(self, url, params=None, retries=MAX_RETRIES):
        """Make HTTP request with retry logic"""
        for attempt in range(retries):
            try:
                # Update user agent
                self.headers['User-Agent'] = self.ua.random
                
                # Make request
                response = self.session.get(
                    url, 
                    params=params,
                    headers=self.headers, 
                    timeout=REQUEST_TIMEOUT,
                    allow_redirects=True
                )
                response.raise_for_status()
                return response
                
            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout (attempt {attempt + 1}/{retries})")
                if attempt < retries - 1:
                    time.sleep(PAGE_DELAY * (attempt + 1))
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(PAGE_DELAY * (attempt + 1))
                else:
                    logger.error(f"Request failed after {retries} attempts: {url}")
                    return None
        
        return None
    
    def parse_movie_list(self, soup):
        """Parse movie list from search results page"""
        movies = []
        
        # Try different selectors for movie containers
        movie_items = soup.find_all('div', class_='lister-item')
        
        if not movie_items:
            movie_items = soup.find_all('li', class_=re.compile(r'ipc.*'))
        
        if not movie_items:
            # Try finding any containers with movie titles
            movie_items = soup.find_all('div', {'class': re.compile(r'.*lister.*')})
        
        if not movie_items:
            logger.warning("No movie items found on page")
            return movies
        
        for item in movie_items:
            try:
                # Get title and link
                title_elem = item.find('h3', class_='lister-item-header')
                if not title_elem:
                    # Try alternative
                    title_elem = item.find('h3')
                    if not title_elem:
                        continue
                
                title_link = title_elem.find('a')
                if not title_link:
                    continue
                    
                title = title_link.text.strip()
                imdb_id = None
                href = title_link.get('href', '')
                if '/title/' in href:
                    imdb_id = href.split('/title/')[1].split('/')[0]
                
                # Get year
                year_elem = title_elem.find('span', class_='lister-item-year')
                if not year_elem:
                    year_elem = title_elem.find('span', class_='year')
                
                year = '2026'
                if year_elem:
                    year_text = year_elem.text.strip()
                    year_match = re.search(r'\d{4}', year_text)
                    if year_match:
                        year = year_match.group(0)
                
                # Get rating
                rating_elem = item.find('div', class_='ratings-bar')
                rating = None
                if rating_elem:
                    rating_span = rating_elem.find('strong')
                    if rating_span:
                        try:
                            rating = float(rating_span.text.strip())
                        except ValueError:
                            rating = None
                
                # Get genres
                genre_elem = item.find('span', class_='genre')
                if not genre_elem:
                    genre_elem = item.find('span', class_='genres')
                
                genres = []
                if genre_elem:
                    genre_text = genre_elem.text.strip()
                    genres = [g.strip() for g in genre_text.split(',') if g.strip()]
                
                # Get runtime
                runtime_elem = item.find('span', class_='runtime')
                runtime = runtime_elem.text.strip() if runtime_elem else None
                
                # Get plot summary - find text-muted paragraph that's not the credit
                plot_elem = None
                plot_elems = item.find_all('p', class_='text-muted')
                for p in plot_elems:
                    if p.find('a'):  # Skip if it has links (credit section)
                        continue
                    if len(p.text.strip()) > 20:  # Probably plot summary
                        plot_elem = p
                        break
                
                plot = plot_elem.text.strip() if plot_elem else None
                
                # Get directors and cast
                credit_elem = item.find('p', class_='')
                if not credit_elem:
                    credit_elem = item.find('p', class_='text-muted')
                    if credit_elem and not credit_elem.find('a'):
                        credit_elem = None
                
                directors = []
                cast = []
                if credit_elem:
                    credit_text = credit_elem.text.strip()
                    # Clean up the text
                    credit_text = ' '.join(credit_text.split())
                    
                    if 'Director:' in credit_text or 'Directors:' in credit_text:
                        parts = credit_text.split('|')
                        for part in parts:
                            part = part.strip()
                            if 'Director:' in part or 'Directors:' in part:
                                director_part = part.replace('Director:', '').replace('Directors:', '').strip()
                                directors = [d.strip() for d in director_part.split(',') if d.strip()]
                            elif 'Star:' in part or 'Stars:' in part:
                                star_part = part.replace('Star:', '').replace('Stars:', '').strip()
                                cast = [c.strip() for c in star_part.split(',') if c.strip()]
                
                # Get poster URL
                poster_elem = item.find('img', class_='loadlate')
                if not poster_elem:
                    poster_elem = item.find('img')
                
                poster_url = None
                if poster_elem:
                    poster_url = poster_elem.get('src') or poster_elem.get('data-src') or poster_elem.get('loadlate')
                    if poster_url and poster_url.startswith('//'):
                        poster_url = 'https:' + poster_url
                
                movie_data = {
                    'title': title,
                    'year': year,
                    'rating': rating,
                    'genres': ', '.join(genres) if genres else None,
                    'directors': ', '.join(directors[:3]) if directors else None,  # Limit to 3
                    'cast': ', '.join(cast[:3]) if cast else None,  # Limit to 3
                    'runtime': runtime,
                    'plot': plot[:500] if plot else None,  # Limit plot length
                    'imdb_id': imdb_id,
                    'poster_url': poster_url,
                    'release_date': None
                }
                
                movies.append(movie_data)
                
            except Exception as e:
                logger.error(f"Error parsing movie item: {e}")
                continue
        
        return movies
    
    def get_movies_by_year(self, year=2026, max_pages=5):
        """Get movies for a specific year from IMDB using Selenium"""
        all_movies = []
        
        logger.info(f"Starting to scrape movies from {year}")
        
        # Initialize driver
        if not self.setup_driver():
            logger.error("Failed to initialize WebDriver")
            return all_movies
        
        try:
            for page in range(1, max_pages + 1):
                logger.info(f"Scraping page {page} of {max_pages}")
                
                # Construct search URL
                params = {
                    'year': f'{year}-01-01,{year}-12-31',
                    'title_type': 'feature',
                    'sort': 'release_date,desc',
                    'start': (page - 1) * 50 + 1
                }
                
                url = "https://www.imdb.com/search/title/?" + urlencode(params)
                
                try:
                    logger.info(f"Loading {url}")
                    self.driver.get(url)
                    
                    # Wait for page to load
                    time.sleep(3)
                    
                    # Get page source
                    page_source = self.driver.page_source
                    
                    if "No results" in page_source:
                        logger.info(f"No results found for {year}")
                        break
                    
                    # Parse with BeautifulSoup
                    soup = BeautifulSoup(page_source, 'html.parser')
                    
                    # Find all movie items
                    movies = self.parse_movie_list(soup)
                    
                    if not movies:
                        logger.warning("No movies parsed from page")
                        # Try to get any links with /title/
                        title_links = soup.find_all('a', href=re.compile(r'/title/tt\d+'))
                        logger.info(f"Found {len(title_links)} direct title links on page")
                        if not title_links:
                            break
                    
                    all_movies.extend(movies)
                    logger.info(f"Found {len(movies)} movies on page {page} (Total: {len(all_movies)})")
                    
                    # Wait between requests
                    time.sleep(PAGE_DELAY)
                    
                except Exception as e:
                    logger.error(f"Error scraping page {page}: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
                    break
        
        finally:
            self.close_driver()
        
        logger.info(f"Scraping completed. Total movies: {len(all_movies)}")
        return all_movies
    
    def get_movie_details(self, imdb_id):
        """Get additional details for a specific movie"""
        try:
            url = f"https://www.imdb.com/title/{imdb_id}/"
            response = self._make_request(url)
            if not response:
                return None
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract release date
            release_date_elem = soup.find('a', href=re.compile(r'releaseinfo'))
            release_date = None
            if release_date_elem:
                release_date = release_date_elem.text.strip()
            
            return {
                'release_date': release_date
            }
            
        except Exception as e:
            logger.error(f"Error getting details for {imdb_id}: {e}")
            return None


def main():
    """Main function to execute the scraper"""
    try:
        logger.info("=" * 60)
        logger.info("IMDB Movie Scraper Started")
        logger.info("=" * 60)
        
        scraper = IMDBScraper()
        
        # Try scraping 2026 first, then fallback to 2025 if no results
        for year in [2026, 2025]:
            logger.info(f"\nTrying to scrape movies from {year}...")
            movies = scraper.get_movies_by_year(year=year, max_pages=2)
            
            if movies:
                logger.info(f"Successfully scraped {len(movies)} movies from {year}")
                
                # Save to Excel (which also saves to CSV)
                from utils.excel import save_to_excel
                
                success = save_to_excel(movies)
                if success:
                    logger.info(f"Data saved successfully to output directory")
                else:
                    logger.error("Failed to save data")
                
                break
            else:
                logger.warning(f"No movies found for {year}, trying {year-1}...")
        
        logger.info("=" * 60)
        logger.info("IMDB Movie Scraper Completed")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Fatal error in main: {e}", exc_info=True)
        import traceback
        logger.error(traceback.format_exc())
        raise


if __name__ == "__main__":
    main()