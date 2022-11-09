
from astropy.time import Time, TimeDelta
import numpy as np
from matplotlib.patches import Polygon, Circle, Rectangle
import matplotlib.pyplot as plt
from PIL import Image, UnidentifiedImageError
import requests

from io import BytesIO
import json

from .io import load_survey, load_milky_way, load_ecliptic
from .coordinates import altaz_to_xy

base_url = "http://varuna.kpno.noirlab.edu/allsky-all/images/cropped/"

class AllSkyImage():
    def __init__(self, data, time):
        self.data = data
        self.time = time

def create_image(time, toggle_mw=False, toggle_ep=False, toggle_survey=False,
                 toggle_pointing=False):

        # Start and end times for image range.
    im_time = Time(time).iso

    # Updating the start time to be the next avaliable image.
    temp_time = str(im_time)
    minutes = int(temp_time[-9:-7])
    # Sets minutes to next even minute if it is odd, and remains the same if even
    minutes = (minutes + 1) // 2 * 2
    temp_time = temp_time[:-9] + str(minutes) + ":05.000"

    im_time = Time(temp_time)
    print(f"Image for at {str(im_time)}")

    if toggle_pointing:
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
                  "sql": f"select time_recorded,mount_el,mount_az from telemetry.tcs_info where time_recorded < TIMESTAMP '{str(im_time)}' order by time_recorded desc limit 1"}
        # Ok so first get the resulting call, and decode it because its in bytes
        # then feed it to a csv reader which we then convert to a list so
        # now the table is a 2-d list.
        r = requests.get(query_url, params=params, auth=(auth["usr"], auth["pass"]))
        if r.status_code == 401:
          print("Invalid authentication!")
          return
        decoded = r.content.decode("utf-8")
        cr = csv.reader(decoded.splitlines(), delimiter=',')
        pointing = list(cr)

    else:
        print("Preparing to download image.")

    t = str(im_time)
    d = t.split(" ")[0] # Extract the current date in case the range ticks over.
    t = t.replace(":", "").replace("-", "").replace(" ", "_").split(".")[0]
    file_name = t + ".jpg"

    # Get the image data for this time from the server and then load
    url = base_url + d.replace("-", "/") + "/" + file_name
    try:
        response = requests.get(url)
        img = np.asarray(Image.open(BytesIO(response.content)))

        # Generate the Image object for appending.
        image = AllSkyImage(img, im_time)

    except UnidentifiedImageError:
        print(f"{t} image not found!")
        return
        # Increment to next image 120 seconds later.

    if toggle_pointing:
        pointing = pointing[1]
        print("Telemetry and image received and organized.")
    else:
        print("Image downloaded.")

    # Set up the figure the same way we usually do for saving so the image is the
    # only thing on the axis.
    dpi = 128
    y = image.data.shape[0] / dpi
    x = image.data.shape[1] / dpi

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
        left, right = load_survey(image.time)

        patch1 = ax.add_patch(Polygon(left, ec=(1, 0, 0, 1), fc=(1, 0, 0, 0.05), lw=1))
        patch2 = ax.add_patch(Polygon(right, ec=(1, 0, 0, 1), fc=(1, 0, 0, 0.05), lw=1))

    # Load the Milky Way
    if toggle_mw:
        mw_x, mw_y = load_milky_way(image.time)
        mw_scatter = ax.scatter(mw_x, mw_y, c=[(1, 0, 1, 1)], s=1)

    # Load the ecliptic
    if toggle_ep:
        ep_x, ep_y = load_ecliptic(image.time)
        ep_scatter = ax.scatter(ep_x, ep_y, c=[(0, 1, 1, 1)], s=1)

    # Adds the image into the axes and displays it
    im = ax.imshow(image.data, cmap="gray", vmin=0, vmax=255)
    if toggle_pointing:
        telescope = ax.add_patch(Circle((0, 0), ec=(0, 1, 0, 1), fill=False, radius=10))
        telescope.set_center(altaz_to_xy(float(pointing[1]), float(pointing[2])))

    # Covers corner text where the time will go
    coverup = ax.add_patch(Rectangle((0, 1024 - 50), 300, 50, fc = "black"))

    temp_text = str(im_time - TimeDelta(7 * 3600, format="sec")).split(" ")[1]
    text_time = ax.text(0, 1024 - 30, temp_text[0:5] + " Local", fontsize=22, color="white")

    date = str(im_time).split(" ")[0].replace("-", "")
    # plt.savefig(f"{date}.png", dpi=dpi)

    return fig, ax