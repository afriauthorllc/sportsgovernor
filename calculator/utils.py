import itertools
from decimal import Decimal

def generate_all_combinations(matches_with_odds):
    """
    Input: List of matches, each with odds
    Example: [
        {'match': 'A v B', 'odds': {'1': 1.5, 'X': 2.0, '2': 2.4}},
        {'match': 'C v D', 'odds': {'1': 3.4, 'X': 1.6, '2': 1.6}},
    ]
    Output: 9 combinations with combined odds
    """
    outcomes = ['1', 'X', '2']
    num_matches = len(matches_with_odds)

    # This is the magic: itertools.product does 3 x 3 = 9
    # For 3 matches it does 3 x 3 x 3 = 27 automatically
    all_product = list(itertools.product(outcomes, repeat=num_matches))

    combinations = []

    for index, combo in enumerate(all_product, start=1):
        picks = []
        combined_odds = Decimal('1.0')

        for match_data, pick in zip(matches_with_odds, combo):
            odd = Decimal(str(match_data['odds'][pick]))
            combined_odds *= odd

            picks.append({
                'match': match_data['match'],
                'match_id': match_data['match_id'],
                'pick': pick,  # '1', 'X', or '2'
                'odd': float(odd),
            })

        combinations.append({
            'combination_number': index,
            'picks': picks,
            'combined_odds': combined_odds,
        })

    return combinations
    
    