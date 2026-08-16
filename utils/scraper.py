import requests
from bs4 import BeautifulSoup
import time
import re
from fake_useragent import UserAgent
from config import HEADERS, MAX_RETRIES, REQUEST_TIMEOUT, PAGE_DELAY
from utils.logger import logger

class IMDBScraper:
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.headers = HEADERS.copy()
        self.headers['User-Agent'] = self.ua.random
        
    def _make_request(self, url, retries=MAX_RETRIES):
        """Make HTTP request with retry logic"""
        for attempt in range(retries):
            try:
                self.headers['User-Agent'] = self.ua.random
                response = self.session.get(
                    url, 
                    headers=self.headers, 
                    timeout=REQUEST_TIMEOUT,
                    allow_redirects=True
                )
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    time.sleep(PAGE_DELAY * (attempt + 1))
                else:
                    logger.error(f"Request failed after {retries} attempts: {url}")
                    return None
    
    def parse_movie_list(self, soup):
        """Parse movie list from search results page"""
        movies = []
        
        # Find movie containers
        movie_items = soup.find_all('div', class_='lister-item')
        
        if not movie_items:
            logger.warning("No movie items found on page")
            return movies
        
        for item in movie_items:
            try:
                # Get title and link
                title_elem = item.find('h3', class_='lister-item-header')
                if not title_elem:
                    continue
                    
                title_link = title_elem.find('a')
                if not title_link:
                    continue
                    
                title = title_link.text.strip()
                imdb_id = title_link.get('href', '').split('/')[2] if title_link.get('href') else None
                
                # Get year
                year_elem = title_elem.find('span', class_='lister-item-year')
                year = year_elem.text.strip() if year_elem else '2026'
                year = re.search(r'\d{4}', year).group(0) if re.search(r'\d{4}', year) else '2026'
                
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
                genres = genre_elem.text.strip().split(',') if genre_elem else []
                genres = [g.strip() for g in genres if g.strip()]
                
                # Get runtime
                runtime_elem = item.find('span', class_='runtime')
                runtime = runtime_elem.text.strip() if runtime_elem else None
                
                # Get plot summary
                plot_elem = item.find('p', class_='text-muted')
                plot = plot_elem.text.strip() if plot_elem else None
                
                # Get directors and cast
                credit_elem = item.find('p', class_='')
                directors = []
                cast = []
                if credit_elem:
                    credit_text = credit_elem.text.strip()
                    if 'Director:' in credit_text or 'Directors:' in credit_text:
                        parts = credit_text.split('|')
                        for part in parts:
                            if 'Director:' in part or 'Directors:' in part:
                                director_part = part.replace('Director:', '').replace('Directors:', '').strip()
                                directors = [d.strip() for d in director_part.split(',') if d.strip()]
                            elif 'Star:' in part or 'Stars:' in part:
                                star_part = part.replace('Star:', '').replace('Stars:', '').strip()
                                cast = [c.strip() for c in star_part.split(',') if c.strip()]
                
                # Get poster URL
                poster_elem = item.find('img', class_='loadlate')
                poster_url = None
                if poster_elem:
                    poster_url = poster_elem.get('src') or poster_elem.get('data-src')
                
                movie_data = {
                    'title': title,
                    'year': year,
                    'rating': rating,
                    'genres': ', '.join(genres) if genres else None,
                    'directors': ', '.join(directors) if directors else None,
                    'cast': ', '.join(cast[:3]) if cast else None,
                    'runtime': runtime,
                    'plot': plot,
                    'imdb_id': imdb_id,
                    'poster_url': poster_url,
                    'release_date': None  # Can be extracted from detail page if needed
                }
                
                movies.append(movie_data)
                
            except Exception as e:
                logger.error(f"Error parsing movie item: {e}")
                continue
        
        return movies
    
    def get_movies_by_year(self, year=2026, max_pages=50):
        """Get movies for a specific year from IMDB"""
        all_movies = []
        
        # Construct search URL
        base_url = "https://www.imdb.com/search/title/"
        
        for page in range(1, max_pages + 1):
            logger.info(f"Scraping page {page} of {max_pages}")
            
            params = {
                'year': f'{year}-01-01,{year}-12-31',
                'title_type': 'feature',
                'sort': 'release_date,desc',
                'start': (page - 1) * 50 + 1,
                'ref_': f'adv_nxt'
            }
            
            try:
                response = self._make_request(base_url, params=params)
                if not response:
                    break
                
                soup = BeautifulSoup(response.content, 'lxml')
                movies = self.parse_movie_list(soup)
                
                if not movies:
                    logger.info("No more movies found, stopping pagination")
                    break
                
                all_movies.extend(movies)
                logger.info(f"Found {len(movies)} movies on page {page}")
                
                # Check if there's a next page
                next_button = soup.find('a', class_='next-page')
                if not next_button:
                    logger.info("Reached last page")
                    break
                
                # Wait between requests
                time.sleep(PAGE_DELAY)
                
            except Exception as e:
                logger.error(f"Error scraping page {page}: {e}")
                break
        
        logger.info(f"Total movies scraped: {len(all_movies)}")
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