from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import os

def scrape_top_250():
    """Scrape IMDB Top 250 movies"""
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    movies = []
    
    try:
        print("Fetching IMDB Top 250 movies...")
        driver.get("https://www.imdb.com/chart/top250/")
        
        # Wait for JavaScript to render
        time.sleep(5)
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find all movie containers - look for links with /title/
        movie_links = soup.find_all('a', href=True)
        movie_links = [l for l in movie_links if '/title/tt' in l.get('href', '')]
        
        print(f"Found {len(movie_links)} movie links")
        
        # Extract movie info
        for i, link in enumerate(movie_links):
            if i >= 20:  # Limit to first 20 for testing
                break
            
            href = link.get('href', '')
            title = link.text.strip()
            
            if '/title/' in href:
                imdb_id = href.split('/title/')[1].split('/')[0]
                
                movie_data = {
                    'title': title,
                    'imdb_id': imdb_id,
                    'url': f'https://www.imdb.com{href}',
                    'year': '',
                    'rating': '',
                    'genres': '',
                    'plot': 'Top 250 Movie'
                }
                
                movies.append(movie_data)
                print(f"  {i+1}. {title} ({imdb_id})")
        
        return movies
        
    finally:
        driver.quit()

if __name__ == "__main__":
    movies = scrape_top_250()
    
    if movies:
        print(f"\nSuccessfully scraped {len(movies)} movies!")
        
        # Save to Excel
        from utils.excel import save_to_excel
        success = save_to_excel(movies)
        
        if success:
            # Show files created
            output_dir = "output"
            files = os.listdir(output_dir)
            print(f"\nFiles created in {output_dir}:")
            for f in files:
                file_path = os.path.join(output_dir, f)
                size = os.path.getsize(file_path)
                print(f"  - {f} ({size} bytes)")
    else:
        print("No movies scraped")
