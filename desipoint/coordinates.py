from astropy import units as u
from astropy.coordinates import SkyCoord, EarthLocation
import numpy as np

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
    # In case you pass in lists
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

    # Spacewatch camera isn't perfectly aligned, true zenith is 2 to the right
    # and 3 down from center.
    x += 2
    y += 3

    return (x.tolist(), y.tolist())

def radec_to_xy(ra, dec, time):
    alt, az = radec_to_altaz(ra, dec, time)
    x, y = altaz_to_xy(alt, az)
    return (x, y)

# Function that trims off any points that are outside the ~512 radius circle
def trim(x_in, y_in):
    x = 512 - x_in
    y = 512 - y_in
    r = np.hypot(x, y)

    # TODO: Vectorize this using numpy
    for i in range(len(r)):
        if r[i] > 504:
            x[i] = float("nan")
            y[i] = float("nan")

    return (512 - x, 512 - y)
