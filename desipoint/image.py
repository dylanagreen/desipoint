from astropy.time import Time, TimeDelta
from matplotlib.patches import Polygon, Circle, Rectangle
import matplotlib.pyplot as plt

from datetime import datetime

from .io import (load_survey, load_milky_way, load_ecliptic, download_telemetry,
                download_image)
from .coordinates import altaz_to_xy

def create_image(time, image=None, toggle_mw=False, toggle_ep=False, toggle_survey=False,
                 toggle_pointing=False):

    # If image isn't passed in then we download the image
    # Start and end times for image range.
    if time == "now":
        im_time = Time.now().iso
    else:
        im_time = Time(time).iso

    # Updating the start time to be the next available image.
    temp_time = str(im_time)
    minutes = int(temp_time[-9:-7])
    # Sets minutes to next even minute if it is odd, and remains the same if even
    minutes = (minutes + 1) // 2 * 2

    # Sets the seconds to always be at 5 seconds. This time format (Even minutes
    # and 5 seconds after) is the datetime each image is taken.
    temp_time = temp_time[:-9] + str(minutes) + ":05.000"
    im_time = Time(temp_time)
    print(f"Image for at {str(im_time)}")

    if image is None:
        print("Preparing to download image.")

        image = download_image(im_time)

    if toggle_pointing:
            print("Downloading telemetry...")
            pointing = download_telemetry(im_time)[1]

    # We failed to download the image if this triggers after the above block.
    if image is None:
        return

    print("Image loaded.")

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
        mw_scatter = ax.plot(mw_x, mw_y, c=(1, 0, 1, 1))#, s=1)

    # Load the ecliptic
    if toggle_ep:
        ep_x, ep_y = load_ecliptic(image.time)
        ep_scatter = ax.plot(ep_x, ep_y, c=(0, 1, 1, 1))#, s=1)

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

    return fig, date, dpi