
import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup

# The base URL for the pages to be scraped
BASE_URL = "https://ssr1.scrape.center"
# The number of pages to scrape
TOTAL_PAGES = 10

def scrape_page(url):
    """Scrapes a single page and returns a list of movie data."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        soup = BeautifulSoup(response.text, 'html.parser')
        
        movies = []
        movie_items = soup.find_all('div', class_='el-card item m-t is-hover-shadow')

        for item in movie_items:
            title_tag = item.find('h2', class_='m-b-sm')
            title = title_tag.text.strip() if title_tag else 'N/A'

            img_tag = item.find('img', class_='cover')
            image_url = img_tag['src'] if img_tag else 'N/A'

            rating_tag = item.find('p', class_='score')
            rating = rating_tag.text.strip() if rating_tag else 'N/A'

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
        st.error(f"Error fetching {url}: {e}")
        return []

def main():
    """Main function to build the Streamlit UI."""
    st.title('🎬 电影数据爬虫')
    st.write(f"此应用将从 `{BASE_URL}` 网站爬取前 {TOTAL_PAGES} 页的电影数据。")

    if st.button('🚀 开始爬取数据'):
        all_movies = []
        progress_bar = st.progress(0)
        status_text = st.empty()

        with st.spinner('正在爬取中... 请稍候...'):
            for page in range(1, TOTAL_PAGES + 1):
                url = f"{BASE_URL}/page/{page}"
                status_text.text(f"正在爬取第 {page}/{TOTAL_PAGES} 页...")
                movies_on_page = scrape_page(url)
                all_movies.extend(movies_on_page)
                progress_bar.progress(page / TOTAL_PAGES)
        
        status_text.text('') # Clear status text
        st.success(f'✅ 爬取完成！共找到 {len(all_movies)} 部电影。')

        if all_movies:
            df = pd.DataFrame(all_movies)
            
            st.subheader('电影数据表格')
            st.dataframe(df)

            st.subheader('电影海报墙')
            # Display images in columns
            cols = st.columns(5) 
            for index, row in df.iterrows():
                with cols[index % 5]:
                    st.image(row['image_url'], caption=f"{row['title']} ({row['rating']})", use_column_width=True)

if __name__ == '__main__':
    main()
