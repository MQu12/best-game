from typing import List, Tuple
import compare_games
import pandas as pd


def run_comparison(
    ratings: pd.DataFrame,
    true_orderings: List[str],
    favour_least_picked: bool,
    favour_closer_ratings: bool,
) -> pd.DataFrame:

    game1, game2 = compare_games.select_games(
        ratings, favour_least_picked, favour_closer_ratings
    )

    game1_true_pos = true_orderings.index(game1)
    game2_true_pos = true_orderings.index(game2)

    winner, loser = (
        (game1, game2) if game1_true_pos < game2_true_pos else (game2, game1)
    )

    updated_ratings = compare_games.update_rating_based_on_winner(
        ratings, winner, loser
    )

    return updated_ratings


def run_one_sim(
    ratings: pd.DataFrame,
    true_orderings: List[str],
    favour_least_picked: bool,
    favour_closer_ratings: bool,
    n_comps: int = 100,
) -> pd.DataFrame:
    for i in range(n_comps):
        ratings = run_comparison(
            ratings, true_orderings, favour_least_picked, favour_closer_ratings
        )
    return ratings.sort_values(["rating"], ascending=False)


def score_list(
    true_ordering: List[str], observed_ordering: List[str], top: int = -1
) -> Tuple[float, int]:

    total_deviation = 0.0
    largest_deviation = 0.0

    for i, game in enumerate(true_ordering):
        if i >= top and i != -1:
            break

        deviation = abs(observed_ordering.index(game) - i)
        total_deviation += deviation
        if deviation > largest_deviation:
            largest_deviation = deviation

    average_deviation = total_deviation / (top if top != -1 else len(true_ordering))

    return average_deviation, largest_deviation


def score_from_ratings(
    ratings: pd.DataFrame, true_ordering: List[str], top: int = -1
) -> Tuple[float, int]:
    return score_list(true_ordering, ratings["game"].tolist(), top)


def run_n_sims(
    true_orderings: List[str],
    favour_least_picked=False,
    favour_closer_ratings=False,
    n_comps: int = 100,
    n_sims: int = 10,
) -> Tuple[float, int]:

    av_devs = []
    max_devs = []

    for i in range(n_sims):

        ratings = pd.DataFrame({"game": true_orderings})
        ratings["rating"] = 1000.0
        ratings["n_comparisons"] = 0.0

        ratings = run_one_sim(
            ratings, true_orderings, favour_least_picked, favour_closer_ratings, n_comps
        )

        av_dev, max_dev = score_from_ratings(ratings, true_orderings, 10)

        av_devs.append(av_dev)
        max_devs.append(max_dev)

    return av_devs, max_devs
