import random
from typing import List
from app.competitions.models import Matchs
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func

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
            matchs_random = random.sample( list_match_peru, len(list_match_peru)) + random.sample( list_match_otros, len_loop - len(list_match_peru))
    else:
        matchs_random = random.sample( list_match_otros, len_loop)

    return matchs_random

def get_cod_competitions_most_used(days: List[str], db: Session) -> List[str]:
    list_match_cod_competitions = []
    total = 0
    result = []
    cod_competitions_most_used = ["PPD"]
    for day in days:
        matchs = (
            db.query(Matchs.cod_competitions,func.count(Matchs.cod_competitions).label('count'))
            .filter(Matchs.date == day)
            .group_by(Matchs.cod_competitions)
            .order_by(func.count(Matchs.cod_competitions).desc())
            .all()
        )            
        for match in matchs:
            match_ = list(match) 
            match_.append(day)
            list_match_cod_competitions.append(match_)            
    df = pd.DataFrame(list_match_cod_competitions, columns=['letter', 'value','a'])
    counts = df['letter'].value_counts()
    sorted_counts = counts.sort_values(ascending=False)
    for letter, count in sorted_counts.items():
        if total >= 7:
            break
        total += count
        result.append((letter, count))
    for letter, count in result:
        cod_competitions_most_used.append(letter)
    
    return cod_competitions_most_used