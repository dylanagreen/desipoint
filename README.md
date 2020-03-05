# desipoint

desipoint is so named as it shows the current pointing of the DESI instrument on the night sky.
The goal is to be able to actively monitor the pointing of the telescope on live all-sky
images taken at the Spacewatch all-sky camera.

desipoint is currently hosted here on this github page: https://dylanagreen.github.io/desipoint/

## Details
- Base image is the [Spacewatch all-sky image](http://varuna.kpno.noao.edu/allsky/AllSkyCurrentImage.JPG).
- Toggleable overlays
  - DESI Survey Area in red.
  - Plane of the milkyway in purple.
  - Ecliptic in cyan
  - Moveable "telescope" in chartreuse.
- URL query params
  - RA/DEC of display pointing can be changed via *?ra=* and *?dec=*
  - Lookback using *?time=*
    - Time query string uses [ISO 8601 format.](https://en.wikipedia.org/wiki/ISO_8601)
    - Ex *?time=2019-06-27T06:09:10.104Z*