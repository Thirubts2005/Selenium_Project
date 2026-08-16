import requests
from bs4 import BeautifulSoup
import json

url = 'https://www.imdb.com/search/title/'
params = {
    'year': '2026-01-01,2026-12-31',
    'title_type': 'feature',
    'sort': 'release_date,desc'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
}

try:
    print("Fetching IMDB page...")
    response = requests.get(url, params=params, headers=headers, timeout=15)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    print(f"Page title: {soup.title.string if soup.title else 'No title'}")
    print(f"Page size: {len(response.text)} characters\n")
    
    # Test different selectors
    selectors_to_test = [
        ('div', 'lister-item'),
        ('div', 'lister-item-content'),
        ('li', 'ipc-metadata-list-summary-item'),
        ('li', 'ipc-list-card'),
        ('div', 'ipc-title'),
        ('article', None),
    ]
    
    for tag, class_name in selectors_to_test:
        if class_name:
            items = soup.find_all(tag, class_=class_name, limit=3)
            print(f"Found {len(soup.find_all(tag, class_=class_name))} <{tag}> with class='{class_name}'")
        else:
            items = soup.find_all(tag, limit=3)
            print(f"Found {len(soup.find_all(tag))} <{tag}> elements")
    
    # Look for any links that might be movie titles
    links = soup.find_all('a', href=True, limit=20)
    movie_links = [l for l in links if '/title/' in l.get('href', '')]
    print(f"\nFound {len(movie_links)} links containing '/title/'")
    
    if movie_links:
        print("Sample movie links:")
        for link in movie_links[:3]:
            print(f"  - {link.text.strip()} -> {link.get('href')}")
    
    # Check page content
    if "No results" in response.text:
        print("\n⚠️  Page shows 'No results' - there might be no 2026 movies on IMDB yet")
    else:
        print("\n✓ Page appears to have content")
        
except requests.exceptions.RequestException as e:
    print(f"Request error: {e}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
