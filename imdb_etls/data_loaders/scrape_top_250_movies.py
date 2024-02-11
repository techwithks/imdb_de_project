import requests
from bs4 import BeautifulSoup
import sys
import pandas as pd
import datetime


if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@data_loader
def load_data(*args, **kwargs):

    # top_250_movies
    url = 'https://www.imdb.com/chart/top/'

    # Define user agent and headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    print("Fetching data from IMDb...")
    
    # Make the request with headers
    response = requests.get(url, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')  
    else:
        print(f"Error: Failed to fetch the page. Status code: {response.status_code}")
        sys.exit(1)  # Terminate the script if the request fails

    print("Data fetched successfully. Parsing HTML...")

    # Find all movie names in the url
    movie_names = []
    movie_years = []
    movie_ratings = []
    vote_counts = []
    durations = []
    rated_values = []

    # Count missing data
    missing_data_count = {'title': 0, 'release_year': 0, 'duration': 0, 'rated': 0, 'rating': 0, 'vote_count': 0}
    
    # Count rows inserted and missing values replaced
    rows_inserted = 0
    missing_values_replaced = 0

    # Find all movie in the url
    listRefs = soup.find_all('li', class_='ipc-metadata-list-summary-item')

    print("Parsing movie data...")

    # Collect movie title, release year, ratings, and user votings
    for movie in listRefs:
        try:
            movie_names.append(movie.find('h3', class_='ipc-title__text').text)
        except:
            movie_names.append(-1)
            missing_data_count['title'] += 1

        try:
            yeardiv = movie.find('div', class_='cli-title-metadata')
            year_span = yeardiv.find('span', class_='cli-title-metadata-item')
            year = year_span.text
            movie_years.append(year)
        except:
            movie_years.append(-1)
            missing_data_count['release_year'] += 1

        try:
            duration_span = yeardiv.find_all('span', class_='cli-title-metadata-item')[1]
            duration_str = duration_span.text
            durations.append(duration_str)

        except:
            durations.append(-1)
            missing_data_count['duration'] += 1

        try:
            rated_spans = yeardiv.find_all('span', class_='cli-title-metadata-item')
            rated_span = rated_spans[2] if len(rated_spans) > 2 else None
            rated_value = rated_span.text
            rated_values.append(rated_value)
        except Exception as e:
            rated_values.append(-1)
            missing_data_count['rated'] += 1

        try:
            rating_span = movie.find('span', class_='ipc-rating-star--voteCount')
            movie_ratings.append(float(rating_span.previous_sibling.strip()))    
        except:
            movie_ratings.append(-1)
            missing_data_count['rating'] += 1

        try:
            votes_str = rating_span.get_text(strip=True)

            # Removing parentheses and handling suffixes
            numeric_value_str = votes_str[1:-1]
            vote_counts.append(numeric_value_str)

        except:
            vote_counts.append(-1)
            missing_data_count['vote_count'] += 1

    print("Data parsing complete. Creating DataFrame...")

    # Create a dataframe
    movie_df = pd.DataFrame({'movie_name': movie_names, 'movie_year': movie_years, 'movie_duration': durations, 'rated': rated_values, 'movie_rating': movie_ratings, 'vote_count': vote_counts})

    # Add movie_id
    movie_df['movie_id'] = movie_df.index + 1

    # set date
    movie_df['update_date'] = datetime.datetime.today().strftime('%Y-%m-%d')

    # reorder columns
    movie_df = movie_df[['movie_id', 'movie_name', 'movie_year', 'movie_duration', 'rated', 'movie_rating', 'vote_count', 'update_date']]

    # Count rows inserted
    rows_inserted = len(movie_df)

    # Count missing values replaced by -1
    missing_values_replaced = sum(movie_df.isna().sum())

    # Print summary
    print(f"Summary: \nRows Inserted: {rows_inserted},\nMissing Data Count: {missing_data_count}")

    return movie_df


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
