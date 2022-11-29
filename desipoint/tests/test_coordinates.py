import pathlib
import unittest

from astropy.time import Time
import numpy as np

from desipoint.coordinates import altaz_to_xy, radec_to_xy, radec_to_altaz

file_loc = pathlib.Path(__file__).parent.resolve() / "test_files"

class TestCoordinateConversions(unittest.TestCase):
    def test_radec_to_altaz(self):
        # Grid that uniformly samples the image at the test timestamp.
        radec_grid = np.load(file_loc / "radec_grid.npy")

        # Only a semi-arbitrary date.
        t = Time("2021-10-09T08:45:00Z")

        observed_alt, observed_az = radec_to_altaz(radec_grid[0], radec_grid[1], t)

        expected = np.load(file_loc / "expected_radec_altaz.npy")
        # Expected is a vstack of the two observed arrays.
        self.assertTrue(np.allclose(observed_alt, expected[0]))
        self.assertTrue(np.allclose(observed_az, expected[1]))

    def test_radec_to_xy(self):
        # Grid that uniformly samples the image at the test timestamp.
        radec_grid = np.load(file_loc / "radec_grid.npy")

        # Only a semi-arbitrary date.
        t = Time("2021-10-09T08:45:00Z")

        observed_x, observed_y = radec_to_xy(radec_grid[0], radec_grid[1], t)

        expected = np.load(file_loc / "expected_radec_xy.npy")
        # Expected is a vstack of the two observed arrays.
        self.assertTrue(np.allclose(observed_x, expected[0]))
        self.assertTrue(np.allclose(observed_y, expected[1]))


    def test_altaz_to_xy(self):
        # Set up the alt az grid
        min_alt = 0
        max_alt = 90

        min_az = 0
        max_az = 360

        alt_base = np.linspace(min_alt, max_alt, 25)

        alt = []
        az = []

        # Sets up the grid to have a different number of points at each
        # azimuthal angle to cover a fuller range of the circular area
        for a in alt_base:
            az_base = np.linspace(min_az, max_az, (90 - int(a)))
            az.append(az_base)
            alt.append([a] * len(az_base))

        alt = np.concatenate(alt)
        az = np.concatenate(az)

        observed_x, observed_y = altaz_to_xy(alt, az)
        expected = np.load(file_loc / "expected_altaz_xy.npy")
        # Expected is a vstack of the two observed arrays.
        self.assertTrue(np.allclose(observed_x, expected[0]))
        self.assertTrue(np.allclose(observed_y, expected[1]))
