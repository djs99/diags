/////////////////////////////////
// Visual representation of nodes
/////////////////////////////////
var nodeShapes = {};
nodeShapes["circle"] = ["initport"];
nodeShapes["triangle"] = ["volume"];
nodeShapes["square"] = ["host"];
nodeShapes["tall"] = ["array"];
nodeShapes["wide"] = ["targetport"];
nodeShapes["pentagon"] = ["instance"];
nodeShapes["hexagon"] = ["zone"];
nodeShapes["rhombus"] = ["node"];
nodeShapes["trapezoid"] = ["nodeElement"];
nodeShapes["parallel"] = ["switch"];
nodeShapes["oval"] = ["project"];


////////////////////////////////////
// Parameters for the force layout
////////////////////////////////////
var svgWidth = 500;  // Horizontal dimension of the canvas.
var svgHeight = 500;  // Vertical dimension of the canvas.

var forceCharge = -8;  // Pushes nodes away from each other.
var forceGravity = 0.1;  // Pulls nodes towards the center of the graph.

var minZoom = 1;
var maxZoom = 30;
var initialScale = 10;

var defaultLinkDistance = 10;
var linkDistances = {};
linkDistances["IMPLEMENTS"] = 10;
linkDistances["CONN"] = 10;
linkDistances["MEMBER"] = 10;
linkDistances["TN"] = 10;

var defaultLinkStrength = 0.3;
var linkStrengths = {};
linkStrengths["IMPLEMENTS"] = 0.3;
linkStrengths["CONN"] = 0.3;
linkStrengths["MEMBER"] = 0.3;
linkStrengths["TN"] = 0.3;


//////////////
// Server Info
//////////////
var serverAddress = "127.0.0.1";
var serverPort = 24680; 
