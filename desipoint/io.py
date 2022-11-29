from astropy.time import Time, TimeDelta
import numpy as np
from PIL import Image, UnidentifiedImageError
import requests

import csv
import json
from io import BytesIO
import os

from .coordinates import radec_to_xy, trim

class AllSkyImage():
    def __init__(self, data, time):
        self.data = data
        self.time = time


base_url = "http://varuna.kpno.noirlab.edu/allsky-all/images/cropped/"

def load_ecliptic(time, radec=False):
    ep_loc = os.path.join(os.path.dirname(__file__), "data", "ecliptic.json")
    with open(ep_loc, "r") as f:
        ep = json.load(f)

        # Since we plot these as lines, for speed we can take only every
        # 3rd point
        ep = ep[::3]
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

        # Since we plot these as lines, for speed we can take only every
        # 3rd point
        mw = mw[::3]

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

def download_telemetry(time):
  try:
      with open("auth.txt", "r") as f:
          auth = json.load(f)
  except Exception as e:
      print("Loading authentication failed.")
      print(e)
      return

  print("Preparing to download image and telemetry.")
  query_url = "https://replicator.desi.lbl.gov/TV3/app/Q/query"
  params = {"namespace": "telemetry", "format": "csv",
            "sql": f"select time_recorded,mount_el,mount_az from telemetry.tcs_info where time_recorded < TIMESTAMP '{str(time)}' order by time_recorded desc limit 1"}
  # Ok so first get the resulting call, and decode it because its in bytes
  # then feed it to a csv reader which we then convert to a list so
  # now the table is a 2-d list.
  r = requests.get(query_url, params=params, auth=(auth["usr"], auth["pass"]))
  if r.status_code == 401:
    print("Invalid authentication!")
    return
  decoded = r.content.decode("utf-8")
  cr = csv.reader(decoded.splitlines(), delimiter=',')
  return list(cr)


def download_image(time):
    t = str(time)
    d = t.split(" ")[0] # Extract the current date in case the range ticks over.
    t = t.replace(":", "").replace("-", "").replace(" ", "_").split(".")[0]
    file_name = t + ".jpg"
    if abs(time - Time.now()) < TimeDelta(60 * 2, format="sec"):
        # Download from the current website if the image is for "now"
        url = "http://gagarin.lpl.arizona.edu/allsky/AllSkyCurrentImage.jpg"
    else:
        # Get the image data for this time from the server and then load
        url = base_url + d.replace("-", "/") + "/" + file_name
    try:
        response = requests.get(url)
        img = np.asarray(Image.open(BytesIO(response.content)))

        # Generate the Image object for appending.
        image = AllSkyImage(img, time)

    except UnidentifiedImageError:
        print(f"{t} image not found!")
        return None

    return image


def load_image(fname, time):
    with Image.open(fname) as im:
        # Generate the Image object.
        return AllSkyImage(np.asarray(im), time)

