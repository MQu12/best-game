import math
from numpy.random import choice
from typing import Tuple
import pandas as pd
import dataio
import numpy as np

def select_games(
    ratings: pd.DataFrame,
    favour_least_picked: bool = True,
    favour_closer_ratings: bool = True,
) -> Tuple[str, str]:
    """Select two games at random

    Args:
        ratings (pd.DataFrame): Ratings dataframe
        favour_least_picked (bool): If true, the first game picked will be one of the least picked games. Defaults to True.

    Returns:
        Tuple[str,str]: Two games
    """

    game2_list = ratings["game"].tolist()

    if favour_least_picked:
        min_comparisons = ratings["n_comparisons"].min()
        game1_list = ratings[ratings["n_comparisons"] == min_comparisons][
            "game"
        ].tolist()
    else:
        game1_list = game2_list

    game1 = choice(game1_list)
    game2 = game1

    while game1 == game2:
        if favour_closer_ratings:
            game1_rating = ratings[ratings["game"] == game1]["rating"]
            ratings_difference_series = (
                ratings.set_index("game").drop(game1)["rating"] - float(game1_rating)
            )
            zero_difference_games = ratings_difference_series[
                ratings_difference_series == 0
            ]
            if len(zero_difference_games) == 0:
                inverse_ratings_diff = 1 / np.abs(ratings_difference_series)
                p = inverse_ratings_diff / sum(inverse_ratings_diff)
                game2 = choice(inverse_ratings_diff.index, p=p)
            else:
                game2 = choice(zero_difference_games.index)
        else:
            game2 = choice(game2_list)

    return game1, game2


def expected_win(elo1: float, elo2: float) -> float:
    """Expected result

    Args:
        elo1 (float): Elo of game 1
        elo2 (float): Elo of game 2

    Returns:
        float: Expectation that game 1 will 'win'
    """
    return 1.0 / (1 + math.pow(10, (elo2 - elo1) / 400))


def new_elo(old_elo: float, expectation: float, result: float, k: float = 32):
    """Calculate new elo based on result

    Args:
        old_elo (float): Elo at start
        expectation (float): Expected result (0-1)
        result (float): Actual result (1 for win, 0 for loss)
        k (float, optional): K factor. Defaults to 32.

    Returns:
        _type_: _description_
    """
    return old_elo + k * (result - expectation)


def update_rating_based_on_winner(
    ratings: pd.DataFrame, winner: str, loser: str
) -> pd.DataFrame:
    """Update game ratings based on winning/losing game based on Elo

    Args:
        ratings (pd.DataFrame): Ratings dataframe
        winner (str): Winning game
        loser (str): Losing game

    Returns:
        pd.DataFrame: Ratings dataframe with rating updated
    """

    ratings_game_indexed = ratings.set_index("game", drop=True)

    winner_Elo = ratings_game_indexed.loc[winner]["rating"]
    loser_Elo = ratings_game_indexed.loc[loser]["rating"]

    winner_exp = expected_win(winner_Elo, loser_Elo)
    loser_exp = expected_win(loser_Elo, winner_Elo)

    winner_new_elo = new_elo(winner_Elo, winner_exp, 1.0)
    loser_new_elo = new_elo(loser_Elo, loser_exp, 0.0)

    ratings_game_indexed.loc[winner]["rating"] = winner_new_elo
    ratings_game_indexed.loc[loser]["rating"] = loser_new_elo

    ratings_game_indexed.loc[winner]["n_comparisons"] += 1
    ratings_game_indexed.loc[loser]["n_comparisons"] += 1

    return ratings_game_indexed.reset_index()


def update_metadata(metadata: pd.Series) -> pd.Series:
    """Update the metadata

    Args:
        metadata (pd.Series): Metadata

    Returns:
        pd.Series: Updated metadata
    """
    metadata["n_comparisons"] += 1
    return metadata


def do_comparison() -> bool:
    """Perform a comparison

    Returns:
        bool: If true, do another comparison, False for quit
    """
    ratings = dataio.load_ratings()
    game1, game2 = select_games(ratings)

    print(f"1. {game1}")
    print(f"2. {game2}")

    valid_response = False

    answer = -1

    while not valid_response:
        answer_raw = input(f"1/2 (or exit)? ")

        if answer_raw == "exit":
            return False

        answer = int(answer_raw)

        if answer != 1 and answer != 2:
            print("Input must be 1/2, try again")

        valid_response = True

    if answer == 1:
        updated_ratings = update_rating_based_on_winner(ratings, game1, game2)
    elif answer == 2:
        updated_ratings = update_rating_based_on_winner(ratings, game2, game1)
    else:
        print("Invalid reponse")
        return False

    dataio.save_ratings(updated_ratings)

    metadata = dataio.load_metadata()
    metadata = update_metadata(metadata)
    dataio.save_metadata(metadata)

    dataio.write_top_10(updated_ratings)

    return True


def main():
    dataio.init_files()
    dataio.update_ratings_dataframe()
    while do_comparison():
        continue


if __name__ == "__main__":
    main()
