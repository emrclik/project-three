var svgWidth = 960;
var svgHeight = 500;

var margin = {
  top: 60,
  right: 40,
  bottom: 60,
  left: 100
};

var width = svgWidth - margin.left - margin.right;
var height = svgHeight - margin.top - margin.bottom;


// Create an SVG wrapper, append an SVG group that will hold our chart, and shift the latter by left and top margins.
var svg = d3.select(".chart")
  .append("svg")
  .attr("width", svgWidth)
  .attr("height", svgHeight)
  .style("background-color", "rgb(233, 233, 233)")

var chartGroup = svg.append("g")
  .attr("transform", `translate(${margin.left}, ${margin.top})`);


// Import Data
d3.csv("trip_duration_comparison.csv", function (err, tripData) {
  if (err) throw err;

  // Step 1: Parse Data/Cast as numbers
   // ==============================
  tripData.forEach(function (data) {
    data.bike_duration_mins = +data.bike_duration_mins;
    data.public_duration_mins = +data.public_duration_mins;
  });

  // Step 2: Create scale functions
  // ==============================
  var xLinearScale = d3.scaleLinear()
    .domain([-20, d3.max(tripData, d => d.bike_duration_mins)])
    .range([0, width]);

  var yLinearScale = d3.scaleLinear()
    .domain([50, d3.max(tripData, d => d.frequency)])
    .range([height, 0]);

  // Step 3: Create axis functions
  // ==============================
  var bottomAxis = d3.axisBottom(xLinearScale);
  var leftAxis = d3.axisLeft(yLinearScale);

  // Step 4: Append Axes to the chart
  // ==============================
  chartGroup.append("g")
    .attr("transform", `translate(0, ${height})`)
    .call(bottomAxis);

  chartGroup.append("g")
    .call(leftAxis);


   // Step 5: Create Circles
  // ==============================
  var circlesGroup = chartGroup.selectAll("circle")
  .data(tripData)
  .enter()
  .append("circle")
  .attr("cx", d => xLinearScale(d.time_saved))
  .attr("cy", d => yLinearScale(d.frequency))
  .attr("r", function(d) {return Math.sqrt(d.frequency); })
  .attr("fill", "rgb(84, 159, 224)")
  .attr("stroke", "rgb(57, 142, 219)")
  .attr("stroke-width", ".5")
  .attr("opacity", ".6");
  

  // Step 6: Initialize tool tip
  // ==============================
  var toolTip = d3.tip()
    .attr("class", "tooltip")
    .offset([80, -60])
    .html(function (d) {
      return (`Trips: ${d.frequency}<br>Bike Time: ${d.bike_duration_mins}<br>Transit Time: ${d.public_duration_mins}<br>Time Saved: ${d.time_saved}`);
    });

  // Step 7: Create tooltip in the chart
  // ==============================
  chartGroup.call(toolTip);
  

  // Step 8: Create event listeners to display and hide the tooltip
  // ==============================
  circlesGroup.on("click", function (data) {
      toolTip.show(data);
    })
    // onmouseout event
    .on("mouseout", function (data, index) {
      toolTip.hide(data);
    });

  // Create axes labels and title
  chartGroup.append("text")
    .attr("transform", "rotate(-90)")
    .attr("y", 0 - margin.left + 40)
    .attr("x", 0 - (height / 2))
    .attr("dy", "1em")
    .attr("class", "axisText")
    .text("Route Frequency (May 2018)");

  chartGroup.append("text")
    .attr("transform", `translate(${width/2}, ${height + margin.top - 15})`)
    .attr("class", "axisText")
    .text("Time Saved (minutes)");

  chartGroup.append("text")
    .attr("transform", `translate(${width/2}, -30)`)
    .attr("class", "titleText")
    .text("Citibikes compared to Public Transportation")
});
