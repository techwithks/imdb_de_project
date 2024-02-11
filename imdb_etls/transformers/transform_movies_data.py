import pandas as pd

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def transform(data, *args, **kwargs):

    # Extracting only the movie name from the 'movie_name' column for entries in the format '1. The Shawshank Redemption'
    mask = data['movie_name'].str.match(r'^\d+\.\s.*$')  # Check if the pattern matches
    # Apply transformation only to entries that match the pattern
    data.loc[mask, 'movie_name'] = data.loc[mask, 'movie_name'].str.split('.', 1).str[1].str.strip()

    # Transforming 'movie_duration' column
    data['movie_duration'] = data['movie_duration'].apply(lambda duration_str: 
        (
            int(duration_str.replace('h', '').replace('m', '').split()[0]) if len(duration_str.split()) > 0 else 0  # Extracting hours if available, otherwise default to 0
        ) * 60 +
        (
            int(duration_str.replace('h', '').replace('m', '').split()[1]) if len(duration_str.split()) > 1 else 0  # Extracting minutes if available, otherwise default to 0
        )
    )

    # Transforming 'vote_count' column
    data['vote_count'] = pd.to_numeric(data['vote_count'].replace({'K': 'e3', 'M': 'e6'}, regex=True), errors='coerce')


    return data


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
