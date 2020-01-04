const pos = [31.96164, -111.60022] // Lat and long of the spacewatch cam

//viewBox is the size of the coordinate system so to speak, so the old 2048x1024
var svg = d3.select("body").append("div").classed("svg-container", true).append("svg")
          .attr("preserveAspectRatio", "xMinYMin meet").attr("viewBox", "0 0 2048 1024")
          .classed("svg-content-responsive", true);

// Setup for the image.
var src = "http://gagarin.lpl.arizona.edu/allsky/AllSkyCurrentImage.JPG";
var img = svg.append("svg:image").attr("xlink:href", src).attr("width", 1024).attr("height", 1024);

// Roughly but not exactly the RA/Dec of Polaris.
var ra = 2.5 * 15;
var dec = 89;

// Start of the J2000 Epoch is January 1, 2000 at 1200 UT.
// So year = 2000, month = 0 (January), day = 1, hour = 12
// minute = 0, second = 0
// Need to use this specific constructor because Date.parse() and all other constructors
// behave differently in different browsers (I ran into this because I use Safari)
const epoch_start = new Date(Date.UTC(2000, 0, 1, 12, 00, 00));

function radec_to_xy(ra, dec){
  let seconds = (Date.now() - epoch_start) / 1000; // Number of seconds elapsed since J2000

  // Double checked this days count against somewhere else, seems accurate to
  // within 1/1000 of a day
  let days = seconds / 3600 / 24; // 3600 seconds in an hour 24 hours per day

  // Finds the number of hours into the universal time day we are
  var today = new Date();
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
var circ = svg.append("circle").attr("r", 3.5).attr("cx", x).attr("cy", y).style("fill", "chartreuse").style("opacity", 1);
circ.opacity = 1 // Variable to easily access whether the circle is on or not.

// Handles the universal time clock on the right side.
var t_size = 200
var text = svg.append("text").attr("x", 1029).attr("y", t_size).attr("font-size", t_size + "px")
var ut_text = svg.append("text").attr("x", 1029).attr("y", 1.5 * t_size).attr("font-size", t_size / 2 + "px")

function update_clock() {
  today = new Date();
  // Kind of ridiculous that this is the only way to get leading 0s on the
  // values if the're less than ten.
  var hour = (today.getUTCHours() < 10 ? "0" : "") + today.getUTCHours();
  var minute = (today.getUTCMinutes() < 10 ? "0" : "") + today.getUTCMinutes();
  var second = (today.getUTCSeconds() < 10 ? "0" : "") + today.getUTCSeconds();
  var t = hour + ":" + minute + ":" + second + "ut";

  ut_text.text(t);

  hour = (today.getHours() < 10 ? "0" : "") + today.getHours();
  t = hour + ":" + minute + ":" + second;

  text.text(t);
}

// Timer that updates every 10ms. Less memory usage than 0ms lol.
var timer = d3.timer(update_clock, 10);

// Rounds to the nearest 1000th in one step.
let ra_rounded = Math.round(ra * 1000) / 1000;
let dec_rounded = Math.round(dec * 1000) / 1000;
let coord_text = "RA:" + ra_rounded + "\tDEC:" + dec_rounded;
var coords = svg.append("text").attr("x", 1029).attr("y", 1.5 * t_size + 85).attr("font-size", t_size / 2 + "px").text(coord_text);

// Plotting the survey area in red.
const left_data = "https://raw.githubusercontent.com/dylanagreen/desipoint/master/src/survey_left.json"
const right_data = "https://raw.githubusercontent.com/dylanagreen/desipoint/master/src/survey_right.json"
const mw_data = "https://raw.githubusercontent.com/dylanagreen/desipoint/master/src/mw.json"
const ecliptic_data = "https://raw.githubusercontent.com/dylanagreen/desipoint/master/src/ecliptic.json"

d3.json(left_data).then(function(d) {
  var xy = d.map(function(d) {
    return radec_to_xy(d[0], d[1]).join(",")
  }).join(" ");

  svg.append("polygon").attr("points", xy).attr("stroke", "red")
     .attr("stroke-width", 2).attr("fill", "red").attr("fill-opacity", 0.4);
});

d3.json(right_data).then(function(d) {
  var xy = d.map(function(d) {
    return radec_to_xy(d[0], d[1]).join(",")
  }).join(" ");

  svg.append("polygon").attr("points", xy).attr("stroke", "red")
     .attr("stroke-width", 2).attr("fill", "red").attr("fill-opacity", 0.4);
});

var survey_opacity = 1

// Line indicating the plane of the milky way
d3.json(mw_data).then(function(d) {
  var xy = d.map(function(d) {
    var point = radec_to_xy(d[0], d[1])
    let r = (512 - point[0]) * (512 - point[0]) + (512 - point[1]) * (512 - point[1])
    if(r < 509 * 509){
      console.log("asdf")
      return point.join(",")
    }
    else {
      return ""
    }
  }).join(" ");

  svg.append("polyline").attr("points", xy).attr("stroke", "magenta").attr("stroke-width", 2).attr("fill", "none").attr("id", "mw");
});

// // Line indicating the barycentric mean ecliptic
// d3.json(ecliptic_data).then(function(d) {
//   var xy = d.map(function(d) {
//     var point = radec_to_xy(d[0], d[1])
//     let r = (512 - point[0]) * (512 - point[0]) + (512 - point[1]) * (512 - point[1])
//     if(r < 509 * 509){
//       console.log("asdf")
//       return point.join(",")
//     }
//     else {
//       return ""
//     }
//   }).join(" ");

//   svg.append("polyline").attr("points", xy).attr("stroke", "cyan").attr("stroke-width", 2).attr("fill", "none").attr("id", "ecliptic");
// });

var mw_opacity = 1;
var ecliptic_opacity = 1;

// Function for toggling the telescope pointing on and off.
function toggle_telescope() {
  circ.opacity = circ.opacity == 1 ? 0: 1
  circ.style("opacity", circ.opacity)
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
  svg.select("polyline#mw").style("opacity", mw_opacity)
}

d3.select("#C").on("change", toggle_mw)

// // Function for toggling the galactic plane on and off.
// function toggle_ecliptic() {
//   ecliptic_opacity = ecliptic_opacity == 1 ? 0 : 1
//   svg.select("polyline#ecliptic").style("opacity", ecliptic_opacity)
// }

// d3.select("#D").on("change", toggle_ecliptic)