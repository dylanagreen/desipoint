const pos = [31.96164, -111.60022] // Lat and long of the spacewatch cam

// I'm recognizing already problems in that the image doesn't encode the
// date/time into the image name.
var src = "http://gagarin.lpl.arizona.edu/allsky/AllSkyCurrentImage.JPG";

var svg = d3.select("body").append("svg").attr("width", 1024).attr("height", 1024);

// // Image object. At least the syntax reminds me heavily of Nim.
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

let seconds = (Date.now() - epoch_start) / 1000; // Number of seconds elapsed since J2000

// Double checked this days count against somewhere else, seems accurate to
// within 1/1000 of a day
let days = seconds / 3600 / 24; // 3600 seconds in an hour 24 hours per day

// Finds the number of hours into the universal time day we are
let today = new Date();
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

// Circle at the given position.
// I didn't know that chartreuse was a green color.
svg.append("circle").attr("r", 3.5).attr("cx", x).attr("cy", y).attr("style", "fill: chartreuse");
