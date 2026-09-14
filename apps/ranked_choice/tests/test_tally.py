import pytest

from apps.ranked_choice.tally import tally


def test_simple_majority():
    ballots = [[1], [1], [1], [2], [2]]
    assert tally(ballots, candidates=[1, 2], num_winners=1) == [1]


def test_pleasant_majority_second_choices_transfer_after_elimination():
    # First preferences: A=1, B=2, C=3 -> D (ranked 3) is eliminated first.
    ballots = [
        [1, 3],
        [1, 3],
        [2, 3],
        [2],
        [3],
    ]
    winners = tally(ballots, candidates=[1, 2, 3], num_winners=2)
    assert winners == [1, 2]


def test_partial_ballots_exhaust_and_rank_last():
    # Ballot [2, 3]: when 2 and 3 are gone it is exhausted (does not transfer
    # to unranked 1) -> 1 never receives that vote.
    ballots = [[1], [2, 3], [2, 1], [1]]
    # First prefs: 1:2, 2:2 -> eliminate 3/ no 3 votes, then 2 has one vote
    # that can only transfer to 1.
    winners = tally(ballots, candidates=[1, 2, 3], num_winners=1)
    assert winners == [1]


def test_tie_break_uses_candidate_order():
    ballots = [[1], [2]]
    winners = tally(ballots, candidates=[1, 2], num_winners=1)
    assert winners == [1]


def test_num_winners_larger_than_candidates():
    ballots = [[1], [2]]
    winners = tally(ballots, candidates=[1, 2, 3], num_winners=5)
    assert set(winners) == {1, 2, 3}


def test_empty_input():
    assert tally([], candidates=[1, 2, 3], num_winners=2) == []


def test_unranked_candidates_never_receive_transfer():
    # Ballot only ranks candidate 2; candidate 1 is unranked (last choice) and
    # must never receive a transfer from this ballot. Candidate 2 therefore
    # wins with the 2:1 first-preference majority.
    ballots = [[2], [2], [1]]
    winners = tally(ballots, candidates=[1, 2], num_winners=1)
    assert winners == [2]

def test_initial_order_ranked_by_position_counts():
    ballots = [[1, 4], [2, 4], [1], [2]]
    candidates = [1, 2, 3, 4]
    winners = tally(ballots, candidates, num_winners=4)
    assert winners.index(4) < winners.index(3)


def test_initial_order_prefers_second_votes_over_third_votes():
    ballots = [[1, 3], [2, 4, 3], [2, 4, 3]]
    candidates = [1, 2, 3, 4]
    winners = tally(ballots, candidates, num_winners=4)
    assert winners.index(4) < winners.index(3)
