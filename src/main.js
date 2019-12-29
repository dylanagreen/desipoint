// Image object. At least the syntax reminds me heavily of Nim.
var img = document.createElement("img")
// I'm recognizing already problems in that the image doesn't encode the
// date/time into the image name.
img.src = "http://gagarin.lpl.arizona.edu/allsky/AllSkyCurrentImage.JPG"

document.body.appendChild(img) // Add to the DOM.