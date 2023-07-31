# settings & imports
import pandas as pd

def total_bases(hits, doubles, triples, homeruns):
    ""
    singles = hits - doubles - triples - homeruns
    tb = singles + (doubles*2) + (triples*3) + (homeruns*4)

    return tb

def batting_average(hits, at_bats):
    ""
    return round(sum(hits) / sum(at_bats), 3)

def on_base_percentage(bases_reached, plate_appearances):
    ""
    return round(sum(bases_reached) / sum(plate_appearances), 3)

def slugging_percentage(total_bases, at_bats):
    ""
    return round(sum(total_bases) / sum(at_bats), 3)