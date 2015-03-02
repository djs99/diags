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

var nodeIcons = {};
nodeIcons["initport"] = "icons/Init_port.png";
nodeIcons["volume"] = "icons/Server_and_storage.png";
nodeIcons["host"] = "icons/Server.png";
nodeIcons["array"] = "icons/Storage.png";
nodeIcons["targetport"] = "icons/Target_port.png";
nodeIcons["instance"] = "icons/vm-instance.png";
nodeIcons["zone"] = "icons/Zone.png";
nodeIcons["node"] = "icons/Cloud_system.png";
nodeIcons["nodeElement"] = "icons/Process.png";
nodeIcons["switch"] = "icons/Core_switch.png";
nodeIcons["project"] = "icons/Project.png";


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
linkDistances["OWNS"] = 10;

var defaultLinkStrength = 0.3;
var linkStrengths = {};
linkStrengths["IMPLEMENTS"] = 0.3;
linkStrengths["CONN"] = 0.3;
linkStrengths["MEMBER"] = 0.3;
linkStrengths["OWNS"] = 0.3;


//////////////
// Server Info
//////////////
var serverAddress = "127.0.0.1";
var serverPort = 24680; 
