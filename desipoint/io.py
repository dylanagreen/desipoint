
from .coordinates import radec_to_xy, trim

import json
import os

def load_ecliptic(time, radec=False):
    ep_loc = os.path.join(os.path.dirname(__file__), "data", "ecliptic.json")
    with open(ep_loc, "r") as f:
        ep = json.load(f)

        # 11/9/22: I don't remember why I do this.
        ep2 = []
        for i in range(len(ep)):
            if i % 10 >= 2 and i % 10 <= 5:
                ep2.append(ep[i])

        ep = ep2
        ep_ra = [c[0]for c in ep]
        ep_dec = [c[1] for c in ep]

    if radec:
        return ep_ra, ep_dec
    else:
        ep_x, ep_y = radec_to_xy(ep_ra, ep_dec, time)
        ep_x, ep_y = trim(ep_x, ep_y)

        return ep_x, ep_y

def load_milky_way(time, radec=False):
    mw_loc = os.path.join(os.path.dirname(__file__), "data", "mw.json")
    with open(mw_loc, "r") as f:
        mw = json.load(f)

        # Makes the line dotted with 5 dot size gaps between the dots.
        mw = mw[::6]

        mw_ra = [c[0]for c in mw]
        mw_dec = [c[1] for c in mw]

    if radec:
        return mw_ra, mw_dec
    else:
        mw_x, mw_y = radec_to_xy(mw_ra, mw_dec, time)
        mw_x, mw_y = trim(mw_x, mw_y)

        return mw_x, mw_y

def load_survey(time, radec=False):
    hull_loc = os.path.join(os.path.dirname(__file__), "data", "survey_left.json")
    with open(hull_loc, "r") as f:
        # Converts the string representation of the list to a list of points.
        left = json.load(f)

        left_ra = [c[0]for c in left]
        left_dec = [c[1] for c in left]

    # Load the DESI survey area
    hull_loc = os.path.join(os.path.dirname(__file__), "data", "survey_right.json")
    with open(hull_loc, "r") as f:
        right = json.load(f)

        right_ra = [c[0]for c in right]
        right_dec = [c[1] for c in right]

    if radec:
        return left_ra, left_dec, right_ra, right_dec
    else:
        # Generating the x/y points for the desi survey areas
        left_x, left_y = radec_to_xy(left_ra, left_dec, time)
        left = [(left_x[i], left_y[i]) for i, _ in enumerate(left_x)]

        right_x, right_y = radec_to_xy(right_ra, right_dec, time)
        right = [(right_x[i], right_y[i]) for i, _ in enumerate(right_x)]

        return left, right