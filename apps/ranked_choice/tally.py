"""Counting logic for the ranked-choice vote.

The ballots are partial: each ballot only contains the candidates the voter
actually ranked, ordered by descending preference. Unranked candidates are
treated as "last choice" - they simply never receive a transfer.

The counting method is a single transferable vote style instant runoff that
produces a full (deterministic) ranking of all candidates by repeatedly
eliminating the candidate with the fewest first-preferences. The top
``num_winners`` candidates of that ranking are the winners.

Tie-breaking is deterministic and hierarchical. The initial order is built lexicographically from the preference counts: rank-1 votes first, then rank-2 votes, then rank-3 votes, and so on. Only if all preference counts are equal, candidates earlier in the provided ``candidates``
order are considered to have a (weak) advantage and are eliminated last on a
tie, therefore ranking higher in the result.
"""


def tally(ballots, candidates, num_winners):
    """Return the ordered list of winning candidate keys.

    Arguments:
        ballots: iterable of ordered iterables of candidate keys, one per
            ballot, ranking only the candidates the voter chose.
        candidates: iterable of all candidate keys.
        num_winners: how many winners to select (top of the resulting ranking).

    Returns:
        List of candidate keys, first element is the top winner.
    """
    ballots = [list(b) for b in ballots]
    candidates = list(candidates)
    num_winners = max(1, int(num_winners))

    if not candidates or not ballots:
        return []

    # Lexicographic merit order per candidate: the counts of ballots that rank
    # the candidate at position 1, 2, 3, ... (positions beyond the ballot
    # length count as zero). This deterministic order is the initial order
    # that breaks ties: rank-1 votes first, then rank-2 votes, then rank-3
    # votes, and so on.
    max_rank = max(len(ballot) for ballot in ballots)
    pos_counts = {candidate: [0] * max_rank for candidate in candidates}
    for ballot in ballots:
        for position, choice in enumerate(ballot[:max_rank]):
            if choice in pos_counts:
                pos_counts[choice][position] += 1

    def merit_key(candidate):
        return tuple(pos_counts[candidate])

    remaining = set(candidates)
    # Descending elimination result: the last eliminated has the most support.
    elimination_order = []

    while remaining:
        counts = {candidate: 0 for candidate in remaining}
        active_ballots = 0
        for ballot in ballots:
            for choice in ballot:
                if choice in remaining:
                    counts[choice] += 1
                    active_ballots += 1
                    break

        if active_ballots == 0:
            # No ballot has a ranked, non-eliminated candidate left. Place the
            # remaining candidates by the initial order only: fewer rank-1
            # votes rank lower, then fewer rank-2 votes, etc.; exact ties
            # favour earlier candidates in the list.
            order = sorted(
                remaining,
                key=lambda c: (merit_key(c), -_tie_break_key(c, candidates)),
            )
            for candidate in order:
                elimination_order.append(candidate)
                remaining.remove(candidate)
            break

        # Eliminate the candidate with the fewest first-preferences. On a tie
        # the candidate with fewer rank-1 votes is eliminated first, then fewer
        # rank-2 votes, then fewer rank-3 votes, etc.; if even that is equal,
        # the candidate later in the provided list is eliminated first.
        lowest = min(
            remaining,
            key=lambda c: (counts[c], merit_key(c), -_tie_break_key(c, candidates)),
        )
        elimination_order.append(lowest)
        remaining.remove(lowest)

    ranking = list(reversed(elimination_order))
    return ranking[:num_winners]


def _tie_break_key(candidate, candidates):
    """Lower means "ranked higher"/survives longer on a tie."""
    try:
        return candidates.index(candidate)
    except ValueError:
        return float("inf")