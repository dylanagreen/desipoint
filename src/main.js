// I'm recognizing already problems in that the image doesn't encode the
// date/time into the image name.
var src = "http://gagarin.lpl.arizona.edu/allsky/AllSkyCurrentImage.JPG";

var svg = d3.select("body").append("svg").attr("width", 1024).attr("height", 1024);

// // Image object. At least the syntax reminds me heavily of Nim.
var img = svg.append("svg:image").attr("xlink:href", src).attr("width", 1024).attr("height", 1024);

// Circle at the zenith position.
svg.append("circle").attr("r", 3.5).attr("cx", 512).attr("cy", 512).attr("style", "fill: chartreuse")