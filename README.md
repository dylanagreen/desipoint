# desipoint

desipoint is so named as it shows the current pointing of the DESI instrument on the night sky.
The goal is to be able to actively monitor the pointing of the telescope on live all-sky
images taken at the Spacewatch all-sky camera. desipoint additionally includes a
paired down script version of the website, see below for details.

desipoint is planned to be hosted here on this github page: https://dylanagreen.github.io/desipoint/.
Currently there is an http/https interop problem, so temporarily desipoint is hosted here:
http://craven-paint.surge.sh.

## Details (Website)
- Base image is the [Spacewatch all-sky image.](http://varuna.kpno.noao.edu/allsky/AllSkyCurrentImage.JPG)
- Toggleable overlays
  - DESI Survey Area in red.
  - Plane of the milkyway in purple.
  - Ecliptic in cyan.
  - Moveable "telescope" in chartreuse.
- URL query params
  - RA/DEC of display pointing can be changed via *?ra=* and *?dec=*
  - Lookback using *?time=*
    - Time query string uses [ISO 8601 format.](https://en.wikipedia.org/wiki/ISO_8601)
    - Ex *?time=2019-06-27T06:09:10.104Z*
- Toggleable automatic telescope tracking
  - By default "telescope" will track the most recent pointing request.

## Details (Script)
- desipoint.py script creates timelapse videos of the desipoint website overlay.
- Start and end times are mandatory.
- Command line switches:
  - *--milkyway* (*-mw*) for toggling the milky way plane
  - *--ecliptic* (*-ep*) for toggling the ecliptic plane
  - *--survey* (*-s*)for toggling the survey area
- Use *--help* for more details.