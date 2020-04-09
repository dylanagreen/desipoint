#!/usr/bin/env python3
import requests
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from astropy import units as u
from astropy.coordinates import SkyCoord, EarthLocation
from matplotlib.patches import Polygon, Circle, Rectangle
from astropy.time import Time, TimeDelta
from astropy.table import Table
from PIL import Image

import argparse
import ast
import os
from io import BytesIO

# In order to remove dependencies on kpno-allsky I've ported these functions
# over from the coordinates file.
r_sw = [0, 55, 110, 165, 220, 275, 330, 385, 435, 480, 510]
theta_sw = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95]
def radec_to_altaz(ra, dec, time):
    # This is the latitude/longitude of the camera
    camera = (31.959417 * u.deg, -111.598583 * u.deg)

    cameraearth = EarthLocation(lat=camera[0], lon=camera[1],
                                height=2120 * u.meter)

    # Creates the SkyCoord object
    radeccoord = SkyCoord(ra=ra, dec=dec, unit="deg", obstime=time,
                          location=cameraearth, frame="icrs",
                          temperature=5 * u.deg_C, pressure=78318 * u.Pa)

    # Transforms
    altazcoord = radeccoord.transform_to("altaz")

    return (altazcoord.alt.degree, altazcoord.az.degree)

def altaz_to_xy(alt, az):
    alt = np.asarray(alt)
    az = np.asarray(az)

    # Reverse of r interpolation
    r = np.interp(90 - alt, xp=theta_sw, fp=r_sw)
    az = az + 0.1 # Camera rotated 0.1 degrees.

    # Angle measured from vertical so sin and cos are swapped from usual polar.
    # These are x,ys with respect to a zero.
    x = -1 * r * np.sin(np.radians(az))
    y = r * np.cos(np.radians(az))

    # y is measured from the top!
    center = (512, 512)
    x = x + center[0]
    y = center[1] - y

    # Spacewatch camera isn't perfectly flat, true zenith is 2 to the right
    # and 3 down from center.
    x += 2
    y += 3

    return (x.tolist(), y.tolist())

def radec_to_xy(ra, dec, time):
    alt, az = radec_to_altaz(ra, dec, time)
    x, y = altaz_to_xy(alt, az)
    return (x, y)

class AllSkyImage():
    def __init__(self, data, time):
        self.data = data
        self.time = time

def create_video(toggle_mw=False, toggle_ep=False):

    date = "20200316"
    base_url = "http://varuna.kpno.noao.edu/allsky-all/images/cropped/"
    image_names = sorted(os.listdir(os.path.join(os.path.dirname(__file__), "Images", "Original", "SW", date)))

    # Start and end times for image range.
    d = date[:4] + "-" + date[4:6] + "-" + date[6:8]
    start_time = Time(d + " 02:30:05")
    end_time = Time(d + " 13:00:00")

    # Loops over the given time period in 120s increments, getting the image at
    # each time step.
    print("Preparing to download requested images.")
    images = []
    cur_time = start_time
    while cur_time < end_time:
        # Convert the time to a useable file name
        t = str(cur_time)
        d = t.split(" ")[0] # Extract the current date in case the range ticks over.
        t = t.replace(":", "").replace("-", "").replace(" ", "_").split(".")[0]
        file_name = t + ".jpg"

        # Get the image data for this time from the server and then load
        url = base_url + d.replace("-", "/") + "/" + file_name
        response = requests.get(url)
        img = np.asarray(Image.open(BytesIO(response.content)))

        # Generate the Image object for appending.
        temp = AllSkyImage(img, cur_time)
        images.append(temp)

        # Increment to next image 120 seconds later.
        cur_time = cur_time + TimeDelta(120, format="sec")

    print("Images downloaded, beginning overlay process.")
    print("Printing every 10th frame.")

    # Load the DESI survey area
    hull_loc = os.path.join(os.path.dirname(__file__), "data", "hull_radec.txt")
    with open(hull_loc, "r") as f:

        # Converts the string representation of the list to a list of points.
        left = f.readline()
        left = ast.literal_eval(left)

        left_ra = [c[0]for c in left]
        left_dec = [c[1] for c in left]

        right = f.readline()
        right = ast.literal_eval(right)

        right_ra = [c[0]for c in right]
        right_dec = [c[1] for c in right]

    # Load the Milky Way
    if toggle_mw:
        mw_loc = os.path.join(os.path.dirname(__file__), "src", "mw.json")
        with open(mw_loc, "r") as f:
            mw = f.readline()
            mw = ast.literal_eval(mw)

            # Makes the line dotted with 5 dot size gaps between the dots.
            mw = mw[::6]

            mw_ra = [c[0]for c in mw]
            mw_dec = [c[1] for c in mw]

    # Load the ecliptic
    if toggle_ep:
        ep_loc = os.path.join(os.path.dirname(__file__), "src", "ecliptic.json")
        with open(ep_loc, "r") as f:
            ep = f.readline()
            ep = ast.literal_eval(ep)

            ep2 = []
            for i in range(len(ep)):
                if i % 10 >= 2 and i % 10 <= 5:
                    ep2.append(ep[i])

            ep = ep2

            ep_ra = [c[0]for c in ep]
            ep_dec = [c[1] for c in ep]

    # Load the data for the pointing
    t = Table.read(os.path.join("data", f"night{date}.csv"))

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

    # Adds the image into the axes and displays it
    im = ax.imshow(images[0].data, cmap="gray", vmin=0, vmax=255)

    # Generating the x/y points for the desi survey areas
    left_x, left_y = radec_to_xy(left_ra, left_dec, images[0].time)
    left = [(left_x[i], left_y[i]) for i, _ in enumerate(left_x)]

    right_x, right_y = radec_to_xy(right_ra, right_dec, images[0].time)
    right = [(right_x[i], right_y[i]) for i, _ in enumerate(right_x)]

    def trim(x_in, y_in):
        x = 512 - np.copy(x_in)
        y = 512 - np.copy(y_in)
        r = np.hypot(x, y)

        for i in range(len(r)):
            if r[i] > 504:
                x[i] = float("nan")
                y[i] = float("nan")

        return (512 - x, 512 - y)

    if toggle_mw:
        mw_x, mw_y = radec_to_xy(mw_ra, mw_dec, images[0].time)
        mw_x, mw_y = trim(mw_x, mw_y)
        mw_scatter = ax.scatter(mw_x, mw_y, c=[(1, 0, 1, 1)], s=1)

    if toggle_ep:
        ep_x, ep_y = radec_to_xy(ep_ra, ep_dec, images[0].time)
        ep_x, ep_y = trim(ep_x, ep_y)
        ep_scatter = ax.scatter(ep_x, ep_y, c=[(0, 1, 1, 1)], s=1)


    patch1 = ax.add_patch(Polygon(left, ec=(1, 0, 0, 1), fc=(1, 0, 0, 0.05), lw=1))
    patch2 = ax.add_patch(Polygon(right, ec=(1, 0, 0, 1), fc=(1, 0, 0, 0.05), lw=1))

    telescope = ax.add_patch(Circle(altaz_to_xy(t["alt"][0], t["az"][0]), ec=(0, 1, 0, 1), fill=False, radius=10))

    coverup = ax.add_patch(Rectangle((0, 1024 - 50), 300, 50, fc = "black"))

    temp_text = t["label"][0]
    text_time = ax.text(0, 1024 - 30, temp_text[0:8], fontsize=22, color="white")
    text_prog = ax.text(175, 1024 - 30, temp_text[8:], fontsize=22, color="white")

    def update_img(n):
        if n % 10 == 0: print(n)
        n = n # Need to increment n by 1 for labeling purposes.
        temp_text = t["label"][n]
        text_time.set_text(temp_text[0:8])
        if temp_text[8:] != "":
            text_prog.set_text(temp_text[8:])
            text_prog.set_alpha(1)
        else:
            text_prog.set_alpha(0.5)

        telescope.set_center(altaz_to_xy(t["alt"][n], t["az"][n]))

        # Index for accessing the correct image for this frame.
        # Since each frame is a minute and each image is two, each image stays
        # on screen for two frames.
        n = (n) // 2

        left_x, left_y = radec_to_xy(left_ra, left_dec, images[n].time)
        left = [(left_x[i], left_y[i]) for i, _ in enumerate(left_x)]

        right_x, right_y = radec_to_xy(right_ra, right_dec, images[n].time)
        right = [(right_x[i], right_y[i]) for i, _ in enumerate(right_x)]

        patch1.set_xy(left)
        patch2.set_xy(right)


        if toggle_mw:
            mw_x, mw_y = radec_to_xy(mw_ra, mw_dec, images[n].time)
            mw_x, mw_y = trim(mw_x, mw_y)
            mw = [(mw_x[i], mw_y[i]) for i, _ in enumerate(mw_x)]
            mw_scatter.set_offsets(mw)

        if toggle_ep:
            ep_x, ep_y = radec_to_xy(ep_ra, ep_dec, images[n].time)
            ep_x, ep_y = trim(ep_x, ep_y)
            ep = [(ep_x[i], ep_y[i]) for i, _ in enumerate(ep_x)]
            ep_scatter.set_offsets(ep)

        im.set_data(images[n].data)
        return im

    ani = animation.FuncAnimation(fig, update_img, len(images) * 2 - 1, interval=30)
    writer = animation.writers['ffmpeg'](fps=20)

    ani.save(f"{date}.mp4", writer=writer, dpi=dpi)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-mw", "--milkyway", help="toggle the milky way", action="store_true")
    parser.add_argument("-ep", "--ecliptic", help="toggle the ecliptic", action="store_true")

    args = parser.parse_args()

    create_video(args.milkyway, args.ecliptic)
