const pos = [31.96164, -111.60022] // Lat and long of the spacewatch cam

// Data for the survey area, galactic plane, and ecliptic.
const left_data = "https://raw.githubusercontent.com/dylanagreen/desipoint/master/src/survey_left.json"
const right_data = "https://raw.githubusercontent.com/dylanagreen/desipoint/master/src/survey_right.json"
const mw_data = "https://raw.githubusercontent.com/dylanagreen/desipoint/master/src/mw.json"
const ecliptic_data = "https://raw.githubusercontent.com/dylanagreen/desipoint/master/src/ecliptic.json"

// Image location
// var src = "http://gagarin.lpl.arizona.edu/allsky/AllSkyCurrentImage.JPG";
var src = "http://varuna.kpno.noao.edu/allsky/AllSkyCurrentImage.JPG"

// Variables to hold the opacity of each element.
var survey_opacity = 1;
var mw_opacity = 1;
var ecliptic_opacity = 1;
var circ_opacity = 1;

// Whether or not to update the display
var update = true;
var today = new Date();

//viewBox is the size of the coordinate system so to speak, so the old 2048x1024
var svg = d3.select("body").append("div").classed("svg-container", true).append("svg")
          .attr("preserveAspectRatio", "xMinYMin meet").attr("viewBox", "0 0 2048 1024")
          .classed("svg-content-responsive", true);

var im_layer = svg.append("g")
var overlay = svg.append("g")

// Base objects for the overlay. These are first so tha the telescope pointing
// circle is the highest object in z-order.

// Ecliptic base
overlay.append("g").attr("id", "ecliptic");

// Galactic plane base
overlay.append("g").attr("id", "mw");

// Survey Bases
overlay.append("polygon").attr("stroke", "red").attr("stroke-width", 2)
       .attr("fill", "red").attr("fill-opacity", 0.2).attr("id", "survey_left");

overlay.append("polygon").attr("stroke", "red").attr("stroke-width", 2)
       .attr("fill", "red").attr("fill-opacity", 0.2).attr("id", "survey_right");

// Add the base image.
im_layer.append("svg:image").attr("width", 1024).attr("height", 1024)
        .attr("xlink:href", src).attr("id", "image")


// Sets up the telescope pointing.
// Roughly but not exactly the RA/Dec of Polaris as defaults
const urlParams = new URLSearchParams(window.location.search);
var it = urlParams.keys();
var ra = 2.5 * 15
var dec = 89

var result = it.next();
for (const [key, val] of urlParams) {
  if (key.toLowerCase() == "ra") {
    var url_ra = val;
    if (!Number.isNaN(url_ra)){
      ra = Number(url_ra)
    }
  }

  if (key.toLowerCase() == "dec") {
    var url_dec = val;
    if (!Number.isNaN(url_dec)){
      dec = Number(url_dec)
    }
  }

  if (key.toLowerCase() == "time") {
    var url_time = val;
    var test_date = new Date(url_time);
    // Check to see if the date is valid.
    if (isNaN(test_date.getTime()) || test_date > Date.now()){
      console.log("Invalid date entered");
    }
    else {
      // Source where the old images are stored.
      var temp_src = "http://varuna.kpno.noao.edu/allsky-all/images/cropped/";
      temp_src = temp_src + test_date.getUTCFullYear().toString() + "/";

      // Get the month and date for the url
      var month = (test_date.getUTCMonth() < 9 ? "0" : "") + (test_date.getUTCMonth() + 1);
      var date = (test_date.getUTCDate() < 10 ? "0" : "") + test_date.getUTCDate();

      temp_src = temp_src + month + "/";
      temp_src = temp_src + date + "/";

      // Set up the filename.
      var file_name = test_date.getUTCFullYear().toString() + month + date + "_";

      var hour = (test_date.getUTCHours() < 10 ? "0" : "") + test_date.getUTCHours();
      var temp_minute = test_date.getUTCMinutes();
      temp_minute = temp_minute % 2 == 0 ? temp_minute : temp_minute - 1;
      var minute = (temp_minute < 10 ? "0" : "") + temp_minute;

      // Smash them together to set the image source.
      file_name = file_name + hour + minute + "05.jpg";
      temp_src = temp_src + file_name;

      // Set the image src to the, well, source.
      src = temp_src;
      update = false;
      today = test_date;
    }
  }
  result = it.next();
}
// Start of the J2000 Epoch is January 1, 2000 at 1200 UT.
// So year = 2000, month = 0 (January), day = 1, hour = 12
// minute = 0, second = 0
// Need to use this specific constructor because Date.parse() and all other constructors
// behave differently in different browsers (I ran into this because I used Safari)
const epoch_start = new Date(Date.UTC(2000, 0, 1, 12, 00, 00));

// Function that converts from ra dec to xy
function radec_to_xy(ra, dec){
  // Finds the number of hours into the universal time day we are
  today = update ? new Date() : today;

  let seconds = (today.getTime() - epoch_start) / 1000; // Number of seconds elapsed since J2000

  // Double checked this days count against somewhere else, seems accurate to
  // within 1/1000 of a day
  let days = seconds / 3600 / 24; // 3600 seconds in an hour 24 hours per day

  var ut = today.getUTCHours() +  today.getUTCMinutes() / 60;

  // Makes sure universal time is on 24 hour time and not 48.
  ut = (ut < 24) ? ut : ut - 24;

  // Calculates Local Sidereal Time
  var lst = 100.46 + 0.985647 * days + pos[1] + 15 * ut;

  // First step to bringing LST to within 0-360.
  // Days is usually close to 7200 so this is a good first approximation
  lst = lst - (360 * 20);

  // Ensures lst is in the good range.
  lst = (lst < 0) ? lst + 360 : lst;
  lst = (lst > 360) ? lst - 360 : lst;
  // I double checked this as well and it is within a minute of real LST

  var hour = lst - ra; // Hour angle

  // Conversions to radians
  dec = dec * Math.PI / 180;
  ra = ra * Math.PI / 180;
  hour = hour * Math.PI / 180;
  var lat = pos[0] * Math.PI / 180;

  // Finds sine of altitude hence taking asin after.
  // Cunning algorithm I found. Allegedly by Peter Duffet-Smith in
  // Practical Astornomy with your Calculator
  var alt = Math.sin(dec) * Math.sin(lat) + Math.cos(dec) * Math.cos(lat) * Math.cos(hour);
  alt = Math.asin(alt)

  var az = (Math.sin(dec) - Math.sin(alt) * Math.sin(lat)) / (Math.cos(alt) * Math.cos(lat));

  // Conversion to degrees, which is needed for the interpolation.
  az = Math.acos(az) * 180 / Math.PI;
  alt = alt * 180 / Math.PI;

  // Makes sure the azimuthal angle is in a good range.
  if (Math.sin(hour) > 0) {
    az = 360 - az;
  }

  // Interpolation tables.
  const r_sw = [0, 55, 110, 165, 220, 275, 330, 385, 435, 480, 510];
  const theta_sw = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95];

  // var alt = 20;
  // var az = 90;

  alt = 90 - alt; // Since alt is measured up from the horizon and we need it from center
  let ind = theta_sw.indexOf(alt); // Checks to see if the item is in the conversion already

  var r = 0;

  // Finding the r value corresponding to the altitude
  if (ind > -1) {
    r = r_sw[ind];
  }
  else if (alt > 95) { // If the alt is outside the circle
    r = 510
  }
  else {
    for (i = 0; i < theta_sw.length; i++){
      // Once we find one that is less than the alt, we can do a linear
      // interpolation to find the corresponding r value.
      if (theta_sw[i] < alt){
        let m = (r_sw[i + 1] - r_sw[i]) / (theta_sw[i + 1] - theta_sw[i]); // Slope
        let b = -m * theta_sw[i] + r_sw[i]; // r axis intercept
        r = m * alt + b;
      }
    }
  }

  let x = 512 - r * Math.sin(az * Math.PI / 180);
  let y = 512 - r * Math.cos(az * Math.PI / 180);

  return [x, y]
}

let new_coords = radec_to_xy(ra, dec)
let x = new_coords[0]
let y = new_coords[1]

// Circle at the given position.
// I didn't know that chartreuse was a green color.
var circ = overlay.append("circle").attr("r", 10).attr("cx", x).attr("cy", y)
              .style("stroke", "chartreuse").style("stroke-width", 4)
              .style("opacity", 1).style("fill-opacity", 0);

// Handles the universal time clock on the right side.
var t_size = 200
var text = svg.append("text").attr("x", 1029).attr("y", t_size).attr("font-size", t_size + "px")
var ut_text = svg.append("text").attr("x", 1029).attr("y", 1.5 * t_size).attr("font-size", t_size / 2 + "px")

function update_clock() {
  today = update ? new Date() : today;
  // Kind of ridiculous that this is the only way to get leading 0s on the
  // values if the're less than ten.
  var hour = (today.getUTCHours() < 10 ? "0" : "") + today.getUTCHours();
  var minute = (today.getUTCMinutes() < 10 ? "0" : "") + today.getUTCMinutes();
  var second = (today.getUTCSeconds() < 10 ? "0" : "") + today.getUTCSeconds();
  var t = hour + ":" + minute + ":" + second + "ut";

  ut_text.text(t);

  var adjusted_hour = today.getUTCHours() - 7
  // This line ensures that we work on 24 hour time and not negative time.
  adjusted_hour = adjusted_hour < 0 ? adjusted_hour + 24 : adjusted_hour
  hour = (adjusted_hour < 10 ? "0" : "") + adjusted_hour;
  t = hour + ":" + minute + ":" + second;

  text.text(t);
}

// Timer that updates clock every 100ms. Less memory usage than 0ms lol.
var timer = d3.interval(update_clock, 100);

// Rounds to the nearest 1000th in one step.
let ra_rounded = Math.round(ra * 1000) / 1000;
let dec_rounded = Math.round(dec * 1000) / 1000;
var clean = false

function update_coords() {
  var ra_str = document.getElementById("ra").value
  var new_ra = Number(ra_str)
  // Sets the ra to the new one as long as its not nan and is allowed.
  if (!Number.isNaN(new_ra)) {
    ra = Number(new_ra)
  }
  else {
    document.getElementById("ra").value = ra
  }

  var dec_str = document.getElementById("dec").value
  var new_dec = Number(dec_str)
  if (!Number.isNaN(new_dec)) {
    dec = Number(new_dec)
  }
  else {
    document.getElementById("dec").value = dec
  }

  update_pointing() // Updates the telescope dot itself.
  clean = true
}

// Don't think I need to ever access these again so I shouldn't need to put them
// into a variable.
svg.append("text").attr("x", 1029).attr("y", 1.5 * t_size + 135)
   .attr("font-size", t_size / 2 + "px").text("RA:");
svg.append("text").attr("x", 1029).attr("y", 1.5 * t_size + 235)
   .attr("font-size", t_size / 2 + "px").text("DEC:");

var ra_text = svg.append("foreignObject").attr("width", 512).attr("height", 500)
                 .attr("x", 1029 + 250).attr("y", 1.5 * t_size + 40)
                 .html("<input type=text id=ra size=5/>")
                 .on("keypress", function() {
                   if(d3.event.keyCode === 13){
                     update_coords()
                   }
                });

var dec_text = svg.append("foreignObject").attr("width", 1024).attr("height", 500)
                  .attr("x", 1029 + 250).attr("y", 1.5 * t_size + 145)
                  .html("<input type=text id=dec size=5/>")
                  .on("keypress", function() {
                    if(d3.event.keyCode === 13){
                      update_coords()
                    }
                  });

// Listener for the focus out update.
document.getElementById("ra").addEventListener("focusout", update_coords)
document.getElementById("dec").addEventListener("focusout", update_coords)

function update_survey() {
  // Plotting the survey area in red.
  d3.json(left_data).then(function(d) {
    var xy = d.map(function(d) {
      return radec_to_xy(d[0], d[1]).join(",")
    }).join(" ");

    overlay.select("polygon#survey_left").attr("points", xy);
      // Above line nsures the opacity remains the same between redraws
  });

  d3.json(right_data).then(function(d) {
    var xy = d.map(function(d) {
      return radec_to_xy(d[0], d[1]).join(",")
    }).join(" ");

    overlay.select("polygon#survey_right").attr("points", xy);
  });
}

function update_galactic_plane() {
  // Line indicating the plane of the milky way
  d3.json(mw_data).then(function(d) {
    var xy = d.map(function(d) {
      var point = radec_to_xy(d[0], d[1])
      let r = (512 - point[0]) * (512 - point[0]) + (512 - point[1]) * (512 - point[1])
      if(r < 509 * 509){
        return point
      }
      else {
        return null
      }
    }).filter(function(d) {
      return d != null;
    }); // Strip out the nulll elements

    // Selects all the dots and update the data array.
    var circles = overlay.select("g#mw").selectAll("circle").data(xy);

    // Removes any circles that don't have new positions i.e. if we have less
    // circles than before
    circles.exit().remove()

    // Updates the positions of the remaining circles.
    circles.attr("cx", function(d) { return d[0]; })
           .attr("cy", function(d) { return d[1]; });

    // Adds any required circles, i.e. if we have more points than before.
    circles.enter().append("circle")
           .attr("cx", function(d) { return d[0]; })
           .attr("cy", function(d) { return d[1]; })
           .attr("r", 1.1)
           .attr("fill", "magenta");
  });
}

function update_ecliptic() {
  // Line indicating the barycentric mean ecliptic
  d3.json(ecliptic_data).then(function(d) {
    var xy = d.map(function(d) {
      var point = radec_to_xy(d[0], d[1])
      let r = (512 - point[0]) * (512 - point[0]) + (512 - point[1]) * (512 - point[1])
      if(r < 509 * 509){
        return point
      }
      else {
        return null
      }
    }).filter(function(d) {
      return d != null;
    }); // Strip out the null elements

    // Selects all the dots and update the data array.
    var circles = overlay.select("g#ecliptic").selectAll("circle").data(xy);

    // Removes any circles that don't have new positions i.e. if we have less
    // circles than before
    circles.exit().remove()

    // Updates the positions of the remaining circles.
    circles.attr("cx", function(d) { return d[0]; })
           .attr("cy", function(d) { return d[1]; });

    // Adds any required circles, i.e. if we have more points than before.
    circles.enter().append("circle")
           .attr("cx", function(d) { return d[0]; })
           .attr("cy", function(d) { return d[1]; })
           .attr("r", 1.1)
           .attr("fill", "cyan");
  });
}

function update_pointing() {
  // Updates the circle's coordinates
  let new_coords = radec_to_xy(ra, dec)
  circ.attr("cx", new_coords[0]).attr("cy", new_coords[1])
}

// Catchall function for drawing the image with everything on top of it.
function draw_canvas() {
  // Updates for each individual piece
  update_ecliptic()
  update_galactic_plane()
  update_survey()
  update_pointing()

  // Resetting the text fields to whatever the new RA/DEC is in case they change.
  document.getElementById("ra").value = Math.round(ra * 1000) / 1000
  document.getElementById("dec").value = Math.round(dec * 1000) / 1000
}

function update_image() {
  // The new fetched image.
  let imsrc = src + "?" + Date.now();
  im_layer.select("image").attr("xlink:href", imsrc).attr("id", "image");
}

draw_canvas() // Call the draw function first to draw everything.
update_image()

if (update) {
  // Exectutes the update function every 60 seconds for the canvas, 120 for the image
  d3.interval(draw_canvas, 60 * 1000)
  d3.interval(update_image, 120 * 1000)
}

// BUTTONS BELOW THIS POINT

// Function for toggling the telescope pointing on and off.
function toggle_telescope() {
  circ_opacity = circ_opacity == 1 ? 0: 1
  circ.style("opacity", circ_opacity)
}

d3.select("#A").on("change", toggle_telescope);

// Function for toggling the survey area on and off.
function toggle_survey() {
  survey_opacity = survey_opacity == 1 ? 0 : 1
  svg.selectAll("polygon").style("opacity", survey_opacity)
}

d3.select("#B").on("change", toggle_survey)

// Function for toggling the galactic plane on and off.
function toggle_mw() {
  mw_opacity = mw_opacity == 1 ? 0 : 1
  svg.select("g#mw").style("opacity", mw_opacity)
}

d3.select("#C").on("change", toggle_mw)

// Function for toggling the galactic plane on and off.
function toggle_ecliptic() {
  ecliptic_opacity = ecliptic_opacity == 1 ? 0 : 1
  svg.select("g#ecliptic").style("opacity", ecliptic_opacity)
}

d3.select("#D").on("change", toggle_ecliptic)

// jQuery.get("http://web.replicator.dev-cattle.stable.spin.nersc.org:60040/TV3/app/Q/query?namespace=telemetry&format=html&width=600&height=400&ymin=None&ymax=None&sql=select+date_ut%2Ctarget_ra%2Ctarget_dec+from+telemetry.tcs_info+order+by+tcs_info+desc+limit+1", success=function(d){console.log(d)})
// console.log(jQuery.get("http://web.replicator.dev-cattle.stable.spin.nersc.org:60040/TV3/app/Q/query", "namespace=telemetry"))
