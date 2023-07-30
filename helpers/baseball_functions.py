# settings & imports
import pandas as pd

def total_bases(hits, doubles, triples, homeruns):
    ""
    singles = hits - doubles - triples - homeruns
    tb = singles + (doubles*2) + (triples*3) + (homeruns*4)

    return tb