# desipoint

`desipoint` is so named as it shows the pointing of the DESI instrument and the DESI survey area plotted on the night sky.  This branch represents the web version of `desipoint`.

`desipoint` is hosted here on this github page: https://dylanagreen.github.io/desipoint/

## Features (Website)
- Base image is the [Spacewatch all-sky image.](http://varuna.kpno.noirlab.edu/allsky/AllSkyCurrentImage.JPG)
- Toggleable overlays
  - DESI Survey Area in red.
  - Plane of the milkyway in purple.
  - Ecliptic in cyan.
  - Moveable "telescope" in chartreuse.
- URL query params
  - RA/DEC of display pointing can be changed via `?ra=` and `?dec=`
  - Lookback using `?time=`
    - Time query string uses [ISO 8601 format.](https://en.wikipedia.org/wiki/ISO_8601)
    - i.e. `?time=2019-06-27T06:09:10.104Z`

  -  Example URL: *https://dylanagreen.github.io/desipoint/?time=2022-02-09T07:10:58Z&ra=144.516*
- Toggleable automatic telescope tracking
  - By default "telescope" will track the most recent pointing request.
  - Clicking the "on" or "off" text will invert the tracking state.
