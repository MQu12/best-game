from typing import List
import pandas as pd
from os.path import exists

RATINGS_FNAME = "game_ratings.csv"
GAME_LIST_FNAME = "game_list.txt"
METADATA_FNAME = "metadata.txt"
TOP10_FNAME = "top10.txt"


def load_games_list() -> List[str]:
    """Open the games list text file

    Args:
        fname (str, optional): Name of the file. Defaults to "game_list.txt".

    Returns:
        List[str]: List of games by name
    """
    game_list = []
    with open(GAME_LIST_FNAME) as f:
        for line in f:
            game_list.append(line.strip())

    return game_list


def load_ratings() -> pd.DataFrame:
    """Load the ratings from file

    Args:
        fname (str, optional): Name of the file. Defaults to "game_ratings.csv".

    Returns:
        pd.DataFrame: Game names and ratings
    """
    return pd.read_csv(RATINGS_FNAME)


def check_game_is_in_ratings_file(game: str, ratings: pd.DataFrame) -> bool:
    """Check if a given game is in the ratings dataframe

    Args:
        game (str): Game name
        ratings (pd.DataFrame): Ratings

    Returns:
        bool: True if game is in the df, false otherwise
    """
    return game in list(ratings["game"])


def save_ratings(ratings: pd.DataFrame):
    ratings = ratings.sort_values(["rating"], ascending=False)
    ratings.to_csv(RATINGS_FNAME, index=False)


def update_ratings_dataframe(default_rating: float = 1000):
    """Update ratings dataframe with missing games

    Args:
        default_rating (float, optional): Default game Elo. Defaults to 1000.

    Returns:
        pd.DataFrame: Updated ratings
    """

    game_list = load_games_list()
    ratings = load_ratings()

    new_entries = []

    for game in game_list:
        if not check_game_is_in_ratings_file(game, ratings):
            new_entries.append(
                {"game": game, "rating": default_rating, "n_comparisons": 0}
            )

    ratings = pd.concat([ratings, pd.DataFrame(new_entries)]).reset_index(drop=True)

    ratings["rating"] = ratings["rating"].astype(float)
    ratings["n_comparisons"] = ratings["n_comparisons"].astype(float)

    save_ratings(ratings)


def load_metadata() -> pd.Series:
    """Load the metadata file

    Args:
        fname (str, optional): File name. Defaults to METADATA_FNAME.

    Returns:
        pd.Series: Metadata
    """

    return pd.read_csv(METADATA_FNAME).iloc[0]


def save_metadata(metadata: pd.Series):
    """Save the metadata

    Args:
        metadata (pd.Series): Output metadata
        fname (str, optional): File name for output. Defaults to METADATA_FNAME.
    """
    pd.DataFrame([metadata]).to_csv(METADATA_FNAME, index=False)


def write_top_10(ratings: pd.DataFrame):
    """Write the top 10 games to a file

    Args:
        ratings (pd.DataFrame): Ratings df
    """
    ratings = ratings.sort_values(["rating"], ascending=False)
    with open(TOP10_FNAME, "w") as f:
        for i, game in enumerate(ratings.iloc[0:10]["game"].tolist()):
            comparisons = int(ratings[ratings["game"] == game].iloc[0]["n_comparisons"])
            f.write(f"{i+1}. {game} ({comparisons})\n")


def init_files():
    """Intialise files on first load
    """

    if not exists(METADATA_FNAME):
        metadata = pd.Series([0.0], index=["n_comparisons"])
        save_metadata(metadata)

    if not exists(RATINGS_FNAME):
        ratings = pd.DataFrame(columns=["game", "rating", "n_comparisons"])
        save_ratings(ratings)


if __name__ == "__main__":
    write_top_10(load_ratings())
