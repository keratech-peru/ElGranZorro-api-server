import random
from typing import List
from app.competitions.models import Matchs

def format_date(date: str):
    return date[-2:]+"/"+date[5:7]+"/"+date[2:4]

def preferred_random_values(matchs: List[Matchs] , len_loop: int):
    list_match_peru = []
    list_match_otros = []
    for match in matchs:
        if match.cod_competitions == 'PPD':
            list_match_peru.append(match)
        else:
            list_match_otros.append(match)

    if len(list_match_peru) > 0:
        if len_loop <= len(list_match_peru):
            matchs_random = random.sample( list_match_peru, len_loop)
        else:
            print("len_loop - len(list_match_peru) : ", len_loop - len(list_match_peru))
            matchs_random = random.sample( list_match_peru, len(list_match_peru)) + random.sample( list_match_otros, len_loop - len(list_match_peru))
    else:
        matchs_random = random.sample( list_match_otros, len_loop)

    return matchs_random