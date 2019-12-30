const pos = [31.96164, -111.60022] // Lat and long of the spacewatch cam

// I'm recognizing already problems in that the image doesn't encode the
// date/time into the image name.
var src = "http://gagarin.lpl.arizona.edu/allsky/AllSkyCurrentImage.JPG";

var svg = d3.select("body").append("svg").attr("width", 1024).attr("height", 1024);

// // Image object. At least the syntax reminds me heavily of Nim.
var img = svg.append("svg:image").attr("xlink:href", src).attr("width", 1024).attr("height", 1024);

// Circle at the zenith position.
// I didn't know that chartreuse was a green color.
svg.append("circle").attr("r", 3.5).attr("cx", 512).attr("cy", 512).attr("style", "fill: chartreuse");

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
console.log(days)

// Finds the number of hours into the universal time day we are
let today = new Date()
var ut = today.getHours() + 8 + today.getMinutes() / 60 // + 8 to get from local to UT

// Makes sure universal time is on 24 hour time and not 48.
ut = (ut < 24) ? ut : ut - 24

console.log(ut)

// Calculates Local Sidereal Time
var lst = 100.46 + 0.985647 * days + (-117.826508) + 15 * ut

// First step to bringing LST to within 0-360.
// Days is usually close to 7200 so this is a good first approximation
lst = lst - (360 * 20)

// Ensures lst is in the good range.
lst = (lst < 0) ? lst + 360 : lst
lst = (lst > 360) ? lst - 360 : lst
// I double checked this as well and it is within a minute of real LST

console.log(lst/15)

