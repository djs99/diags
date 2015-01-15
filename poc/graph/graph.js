// Containers for the nodes and links to come.
var nodes = [],
    links = [];

// Define the force layout.
var force = d3.layout.force()
    .nodes(nodes)                           
    .links(links)                          
    .charge(forceCharge)
    .gravity(forceGravity)
    .linkDistance(function(link) { return setLinkDistance(link); })
    .linkStrength(function(link) { return setLinkStrength(link); })
    .size([svgWidth, svgHeight])
    .on("tick", tick);                    


//
// Custom link settings by type.
//
function setLinkDistance(link) {
    var distance = linkDistances["link.type"];
    if (distance == undefined) {
        return defaultLinkDistance;
    }
    return distance;
}

function setLinkStrength(link) {
    var strength = linkStrengths["link.type"];
    if (strength == undefined) {
        return defaultLinkStrength;
    }
    return strength;
}


// Enable the zoom behavior.
var zoomer = d3.behavior.zoom()
               .scaleExtent([minZoom, maxZoom])
               .on("zoom", doZoom);


// Create the SVG
var svg = d3.select("body").append("svg")
    .attr("width", svgWidth)               
    .attr("height", svgHeight)           
    .attr("class", "graph-svg-component")
    .append("g")
    .call(zoomer)
    .append("g");

svg.append("rect")
    .attr("class", "overlay")
    .attr("width", svgWidth)
    .attr("height", svgHeight);


function doZoom() {
    svg.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
}


// Define the arrow heads for paths.
svg.append("defs").append("svg:marker")
    .attr("id", "arrowhead")
    .attr("viewBox", "0 -5 10 10")
    .attr("refX", 17) 
    .attr("refY", 0)
    .attr("markerWidth", 10)
    .attr("markerHeight", 10)
    .attr("orient", "auto")
    .append("path")
        .attr("d", "M 0,-2 L 4,0 L 0,2"); 


//
// Returns an array of all nodes which are represented 
// by the specified shape in the graph.
//
function getNodesOfShape(nodes, shape) {
    var outputArray = [];
    nodes.forEach( function(node) {
        if (nodeShapes[shape].indexOf(node.type) != -1 ) {
            outputArray.push(node);
        };
    } );
    return outputArray;
}


//
// Return a list of nodes in the critical state.
//
function getNodesByStatus(nodes, status) {
    var outputArray = [];
    nodes.forEach( function(node) {
        if (node.status == status) {
            outputArray.push(node);
        };
    } );
    return outputArray;
}


//
// Return a list of highlighted nodes.
//
function getHighlightedNodes(nodes) {
    var outputArray = [];
    nodes.forEach( function(node) {
        if (node.highlight == "true") {
            outputArray.push(node);
        };
    } );
    return outputArray;
}


// Shortcut selections for graph entities.
var circle = svg.selectAll(".circle");    
var square = svg.selectAll(".rect");   
var rectangle = svg.selectAll(".rect");   
var triangle = svg.selectAll(".polygon");   
var pentagon = svg.selectAll(".polygon");   
var hexagon = svg.selectAll(".polygon");   
var text = svg.selectAll(".text");   
var warn = svg.selectAll(".warn");   
var warnLabel = svg.selectAll(".warnLabel");   
var crit = svg.selectAll(".crit");   
var link = svg.selectAll(".link");   
var highlight = svg.selectAll(".highlight");   
var bracket = svg.selectAll(".bracket");   

var linkTypes = [];

//
// Start or re-start the force layout.
//
function start() {                                                                               
    // Highlight backgrounds
    highlight.remove();
    highlight = svg.selectAll(".highlight");
    highlight = highlight.data( getHighlightedNodes(force.nodes() ) )
        .enter().append("rect")
        .attr("height", 52)
        .attr("width", 52)
        .attr("x", -26)
        .attr("y", -26)
        .attr("class", "highlight");

    // Highlight brackets
    bracket.remove();
    bracket = svg.selectAll(".bracket");
    bracket = bracket.data( getHighlightedNodes(force.nodes() ) )
        .enter().append("path")
        .attr("d", "M -26,-15 L -26,-26 L -15,-26 \
                    M 15,-26 L 26,-26 L 26,-15 \
                    M 26,15 L 26,26 L 15,26 \
                    M -15,26 L -26,26 L -26,15")
        .attr("class", "bracket");

    // Links
    link.remove();
    link = svg.selectAll(".link");
    link = link.data(force.links(), function(d) { return d.source.id + "-" + d.target.id; });
    link.enter().append("g")
    link.append("line")
        .attr("class", function(d) { return "link " + d.type; })
        .on("mouseover", function(d) { return linkToolTipIn(d); } ) 
        .on("mouseout", function(d) { return toolTipOut(d); } )
        .on("click", function(d) { return selectLink(d); } )
        .attr("marker-end", "url(#arrowhead)")
    link.append("text")
        .attr("class", "linktext")
        .attr("text-anchor", "middle")
        .attr("x", function(d) { return d.source.x; } )
        .attr("y", function(d) { return d.source.y; } )
        .text( function(d) { return d.type; } );
    link.exit().remove();

    // Circles
    circle.remove();
    circle = svg.selectAll(".circle");
    circle = circle.data(getNodesOfShape(force.nodes(), "circle"), function(d) { return d.id; });
    circle.enter().append("g")
        .append("circle")
        .attr("class", function(d) { return "node " + d.type; })
        .attr("r", 20)
        .on("mouseover", function(d) { return nodeToolTipIn(d); } ) 
        .on("mouseout", function(d) { return toolTipOut(d); } )
        .on("click", function(d) { return selectNode(d); } )
        .call(force.drag);
    circle.append("text")
        .attr("text-anchor", "middle")
        .attr("fill", "#000000")
        .attr("y", ".31em")
        .text(function(d) {return d.name;});
    circle.exit().remove();

    // Squares
    square.remove();
    square = svg.selectAll(".square");
    square = square.data(getNodesOfShape(force.nodes(), "square"), function(d) { return d.id; } );
    square.enter().append("g")
        .append("rect")
        .attr("class", function(d) { return "node " + d.type; } )
        .attr("height", 32)
        .attr("width", 32)
        .attr("x", -16)
        .attr("y", -16)
        .on("mouseover", function(d) { return nodeToolTipIn(d); } ) 
        .on("mouseout", function(d) { return toolTipOut(d); } )
        .on("click", function(d) { return selectNode(d); } )
        .call(force.drag);
    square.append("text")
        .attr("text-anchor", "middle")
        .attr("fill", "#000000")
        .attr("y", ".31em")
        .text(function(d) {return d.name;});
    square.exit().remove();

    // Rectangles
    rectangle.remove();
    rectangle = svg.selectAll(".rect");
    rectangle = rectangle.data( getNodesOfShape(force.nodes(), "rectangle"), function(d) { return d.id; } );
    rectangle.enter().append("g").append("rect")
        .attr("class", function(d) { return ( "node " + d.type ); } )
        .attr("height", 44)
        .attr("width", 30)
        .attr("x", -15)
        .attr("y", -22)
        .on("mouseover", function(d) { return nodeToolTipIn(d); } ) 
        .on("mouseout", function(d) { return toolTipOut(d); } )
        .on("click", function(d) { return selectNode(d); } )
        .call(force.drag);
    rectangle.append("text")
        .attr("text-anchor", "middle")
        .attr("fill", "#000000")
        .attr("y", ".31em")
        .text(function(d) {return d.name;});
    rectangle.exit().remove();

    // Triangles
    triangle.remove();
    triangle = svg.selectAll(".polygon");
    triangle = triangle.data( getNodesOfShape(force.nodes(), "triangle"), function(d) { return d.id; } );
    triangle.enter().append("g").append("polygon")
        .attr("class", function(d) { return ( "node " + d.type ); } )
        .attr("points", "0,-20 -18,10 18,10")
        .on("mouseover", function(d) { return nodeToolTipIn(d); } ) 
        .on("mouseout", function(d) { return toolTipOut(d); } )
        .on("click", function(d) { return selectNode(d); } )
        .call(force.drag);
    triangle.append("text")
        .attr("text-anchor", "middle")
        .attr("fill", "#000000")
        .attr("y", ".31em")
        .text(function(d) {return d.name;});
    triangle.exit().remove();

    // Pentagons
    pentagon.remove();
    pentagon = svg.selectAll(".polygon");
    pentagon = pentagon.data( getNodesOfShape(force.nodes(), "pentagon"), function(d) { return d.id; } )
    pentagon.enter().append("g").append("polygon")
        .attr("class", function(d) { return ( "node " + d.type ); } )
        .attr("points", "0,-20 -20,-6 -12,16 12,16 20,-6")
        .on("mouseover", function(d) { return nodeToolTipIn(d); } ) 
        .on("mouseout", function(d) { return toolTipOut(d); } )
        .on("click", function(d) { return selectNode(d); } )
        .call(force.drag);
    pentagon.append("text")
        .attr("text-anchor", "middle")
        .attr("fill", "#000000")
        .attr("y", ".31em")
        .text(function(d) {return d.name;});
    pentagon.exit().remove();

    // Hexagons
    hexagon.remove();
    hexagon = svg.selectAll(".polygon");
    hexagon = hexagon.data( getNodesOfShape(force.nodes(), "hexagon"), function(d) { return d.id; } )
    hexagon.enter().append("g").append("polygon")
        .attr("class", function(d) { return ( "node " + d.type ); } )
        .attr("points", "12,-20 -12,-20 -24,0 -12,20 12,20 24,0")
        .on("mouseover", function(d) { return nodeToolTipIn(d); } ) 
        .on("mouseout", function(d) { return toolTipOut(d); } )
        .on("click", function(d) { return selectNode(d); } )
        .call(force.drag);
    hexagon.append("text")
        .attr("text-anchor", "middle")
        .attr("fill", "#000000")
        .attr("y", ".31em")
        .text(function(d) {return d.name;});
    hexagon.exit().remove();

    // Warning icons
    warn.remove();
    warn = svg.selectAll(".warn");
    warn = warn.data( getNodesByStatus(force.nodes(), "warning") )
        .enter().append("polygon")
        .attr("class", "warning")
        .attr("points", "-20,10 -29,25 -11,25");
    
    // Putting an "!" on the Warning icons
    warnLabel.remove();
    warnLabel = svg.selectAll(".warnLabel");
    warnLabel = warnLabel.data( getNodesByStatus(force.nodes(), "warning") )
        .enter().append("text")
        .attr("class", "warnLabel")
        .attr("x", -24)
        .attr("y", 23)
        .text("!");

    // Crit icons
    crit.remove();
    crit = svg.selectAll(".crit");
    crit = crit.data( getNodesByStatus(force.nodes(), "critical") )
        .enter().append("polygon")
        .attr("class", "critical")
        .attr("points", "   -23,7 -21,7 -15,13  -9,7 -7,7 -7,9 -13,15 -7,21 -7,23 -9,23 -15,17 -21,23 -23,23 -23,21 -17,15 -23,9");


    force.start();
}


//
// Run a cycle of the force layout's positioning algorithm.
//
function tick() {
    circle.attr("transform", transform);
    square.attr("transform", transform);
    rectangle.attr("transform", transform);
    triangle.attr("transform", transform);  
    pentagon.attr("transform", transform);  
    hexagon.attr("transform", transform);  

    warn.attr("transform", transform);  
    warnLabel.attr("transform", transform);  
    crit.attr("transform", transform);  

    highlight.attr("transform", transform);  
    bracket.attr("transform", transform);  

    link.select("line").attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });

    link.select(".linktext")
        .attr("x", function(d) { return getLinkTextX(d.source, d.target); } )
        .attr("y", function(d) { return getLinkTextY(d.source, d.target); } )
        .attr("transform", function(d) { return getLinkTextR(d.source, d.target); } )
}

// Re-position the nodes on the canvas.
function transform(d) {
  return "translate(" + d.x + "," + d.y + ")";  // "translate" does the work, it seems.
}


//
// Position and rotate link text.
//
function getLinkTextX (source, target) {
    var cx = (source.x + target.x) / 2;
    return cx;
}

function getLinkTextY (source, target) {
    var cy = (source.y + target.y) / 2;
    return cy;
}

function getLinkTextR (source, target) {
    var cx = (source.x + target.x) / 2;
    var cy = (source.y + target.y) / 2;
    var dx = source.x - target.x;
    var dy = source.y - target.y;
    var angleRads = 0;
    var angleDegs = 0;
    if (dx == 0) {
        if (dy > 0) angleDegs = 90;
        else angleDegs = 270;
    }
    else
    {
        var tanAngle = dy / dx;
        angleRads = Math.atan(tanAngle);
        angleDegs = angleRads * (180 / Math.PI);
    }

    return "rotate("+angleDegs+" "+cx+","+cy+")";
}


//
// Update the local model with new data from the server.
//
function loadGraphData(data) {
    var newNodes = data["nodes"];
    var newLinks = data["links"];

    nodes.length = 0;
    links.length = 0;

    // Build an association array for quicker lookups...
    var nodeLookup = {};
    newNodes.forEach( function(node) {
        nodeLookup[node.id] = node;

        // Set default name, if required.
        if (node.name == undefined) {
            node.name = node.type;
        };

        // Set default status, if required.
        if (node.status == undefined) {
            node.status = "normal";
        };

        nodes.push(node);
        console.log("NODE: type=" + node.type + " name=" + node.name + "  id=" + node.id + "  status=" + node.status);
    } );


    // Connect nodes to edges...
    newLinks.forEach( function(link) {
        link.source = nodeLookup[link.source];
        link.target = nodeLookup[link.target];
        link.status = link.target.status;
 
        // Track the different types of link status.
        if (linkTypes.indexOf(link.status) == -1) {
            linkTypes.push(link.status);
        };

        links.push(link);
        console.log("LINK: type=" + link.type + " source=" + link.source.id + "  target=" + link.target.id + "  status=" + link.status);
    } );

    start();
}


//
// Tooltips . . .
//
var div = d3.select("body").append("div")
    .attr("class", "tooltip")
    .style("opacity", 0);

function nodeToolTipIn(d) {
    div.transition()
        .duration(200)
        .style("opacity", .9);
        div.html("<b>Name:</b> " + d.name + 
                 "<br> <b>Type:</b> " + d.type + 
                 "<br> <b>Status:</b> " + d.status)
        .style("left", (d3.event.pageX + 10) + "px")
        .style("top", (d3.event.pageY + 10) + "px");
}

function linkToolTipIn(d) {
    div.transition()
        .duration(200)
        .style("opacity", .9);
        div.html("<b>Source:</b> " + d.source.name + 
                 "<br> <b>Target:</b> " + d.target.name + 
                 "<br> <b>Type:</b> " + d.type)
        .style("left", (d3.event.pageX + 10) + "px")
        .style("top", (d3.event.pageY + 10) + "px");
}

function toolTipOut(d) {
    div.transition()
        .duration(500)
        .style("opacity", 0);
}


//
// Controls . . .
//
var selectedNode = null;
var selectedLink = null;

function selectNode(d) {
    selectedNode = d;
    selectedLink = null;
    showDetails();
}

function selectLink(d) {
    selectedNode = null;
    selectedLink = d;
    showDetails();
}



var graphScale = 1;


function showDetails() {
    var popup = document.getElementById("details");

    var details;

    if (selectedNode != null) {
        details = getNodeDetails();
    }
    else if (selectedLink != null){
        details = getLinkDetails();
    }
    else {
        details = "No element selected!";
    }

    var contentpane = document.getElementById("detailscontent");
    contentpane.innerHTML = details;
    popup.style.visibility = "visible";
}


function hideDetails() {
    var popup = document.getElementById("details");
    popup.style.visibility = "hidden";
}


function getNodeDetails() {
    var details = ""; 

    details += "<b>Node Details . . .</b><hr>";
    details += "<li><b>Name:</b> " + selectedNode.name + "</li>";
    details += "<li><b>Type:</b> " + selectedNode.type + "</li>";
    details += "<li><b>State:</b> " + selectedNode.status + "</li>";
    details += "<li><a href='http://www.hp.com/' target='mgrWindow'>Element Manager</a></li>";

    var links = getNodeLinks(selectedNode);
    if (links["incoming"].length != 0)
    {
        details += "<li><b>Incoming Links:</b><ul>";
        for (idx = 0; idx < links["incoming"].length; idx++) {
            var thisLink = links["incoming"][idx];
            details += "<li>" + thisLink.source.name + "</li>";
        }
        details += "</ul></li>";
    }

    if (links["outgoing"].length != 0)
    {
        details += "<li><b>Outgoing Links:</b><ul>";
        for (idx = 0; idx < links["outgoing"].length; idx++) {
            var thisLink = links["outgoing"][idx];
            details += "<li>" + thisLink.target.name + "</li>";
        }
        details += "</ul></li>";
    }

    return details;
}


function getNodeLinks(node) {
    var links = force.links();

    var incoming = [];
    var outgoing = [];

    for (idx = 0; idx < links.length; idx++)
    {
        var link = links[idx];
        if (link.source.name == node.name) {
            outgoing.push(link);
        }
        else if (link.target.name == node.name) {
            incoming.push(link);
        }
    }

    var result = {};
    result["incoming"] = incoming;
    result["outgoing"] = outgoing;

    return result;
}


function getLinkDetails() {
    var details = ""; 

    details += "<b>Link Details . . .</b><hr>";
    details += "<li><b>Source:</b> " + selectedLink.source.name + "</li>";
    details += "<li><b>Relationship:</b> " + selectedLink.type + "</li>";
    details += "<li><b>Target:</b> " + selectedLink.target.name + "</li>";
    details += "<li><a href='http://www.hp.com/' target='mgrWindow'>Element Manager</a></li>";

    return details;
}



//
// Graph API calls, to be called from the host page.
//

var highlightEnabled = true;
function toggleHighLight() {
    if (highlightEnabled == true) {
        highlightEnabled = false;
	highlight.attr("visibility", "hidden");
        bracket.attr("visibility", "hidden");
    }
    else {
        highlightEnabled = true;
	highlight.attr("visibility", "visible");
        bracket.attr("visibility", "visible");
    }
}




/*
function zoomToFit() {
    var minX = 10000, maxX = 0, minY = 10000, maxY = 0;
    var nodes = force.nodes();
    for (idx = 0; idx < nodes.length; idx++) {
        var node = nodes[idx];
        if (node.x < minX) { minX = node.x; }
        if (node.y < minY) { minY = node.y; }
        if (node.x > maxX) { maxX = node.x; }
        if (node.y > maxY) { maxY = node.y; }
    }
    var sizeX = maxX - minX;
    var sizeY = maxY - minY;

    var scaleX = svgWidth / sizeX;
    var scaleY = svgHeight / sizeY;

    graphScale = scaleMargin * Math.max(scaleX, scaleY);

    svg.attr("transform", "scale(" + graphScale +  ")");
}
*/
