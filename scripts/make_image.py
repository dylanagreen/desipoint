#!/usr/bin/env python3
import requests
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Polygon, Circle, Rectangle
from astropy.time import Time, TimeDelta
from PIL import Image, UnidentifiedImageError

import argparse
import csv
import json
import os
from io import BytesIO

from desipoint.coordinates import radec_to_xy, altaz_to_xy, trim
from desipoint.io import load_ecliptic, load_milky_way, load_survey
from desipoint.image import create_image

base_url = "http://varuna.kpno.noirlab.edu/allsky-all/images/cropped/"

class AllSkyImage():
    def __init__(self, data, time):
        self.data = data
        self.time = time


def create_video(start, end, toggle_mw=False, toggle_ep=False, toggle_survey=False,
                 toggle_pointing=False):
    # Start and end times for image range.
    start_time = Time(start).iso
    end_time = Time(end).iso

    # Updating the start time to be the next avaliable image.
    temp_start = str(start_time)
    minutes = int(temp_start[-9:-7])
    # Sets minutes to next even minute if it is odd, and remains the same if even
    minutes = (minutes + 1) // 2 * 2
    temp_start = temp_start[:-9] + str(minutes) + ":05.000"

    start_time = Time(temp_start)

    # Loops over the given time period in 120s increments, getting the image at
    # each time step.
    print(f"Video start at {str(start_time)}")
    print(f"Video end at {str(end_time)}")

    if toggle_pointing:
        try:
            with open("auth.txt", "r") as f:
                auth = json.load(f)
        except Exception as e:
            print("Loading authentication failed.")
            print(e)
            return

        print("Preparing to download images and telemetry.")
        query_url = "https://replicator.desi.lbl.gov/TV3/app/Q/query"
        params = {"namespace": "telemetry", "format": "csv",
                  "sql": f"select time_recorded,mount_el,mount_az from telemetry.tcs_info where time_recorded >= TIMESTAMP '{str(start_time)}' AND time_recorded < TIMESTAMP '{str(end_time)}' order by time_recorded asc"}
        # Ok so first get the resulting call, and decode it because its in bytes
        # then feed it to a csv reader which we then convert to a list so
        # now the table is a 2-d list.
        r = requests.get(query_url, params=params, auth=(auth["usr"], auth["pass"]))
        if r.status_code == 401:
          print("Invalid authentication!")
          return
        decoded = r.content.decode("utf-8")
        cr = csv.reader(decoded.splitlines(), delimiter=',')
        results = list(cr)

        # Then since the telemetry updates (on average) every ~4.3s, we need to
        # only strip out the ones we want. So we loop over the telemetry
        # and extra approx 20 timestamps near a minute later than the previous
        # saved telemetry. We do this because it's way quicker to search 20
        # rather than 10k for a single timestamp.
        pre = 0

        # Helper array of only the time stamps. This is the slowest part of this
        # process, stripping out the time component only.
        time_only = np.asarray([Time(r[0][:-6]) for r in results[1:-1]])

        pointings = []
        pointings.append(results[1])

        # A small helper function that allows us to subtract times from a np array
        # of times.
        def sub_time(t1, t2):
            t = t2 - t1
            # Ensures we always find the lowest possible  positive difference
            # from the next time.
            if t < 0:
              return 1000
            else:
              return t

        v_sub = np.vectorize(sub_time)
    else:
        print("Preparing to download images.")

    images = []
    cur_time = start_time
    counter = 0
    while cur_time < end_time:
        # Convert the time to a useable file name
        t = str(cur_time)
        d = t.split(" ")[0] # Extract the current date in case the range ticks over.
        t = t.replace(":", "").replace("-", "").replace(" ", "_").split(".")[0]
        file_name = t + ".jpg"

        # Get the image data for this time from the server and then load
        url = base_url + d.replace("-", "/") + "/" + file_name
        try: # We only need to download images on even times.
            if counter % 2 == 0:
                response = requests.get(url)
                img = np.asarray(Image.open(BytesIO(response.content)))

                # Generate the Image object for appending.
                temp = AllSkyImage(img, cur_time)
                images.append(temp)

        except UnidentifiedImageError:
            print(f"{t} image not found, skipping")
            # Increment to next image 120 seconds later.
            counter += 2
            cur_time += TimeDelta(120, format="sec")
        else:
            # I am fairly confident that the next 60s later update appears between 10
            # and 30 telemetry updates from now.
            # We find the next time by subtracting each stamp from the current one
            # and then finding the minimum positive distance. Then the last update
            # BEFORE the one minute per frame update is that index - 1. Don't need
            # to subtract 1 since the addition of the column titles in results
            # takes care of that already.
            if toggle_pointing and counter > 1:
                truncated_time = time_only[pre + 10: pre + 30]
                time_test = v_sub(truncated_time, cur_time)

                pre = np.argmin(time_test) + pre + 10
                pointings.append(results[pre])
            # Increment to next time 60 seconds later.
            counter += 1
            cur_time += TimeDelta(60, format="sec")

    if toggle_pointing:
        print("Telemetry and images received and organized.")
    else:
        print("Images downloaded.")
    print("Printing every 10th frame.")

    # Set up the figure the same way we usually do for saving so the image is the
    # only thing on the axis.
    dpi = 128
    y = images[0].data.shape[0] / dpi
    x = images[0].data.shape[1] / dpi

    # Generate Figure and Axes objects.
    fig = plt.figure()
    fig.set_size_inches(x, y)
    ax = plt.Axes(fig, [0., 0., 1., 1.])  # 0 - 100% size of figure

    # Turn off the actual visual axes for visual niceness.
    # Then add axes to figure
    ax.set_axis_off()
    fig.add_axes(ax)

    # Load the DESI survey area
    if toggle_survey:
        left_ra, left_dec, right_ra, right_dec = load_survey(images[0].time, True)

        # Generating the x/y points for the desi survey areas
        left_x, left_y = radec_to_xy(left_ra, left_dec, images[0].time)
        left = [(left_x[i], left_y[i]) for i, _ in enumerate(left_x)]

        right_x, right_y = radec_to_xy(right_ra, right_dec, images[0].time)
        right = [(right_x[i], right_y[i]) for i, _ in enumerate(right_x)]

        patch1 = ax.add_patch(Polygon(left, ec=(1, 0, 0, 1), fc=(1, 0, 0, 0.05), lw=1))
        patch2 = ax.add_patch(Polygon(right, ec=(1, 0, 0, 1), fc=(1, 0, 0, 0.05), lw=1))

    # Load the Milky Way
    if toggle_mw:
        mw_ra, mw_dec = load_milky_way(images[0].time, True)
        mw_x, mw_y = radec_to_xy(mw_ra, mw_dec, images[0].time)
        mw_x, mw_y = trim(mw_x, mw_y)
        mw_scatter = ax.scatter(mw_x, mw_y, c=[(1, 0, 1, 1)], s=1)

    # Load the ecliptic
    if toggle_ep:
        ep_ra, ep_dec = load_ecliptic(images[0].time, True)
        ep_x, ep_y = radec_to_xy(ep_ra, ep_dec, images[0].time)
        ep_x, ep_y = trim(ep_x, ep_y)
        ep_scatter = ax.scatter(ep_x, ep_y, c=[(0, 1, 1, 1)], s=1)

    # Adds the image into the axes and displays it
    im = ax.imshow(images[0].data, cmap="gray", vmin=0, vmax=255)
    if toggle_pointing:
        telescope = ax.add_patch(Circle((0, 0), ec=(0, 1, 0, 1), fill=False, radius=10))
    coverup = ax.add_patch(Rectangle((0, 1024 - 50), 300, 50, fc = "black"))

    temp_text = str(start_time).split(" ")[1]
    text_time = ax.text(0, 1024 - 30, temp_text[0:5], fontsize=22, color="white")

    def update_img(n):
        if n % 10 == 0: print(n)

        cur_time = images[n // 2].time
        if n % 2 == 1:
          cur_time = cur_time + TimeDelta(60, format="sec")

        # Updates the clock at the lower left corner.
        temp_text = str(cur_time - TimeDelta(7 * 3600, format="sec")).split(" ")[1]
        text_time.set_text(temp_text[0:5] + " Local")

        if toggle_pointing:
            # Updates the telescope from the retrieved telemetry.
            telescope.set_center(altaz_to_xy(float(pointings[n][1]), float(pointings[n][2])))

        if toggle_survey:
            left_x, left_y = radec_to_xy(left_ra, left_dec, cur_time)
            left = [(left_x[i], left_y[i]) for i, _ in enumerate(left_x)]

            right_x, right_y = radec_to_xy(right_ra, right_dec, cur_time)
            right = [(right_x[i], right_y[i]) for i, _ in enumerate(right_x)]

            patch1.set_xy(left)
            patch2.set_xy(right)

        # Set offsets updates the positions of all the points defining the milky
        # way and ecliptic lines.
        if toggle_mw:
            mw_x, mw_y = radec_to_xy(mw_ra, mw_dec, cur_time)
            mw_x, mw_y = trim(mw_x, mw_y)
            mw = [(mw_x[i], mw_y[i]) for i, _ in enumerate(mw_x)]
            mw_scatter.set_offsets(mw)

        if toggle_ep:
            ep_x, ep_y = radec_to_xy(ep_ra, ep_dec, cur_time)
            ep_x, ep_y = trim(ep_x, ep_y)
            ep = [(ep_x[i], ep_y[i]) for i, _ in enumerate(ep_x)]
            ep_scatter.set_offsets(ep)

        # Index for accessing the correct image for this frame.
        # Since each frame is a minute and each image is two, each image stays
        # on screen for two frames.
        n = n // 2
        im.set_data(images[n].data)
        return im

    ani = animation.FuncAnimation(fig, update_img, (len(images) - 1) * 2, interval=30)
    writer = animation.writers['ffmpeg'](fps=20)

    date = str(start_time).split(" ")[0].replace("-", "")
    ani.save(f"{date}.mp4", writer=writer, dpi=dpi)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Required arguments
    parser.add_argument("start", help="starting time, in ISO-8601 format")
    # parser.add_argument("end", help="ending time of the video, in ISO-8601 format")

    # Optional arguments
    parser.add_argument("-im", "--image", help="whether or not to make a single image", action="store_true")
    parser.add_argument("-e", "--end", help="ending time of the video, in ISO-8601 format", default=None)

    parser.add_argument("-mw", "--milkyway", help="toggle the milky way", action="store_true")
    parser.add_argument("-ep", "--ecliptic", help="toggle the ecliptic", action="store_true")
    parser.add_argument("-s", "--survey", help="toggle the survey area", action="store_true")
    parser.add_argument("-p", "--pointing", help="toggle the telescope pointing", action="store_true")
    parser.add_argument("-a", "--all", help="toggle everything", action="store_true")

    args = parser.parse_args()

    if args.image:
        if args.all:
            create_image(args.start, None, True, True, True)
        else:
            create_image(args.start, None, args.milkyway, args.ecliptic, args.survey, args.pointing)

    elif args.end:
        if args.all:
            create_video(args.start, args.end, True, True, True, True)
        else:
            create_video(args.start, args.end, args.milkyway, args.ecliptic,
                        args.survey, args.pointing)
    else:
        print("If you request a movie, you must specify an ending time.")
