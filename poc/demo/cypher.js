/** BUILD CYPHER QUERIES FROM FUNCTIONS
  Cypher query = 
    node relation node... where 
*/

/* -----------------------
    NODE CLASS
    
    Converts functional input to Cypher node string
*/
function node() {
  this.typeName_   ="";
  this.separator_  ="";
  this.type_       = "";
  this.properties_ = {};
  this.inResult_   = false;  
  
  this.typeName = function( nameIn ) {
    if( nameIn) {this.typeName_ = nameIn; }
    return this;
  }
  
  this.type = function( typeIn) {
    if( typeIn) {
      this.separator_ = ":";
      this.type_ = typeIn; 
      }
    return this;
  }
  
  this.property = function( name, value ){
    this.properties_[name] = value;
    return this;
  }//fn
  
  this.inResult = function() {this.inResult_ = true; }
  
  this.result = function(){
    if(this.inResult_) {return this.typeName_;}
    else {return undefined;}
  }//fn
    
  this.toString = function(){
      
      function stringFromObject(obj) {
        // Cypher won't accept quotes on the key names, so JSON.stringify doesn't work
        var result = "";
        if( Object.keys(obj).length ) {
          result += "{";
          for( var key in obj ) {
            result += key + ":" + obj[key] + ",";
          }//for
          //remove trailing comma 
          result= result.replace(/,+$/,"");
          result += "}";
        }//if
        return result;
      }//fn
    
    return '(' + this.typeName_ + this.separator_+ this.type_ + stringFromObject(this.properties_) + ')';
  }
     
}//cl

/* -----------------
   RELATION CLASS
   
   Converts functional input to Cypher relation string
*/ 
function relation() {
  this.left_       = "";   //left gives <-[]- relation
  this.name_       = "";
  this.separator_  = "";
  this.type_       = "";
  this.right_      = "";   // right gives -[]-> relation
  this.inResult_   = false;
  this.allSpan_    = false;
  this.minSpan_;  
  this.maxSpan_; //how many relationship hops in the path 
                      // <blank> = 1
                      // *      =   any
                      // *n..m  =   at least n, at most m
                      // *..m   =  <= m
                      // *n..   = >= n

  this.name = function( nameIn ){
    if( nameIn ) { this.name_ = nameIn; }
    return this; 
  }

  this.type = function( typeIn ){
    if( typeIn ) { 
      this.separator_ = ":";
      this.type_ = typeIn; 
      }
    return this; 
  }

  this.direction = function( directionIn ) {
   switch (directionIn ){
    case   "Up": return this.left(); 
    case "Down": return this.right(); 
    case "Both": return this.both();
    default: alert( "missing direction" );
      }
    return this;
    }
    
  this.left   = function() { this.left_ = "<"; return this;}
  this.right  = function() { this.right_ = ">"; return this;}
  this.both   = function() {return this;}
 
  this.inResult = function() {this.inResult_ = true; }
  this.result   = function(){ if(this.inResult_) {return this.name_;} else {return undefined;} }//fn
 
  this.minSpan  = function(minIn) {if( minIn ) {this.minSpan_ = minIn; } return this; }//fn 
  this.maxSpan  = function( maxIn ){ if( maxIn ) {this.maxSpan_ = maxIn; } return this; }//fn
  this.allSpan  = function() { this.allSpan_ = true; return this; }

  this.spanString = function(){
  
   // allSpan  min   max   spanString
   // ----------------------------
   // t         x     x    *
   // f         ""    m    *..m
   // f         n     m    *n..m
   // f         n     ""   *n..
   // f          ""    m    *..m
   // -----------------------------
    var n = this.minSpan_;
    var m = this.maxSpan_;
    if(this.allSpan_ ){return "*";               }
    if( n &&!m       ){return "*"+ n +"..";      }
    if( n && m       ){return "*" + n + ".." + m;}
    if(!n && m       ){return "*" + ".." + m;    }
    if(!n &&!m       ){return "*";               }
  }//fn

  
  
  this.toString = function(){
     return this.left_ + '-[' + this.name_ + this.separator_ + this.type_ + this.spanString() +  ']-' + this.right_;
  }//fn
}//cl

/* -----------------------------
  WHERE CLASS

  !!TODO - not complete or tests !!
  
  Builds WHERE clause of Cypher query

 Usage:
     Create:
        whereClause = new where();
  
    Label filter :
      where.label( "name", "type");
        name: is a node name from the match clause
        example: where.("myhost", "host");
    
    Property filter:
      where.property( name, property, predicate);
      
   var f = new labelFilter( "name");
   var p = new propertyFilter( name, property, predicate);
   var pred = new predicate( LT, 20 );
   
   wh = new where();
      wh.prop( z1, name)
        .equals()
        .prop( z2.name )
        .and()
        .prop( i1, id)
        .notequals()
        .(i2, id);
        
      wh.prop( n, status)
        .equals()
        .val( "failed" );  
 
      wh.prop( n, name)
        .equals()
        .val( "andres")
        .and()
        .type(r)
        .equals()
        .val( "K");
        
      wh label( n, "swedish");  
*/  


function where() {

}//cl


/******************************
  BUILD CYPHER QUERY STRING FROM PATH ARRAY

*/


/* -------------------
   PATH STRING FROM
   
   Build the string for the front section of a cypher query from a path array
*/ 
function pathStringFrom( path ) {
  var pathString = '"MATCH ';
  
  for( n in path ) {
    pathString += path[n].toString();
  }
  return pathString;
}//fn


/* --------------------
   BUILD PATH RESULT
   
    Extract the nodes from the path that have been tagged as "inResult", and put then
    into a result array

    Returns: array of nodes & releations that should be in the result.
*/ 
function buildPathResult( path ) {
  var pathResult = [];
  var r;
  
  for( n in path ){
    r = path[n].result();
    if( r ) { pathResult.push(r);}
  }//for
  return  pathResult;
}//fn


/* -------------------
   PATH RESULT STRING FROM

   Build the string for the result section of a Cypher query from a pathResult array
     
*/ 
function pathResultStringFrom( pathResult) {
  var resultString = "";
 
  if( pathResult.length > 0 ) {
    resultString += ' RETURN ';
    for(n in pathResult ){
      resultString += pathResult[n].toString();
      resultString += ",";
    }//for
    //remove trailing comma 
    resultString = resultString.replace(/,+$/,"");
    // place final quotes
    resultString += '"';
  }//if
  return resultString;
}//fn


/* ------------------------------------
     QUERY STRING FROM
     Build Cypher query string from path string and result string
     
   Query structure:

   '{ "statements" : 
        [   {  "statement" : "MATCH (e:elementType {id:elemenId})-[r*]-(a)
                               RETURN e, r, a",    "resultDataContents": ["graph"]
           }
        ] 
      }'

   Placement of ' and " marks is critical
*/
function queryStringFrom( pathStr, resultStr ) {
  var startStr= '{ "statements" : [ {  "statement" :';
  var endStr =   ',"resultDataContents": ["graph"]}]}'; 
  
  return startStr + pathStr + resultStr + endStr;
}//fn



/***************************
    TEST FUNCTIONS

*/


/* ----------------------
    TEST CYPHER
    
    Build a test Cypher query and display it
*/

function testCypher() {
  //alert( "test cypher" );
  var queryStrs = buildCypher();
  alert( "buildstr= " + queryStrs[0] + " queryStr= " + queryStrs[1]);
}//fn



/* ----------------------
   BUILD CYPHER
   
   Build a test Cypher query

*/

function buildCypher() {

  var path       =  buildNodes();
  var pathResult =  buildPathResult( path );
  var buildStr = pathStringFrom( path ) + pathResultStringFrom( pathResult);
  var queryStr = queryStringFrom(pathStringFrom( path ), pathResultStringFrom( pathResult ));
  return [buildStr, queryStr] ;
}//fn


/* ----------------------
   BUILD NODES
   
   Build a test Cypher relation 

*/

function buildNodes() {
  var host= new node();
  host.name( "21")
       .type( "host")
       .inResult();
  
  var port = new node();
    port.name( "24")
        .type( "initPort" )
        .inResult();
  
   var hba = new relation();
       hba.type("HBA")
          .right()
          .minSpan( 2 );
   
   var path = [];
   path.push( host, hba, port);
   return path;
}//fn







