# desipoint

`desipoint` is so named as it shows the pointing of the DESI instrument and the DESI survey area plotted on the night sky.

`desipoint` is also available as a website hosted here on this github page: https://dylanagreen.github.io/desipoint/, and more details can be found by switching to the `web` branch.


## Details

`desipoint` represents a small suite of software designed to make working with Spacewatch all-sky images easier for the DESI collaboration. Detailed documentation is forthcoming.

## Requirements

- astropy
- numpy
- matplotlib

## Scripts

`desipoint` also provides some scripts, one to produce static images and one to produce animated videos:

- Command line switches:
  - *--milkyway* (*-mw*) for toggling the milky way plane
  - *--ecliptic* (*-ep*) for toggling the ecliptic plane
  - *--survey* (*-s*) for toggling the survey area
  - *--pointing* (*-p*) for toggling the telescope pointing
  - *--all* (*-a*) for conveniently toggling on all of the above
- Use *--help* for more details.

See `scripts/` for more details.