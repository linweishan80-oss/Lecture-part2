
import requests
import csv
from bs4 import BeautifulSoup

# The base URL for the pages to be scraped
BASE_URL = "https://ssr1.scrape.center"
# The number of pages to scrape
TOTAL_PAGES = 10
# The list to store all movie data
all_movies = []

def scrape_page(url):
    """Scrapes a single page and returns a list of movie data."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        soup = BeautifulSoup(response.text, 'html.parser')
        
        movies = []
        movie_items = soup.find_all('div', class_='el-card item m-t is-hover-shadow')

        for item in movie_items:
            # Extract title
            title_tag = item.find('h2', class_='m-b-sm')
            title = title_tag.text.strip() if title_tag else 'N/A'

            # Extract image URL
            img_tag = item.find('img', class_='cover')
            image_url = img_tag['src'] if img_tag else 'N/A'

            # Extract rating
            rating_tag = item.find('p', class_='score')
            rating = rating_tag.text.strip() if rating_tag else 'N/A'

            # Extract genres
            genres_div = item.find('div', class_='categories')
            genres = [span.text.strip() for span in genres_div.find_all('span')] if genres_div else []
            genres_str = ', '.join(genres)

            movies.append({
                'title': title,
                'image_url': image_url,
                'rating': rating,
                'genres': genres_str
            })
        return movies
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return []

def main():
    """Main function to scrape all pages and save to CSV."""
    for page in range(1, TOTAL_PAGES + 1):
        url = f"{BASE_URL}/page/{page}"
        print(f"Scraping {url}...")
        movies_on_page = scrape_page(url)
        all_movies.extend(movies_on_page)
        print(f"Found {len(movies_on_page)} movies on page {page}.")

    # Write data to CSV
    if all_movies:
        with open('movie.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['title', 'image_url', 'rating', 'genres']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(all_movies)
        print(f"\nSuccessfully saved {len(all_movies)} movies to movie.csv")
    else:
        print("No movies were scraped. CSV file not created.")

if __name__ == '__main__':
    main()
