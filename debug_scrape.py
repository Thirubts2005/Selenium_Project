from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Setup driver
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(options=chrome_options)

try:
    # Load IMDB top 250
    print("Loading IMDB Top 250...")
    driver.get("https://www.imdb.com/chart/top250/")
    
    # Wait for content to load
    time.sleep(5)
    
    # Save HTML
    html = driver.page_source
    with open('imdb_page.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Saved HTML ({len(html)} bytes) to imdb_page.html")
    
    # Try to find movies
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    
    # Look for movie links
    movie_links = soup.find_all('a', href=True, limit=20)
    movie_links = [l for l in movie_links if '/title/' in l.get('href', '')]
    
    print(f"\nFound {len(movie_links)} movie links")
    if movie_links:
        print("Sample movies:")
        for link in movie_links[:5]:
            print(f"  - {link.text.strip()}")
    
    # Check for specific classes/divs
    divs = soup.find_all('div', limit=10)
    print(f"\nFirst 10 div elements:")
    for i, div in enumerate(divs[:10]):
        classes = div.get('class', [])
        print(f"  {i}: {' '.join(classes) if classes else 'no classes'}")

finally:
    driver.quit()
    print("\nDone!")
