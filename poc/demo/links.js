

/** UTILITY FUNCTIONS
*/
// CLONE
//    Only works for objects with no methods
function clone( obj ) { return JSON.parse( JSON.stringify( obj )); }



/** LINK STORE  
Store compressed and uncompressed versions of all links in current graph

API
  put( s, e, linkarray ); // add uncompressed links for one graph
  get() -> links[] // get all uncompressed links
  get( compList ) -> links[] // get all links compressing those on complist
  get( decompList ) -> links[] // get all links compressed except those on decomplist
 
 STRUCT
 link { "source": "id", "target": "id", "type": "..."}
 
 links[
  { s: "id", e:"id", uncomp: [{link},{link}...] } // link record
   // s = uncomp[0].source, e = uncomp[len-1].target
 ] 
  
*/


function linkStore() {
  this.linkRecords_= [];
  
  // Add ============
  // Add link array from one Cypher graph object
  //
  this.add = function( graphLinks ) {
    var path = compress( graphLinks );
    this.linkRecords_.push( { s:path[0].source, e:path[0].target , links: graphLinks});
    return this;
  }//fn add
  
  // ExpandAll ================
  this.expandAll = function(){
    var collectedLinks = [];
    for( var i in this.linkRecords_ ) {
      collectedLinks.push.apply( collectedLinks, this.linkRecords_[i].links );
    }
    
    return clone( dedupe(collectedLinks));
  }//fn expandAll
  
  // CompressAll ================
  this.compressAll = function(){
    var collectedLinks = [];
    for( var i in this.linkRecords_ ) {
      collectedLinks.push.apply( collectedLinks, compress(this.linkRecords_[i].links) ); 
    }
    return clone( dedupe(collectedLinks));

  }//fn compress all
  
  // CompressSome ===================
  this.compressSome = function( compressList) {
    var compressfn = compress;
    var expandfn = function( links ) { return links; }
    return clone( dedupe( this.linkCollector( compressList,compressfn, expandfn)));
  }//fn

  // ExpandSome =======================
  this.expandSome   = function( expandList) {
    var compressfn = compress;
    var expandfn = function( links ) { return links; }
    return clone( dedupe( this.linkCollector( expandList, expandfn, compressfn )));
  }//fn
  
  // LinkCollector ==========================================
  //    Compress or expand each path in linkrecord based on its presence in the 
  //    input list.
  //    Depending on call, containsFn will be compress or expand and otherwiseFn will be expand or compress
  //     Return an array of the compressed/expanded links
  //
  // 
  this.linkCollector= function ( list, containsFn, otherwiseFn ){
      
      // Does the input list contain the input path record?
      //
      function listContains( list, pathRec){
       
        // Compare one list record to the input path record
        var equalsPathRec = function( arrayRec, index, array ) {
            return arrayRec.start == pathRec.start && arrayRec.end == pathRec.end;
            }//fn
       // Return true if the list contains a record that matches pathRec
       return list.some( equalsPathRec ); 
      }//fn
 
    var collectedLinks = [];
    for( var i = 0; i < this.linkRecords_.length; i++) {
        var pathRecord = { start: this.linkRecords_[i].s, end:this.linkRecords_[i].e };
        var fn = listContains( list, pathRecord ) ? containsFn: otherwiseFn;
        collectedLinks.push.apply( collectedLinks, fn(this.linkRecords_[i].links) );
    }//for
    
    return collectedLinks;
  }//fn
  
}//linkStoreClass

// LINK HANDLING FUNCTIONS ============================


// --------------------------------------
// Build link record store from response object
//
function linkStoreFrom( respObj ) {
  var data = respObj.results[0].data;
  var store = new linkStore();
  
  //store links from each graph
  for( var i = 0, len = data.length; i < len; i++){
    var graphLinks = linksFromGraph( data[i].graph);
    if( graphLinks.length > 0 ){ store.add( graphLinks); }
    }//for
  return store;
}//fn


//------------------------
//  linkArrayFrom
//
function linkArrayFrom( respObj ){
    var data = respObj.results[0].data;
    var completeLinkSet = [];
    
    //for each graph
    for( var i = 0, len = data.length; i < len; i++){
      var graphLinks= linksFromGraph( data[i].graph);
      if( graphLinks.length > 0 ) { completeLinkSet.push.apply( completeLinkSet, graphLinks);}
      }
    return completeLinkSet;
}//fn


// -----------------------------
//  linksFromGraph
//
//  Get the links from one graph object
//  Pre: there is >= 1 link in graph
//  return set of links as {source: id, target: id, type: xxx}
//
function linksFromGraph( graphObj ) {
 var links = graphObj.relationships
 var linkSet = [];
 for( var i = 0, len = links.length; i < len; i++){
    var curlink  = links[i];
    var newlink = {source: curlink.startNode , target: curlink.endNode, type: curlink.type};
    linkSet.push( newlink );
    }//for
  return linkSet;  
}//fn
  


//------------------------
//  CompressedLinkArrayFrom
//
//  for each graph, extract a compressed link
//  return a link set of compressed links
// 
function compressedLinkArrayFrom( respObj ){
    var data = respObj.results[0].data;
    var compressedLinks = [];
    var testcompletelinks = [];
 
    //for each graph
    for( var i = 0, len = data.length; i < len; i++){
      var graphLinks = linksFromGraph( data[i].graph);
      if( graphLinks.length > 0 ) { compressedLinks.push( compress( graphLinks ));}
      }//for
 
     return compressedLinks;
}//fn


//------------------------
// Compress links
//
//    Compress a path made of several links to show just the start and end nodes, with compressed link
//    between them
// Takes:  
//     (a)-[r1]->(b)-[r2]->(c)-[r3]->(d)
// 
//  To:
//     (a)-[compressed]->(d)
// 
// Preconditions: 

//  Linkset contains links from one graph object
//  
/// Returns one link
//     if the graph is only one link long, returns that link
//     if the graph >  1 link, return link with start and end node ids as source and target
//              { source: "a", target: "d", type: "compressed"}
//  

function compress( graphLinks ){
  
  switch( graphLinks.length ) {
    case 0:  alert( "compress(), no links in graph"); 
             return {source: "0", target: "0", type: "bad link"};
    case 1:  return [graphLinks[0]];
    default: return compressMultipleLinks( graphLinks );
  }//sw
  
  function compressMultipleLinks( graphLinks){  
    var sourceNodes = [];
    var targetNodes = [];
  
    for( var i in graphLinks ) {
      sourceNodes.push(graphLinks[i].source);
      targetNodes.push(graphLinks[i].target );
      }
    
    var   pathStartNodes = $(sourceNodes).not(targetNodes).get();
    var pathEndNodes   = $(targetNodes).not(sourceNodes).get();
    //DEBUG compression doesn't work if paths come from initport query. Graph returns two separate paths in one graph object
    //DEBUG if( pathStartNodes.length != 1 ) {alert ("compress(), pathStartNodesArray error, length = " + pathStartNodes.length );}
    //DEBUG if( pathEndNodes.length != 1 )   {alert ("compress(), pathStartNodesArray error, length = " + pathEndNodes.length );}  
  
    return [{source: pathStartNodes[0], target: pathEndNodes[0], type: "compressed"}];
  }//compress multiple links
}//compress  


//--------------------------------------
//    dedupe()
//
//      remove duplicate links
//
//         Remove single hop link if it already exists in the collection
//
//        This can happen because the cypher query returns path graphs which are distguished by start and end node, but several paths may
//        contain the same link.
//


function dedupe( links ) {
  var newLinks = [];
  for( var i = 0, len = links.length; i < len; i++){
    var curLink = links[i];
    // Only add curLink to newLinks if it is not
    // a duplicate of  link later in links
    if( excludes( links.slice(i+1), curLink ))
     { newLinks.push(curLink);}
    }//for
  
  return newLinks;
}//dedupe


//------------------------------
//     excludes()
//
//        True if array does not contain copy of link
//
function excludes( array, link ) {
  for( var i = 0; i < array.length; i++) {
    var cur = array[i];
    if(link.source == cur.source && link.target == cur.target) {return false;}
  }
  return true;
}