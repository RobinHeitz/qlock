# %%

WD_IT_IS = [34,61,93,98,125]
WD_5_1 = [162,189,194,221]
WD_10_1 = [35,60,67,92]
WD_20_1 = [124,131,156,163,188,195,220]
WD_three_quarter = [36,59,68,91,100,123,132,155,164,187,196]
WD_quarter = WD_three_quarter[4:]
WD_3_1 = [36,59,68,91]
WD_before = [37,58,69]
WD_after = [154,165,186,197]
WD_GOOD_NIGHT = [90,101,122,133,154,165,186,197,218]
WD_GOOD = WD_GOOD_NIGHT[:4]
WD_NIGHT = WD_GOOD_NIGHT[4:]
WD_HALF = [38,57,70,89]
WD_11 = [121,134,153]
WD_5_2 = [153,166,185,198]
WD_HAPPY_BD = [217,216,215,214,213,148,171,180,203,212,179,204,211]
WD_HAPPY = WD_HAPPY_BD[:5]
WD_BIRTHDAY = WD_HAPPY_BD[5:]
WD_1 = [39,56,71,88]
WD_1_O_CLOCK = [39,56,71]
WD_2 = [135,152,167,184]
WD_3_2 = [40,55,72,87]
WD_4 = [136,151,168,183]
WD_6 = [41,54,73,86,105]
WD_8 = [137,150,169,182]
WD_7 = [42,53,74,85,106,117]
WD_12 = [138,149,170,181,202]
WD_GOOD_MORNING = [90,101,122,133,154,43,52,75,84,107,116]
WD_CHARLY =  [50,77,82,109,114,141,146]
WD_10_2 = [44,51,76,83]
WD_9 = [83,108,115,140]
WD_CLOCK = [178,205,210]
WD_MIN_1 = [0]
WD_MIN_2 = [0,255]
WD_MIN_3 = [0,255,240]
WD_MIN_4 = [0,255,240,15]

WD_5_MIN_AFTER = WD_5_1 + WD_after 
WD_10_MIN_AFTER = WD_10_1 + WD_after 
WD_15_MIN_AFTER = WD_quarter + WD_after 
WD_20_MIN_AFTER = WD_20_1 + WD_after 
WD_5_MIN_BEFORE_HALF = WD_5_1 + WD_before + WD_HALF 
WD_5_MIN_AFTER_HALF = WD_5_1 + WD_after + WD_HALF 
WD_20_BEFORE = WD_20_1 + WD_before
WD_15_BEFORE = WD_quarter + WD_before
WD_10_BEFORE = WD_10_1 + WD_before
WD_5_BEFORE = WD_5_1 + WD_before



HOUR_DEF  = {1:WD_1,2:WD_2,3:WD_3_2,4:WD_4,5:WD_5_2,6:WD_6,7:WD_7,8:WD_8,9:WD_9,10:WD_10_2,11:WD_11,12:WD_12}
MIN_POINTS_DEF = {1:WD_MIN_1,2:WD_MIN_2,3:WD_MIN_3,4:WD_MIN_4,0:[] }

_ALL_WD_DEFS = [
    WD_IT_IS,
    WD_5_1,
    WD_10_1,
    WD_10_1,
    WD_20_1,
    WD_three_quarter,
    WD_quarter,
    WD_3_1,
    WD_before,
    WD_after,
    WD_GOOD_NIGHT,
    WD_GOOD,
    WD_NIGHT,
    WD_HALF,
    WD_11,
    WD_5_2,
    WD_HAPPY_BD,
    WD_1,
    WD_1_O_CLOCK,
    WD_2,
    WD_3_2,
    WD_4,
    WD_6,
    WD_8,
    WD_7,
    WD_12,
    WD_GOOD_MORNING,
    WD_CHARLY,
    WD_10_2,
    WD_9,
    WD_CLOCK,
    WD_MIN_1, WD_MIN_2, WD_MIN_3, WD_MIN_4,
]

PIXELS = []

for i in _ALL_WD_DEFS:
    PIXELS = PIXELS + i

WD_ALL_PIXELS = set(PIXELS)