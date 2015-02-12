//Creates the demo table

function createTable() {
	var data = {"703":"vm", "102":"array", "204":"host", "501":"switch", "5000":"node", "1001":"volume", "1013":"volume"}
	var table = "									\
	<br></br>										\
	<table id=alertentrytable>						\
		<tr>										\
			<th>Alert Element</th>					\
			<th>Alert Element ID</th>				\
			<th>Alert Text</th>						\
			<th>Select Number of Hops</th>			\
			<th>Direction</th>						\
			<th>Select Node</th>					\
		</tr>										\
		";
		var numOfItems = 0;	//index to dynamically create ids for later use as parameters
		for (var item in data) {
			numOfItems += 1;
			table +=								
			"<tr>									\
				<td id='alertelement" + numOfItems + "'>" + data[item] + "</td> 	\
				<td id='id" + numOfItems + "'>" + item + "</td> 		\
				<td>XYZ went wrong</td>										\
				<td>									\
					<select id='selectspan" + numOfItems + "'>			\
						<option selected='selected'>Any</option> \
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

function passSiblingValues(element, index){  //1 based index
	var type 	= document.getElementById("alertelement" + index).innerHTML
	var id 		= document.getElementById("id" + index).innerHTML;
	var hops 	= document.getElementById("selectspan" + index).value;
	var direction = document.getElementById("selectdirectionlist" + index).value;
	getGraph(type, id, hops, direction);
}

$(document).ready(function(){
	$("#alertentry").append(createTable());
	$('tr:nth-child(odd)').addClass('alt');
});