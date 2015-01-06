/////////////////////////////////
// Visual representation of nodes
/////////////////////////////////
var nodeShapes = {};
nodeShapes["circle"] = ["initport", "targetport", "cindervolume", "vvol", "cpg"];
nodeShapes["triangle"] = ["tenant", "process", "cfgfile"];
nodeShapes["square"] = ["host", "switch", "cindernode"];
nodeShapes["rectangle"] = ["array"];
nodeShapes["pentagon"] = ["vm"];
nodeShapes["hexagon"] = ["zone"];


////////////////////////////////////
// Parameters for the force layout
////////////////////////////////////
var svgWidth = 500;  // Horizontal dimension of the canvas.
var svgHeight = 500;  // Vertical dimension of the canvas.
var forceCharge = -800;  // Pushes nodes away from each other.
var forceGravity = 0.1;  // Pulls nodes towards the center of the graph.
var minZoom = -100;
var maxZoom = 100;
var scaleMargin = 0.8;

var defaultLinkDistance = 100;
var linkDistances = {};
linkDistances["IMPLEMENTS"] = 100;
linkDistances["CONN"] = 100;
linkDistances["MEMBER"] = 100;
linkDistances["TN"] = 100;

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
