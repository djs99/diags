//Creates the demo table

function createTable() {
	var data = {"703":{"type":"vm", "name":"Delta", "status":"critical"}, "101":{"type":"array", "name":"Array Orange", "status":"critical"}, "204":{"type":"host", "name":"Host E", "status":"warning"}, "501":{"type":"switch", "name":"Switch B", "status":"warning"}, "5000":{"type":"node", "name":"CinderNode", "status":"warning"}, "1001":{"type":"volume", "name":"volume", "status":"critical"}, "1013":{"type":"volume", "name":"volume", "status":"warning"}}
	var table = "									\
	<br></br>										\
	<table id=alertentrytable>						\
		<tr>										\
			<th>Name</th>							\
			<th>Element Type</th>					\
			<th>Alert Element ID</th>				\
			<th>Status</th>							\
			<th>Alert Text</th>						\
			<th>Select Number of Hops</th>			\
			<th>Direction</th>						\
			<th>Select Node</th>					\
		</tr>										\
		";
		var numOfItems = 0;	//index to dynamically create ids for later use as parameters
		for (var item in data) {
			name = "name";
			type = "type";
			status = "status";
			numOfItems += 1;
			table +=								
			"<tr>									\
				<td>" + data[item][name] + "</td>	\
				<td id='alertelement" + numOfItems + "'>" + data[item][type] + "</td> 	\
				<td id='id" + numOfItems + "'>" + item + "</td> 		\
				<td>" + data[item][status] + "</td>		\
				<td>XYZ went wrong</td>					\
				<td>									\
					<select id='selectspan" + numOfItems + "'>			\
						<option selected='selected'>Any</option> 		\
						<option>1</option>				\
						<option>2</option>				\
						<option>3</option>				\
					</select>							\
				</td>									\
				<td>									\
					<select name='selectdirectionlist' id='selectdirectionlist" + numOfItems + "'>	\
						<option selected='selected'>Down</option>\
						<option>Up</option>				\
						<option>Both</option>			\
					</select>							\
				</td>									\
				<td><button onclick='passSiblingValues(this, " + numOfItems + ")'>Get Graph</button></td>		\
			</tr>";
		}
	return table;
}

function createBestPractices() {
	var data = {"One Init Port Per Zone":"3"}
	var numOfItems = Object.keys(data);
	var table = "																						\
		<table id='bestpracticestable'>																	\
			<tr>																						\
				<th>Best Practice</th>																	\
				<th>Number of Violations</th>															\
				<th>Show Violations</th>																\
			</tr>																						\
		";
	for (var item in data) {
		table +=
			"<tr>																						\
				<td>" + item + "</td>																	\
				<td>" + data[item] + "</td>																\
				<td><button>Get Graph</button></td>														\
			</tr>																						\
			";
	}
	return table;
}

function passSiblingValues(element, index){  //1 based index
	var type 	= document.getElementById("alertelement" + index).innerHTML
	var id 		= document.getElementById("id" + index).innerHTML;
	var hops 	= document.getElementById("selectspan" + index).value;
	var direction = document.getElementById("selectdirectionlist" + index).value;
	getGraph(type, id, hops, direction);
}

$(document).ready(function(){
	$("#alertentry").append(createTable());
	$("#bestpractices").append(createBestPractices());
	$('tr:nth-child(odd)').addClass('alt');
});