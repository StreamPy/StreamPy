$(function(){ // on dom ready

var cy = cytoscape({
  container: document.getElementById('cy'),

  style: cytoscape.stylesheet()
    .selector('node')
      .css({
        'content': 'data(name)',
        'text-valign': 'bottom',
        'color': 'black',
        'font-size': '15',
    'shape': 'rectangle',
    'background-color': 'orange',
    'width': 30,
    'height': 30,
    
      })
    .selector('edge')
      .css({
    'content': 'data(val)',
    'target-arrow-shape': 'triangle',
        'width': '10',
    'font-size': '12',
    'target-arrow-color': '#D3D3D3',
    'line-color': '#D3D3D3'
      })
    .selector(':selected')
      .css({
        'background-color': 'orange',
        'line-color': '#D3D3D3',
        'target-arrow-color': '#D3D3D3',
        'source-arrow-color': '#D3D3D3',
        'content': 'data(name)'
      })
    
    .selector('.faded')
      .css({
        'opacity': 0.25,
        'text-opacity': 0
      }),
  
  elements: {
    ELEMENTS
    },
  
  layout: {
    name: 'breadthfirst',
    directed: true,
    padding: 20
}
  });
  

var myVar;

SEQUENCE
 
var n = 0;
function myFunction() {
   myVar = setTimeout(myFunction, 200);
   var edge_index = n % edge.length;
   var sname = stream_names[edge_index];
   //var sname = cy.elements(edge[edge_index]).data('stream');
   //cy.elements(edge[n]).data('name', sname + ': ' + value[n]);
   cy.elements(edge[edge_index]).data('name', sname + ': ' + value[n]);
   cy.elements(edge[edge_index]).data('val', value[n]);
   //setTimeout(function(){
   //     cy.elements(edge[edge_index]).data('name', sname);
   //     cy.elements(edge[edge_index]).data('val', '');
   //     }, 500);
   if (n < value.length - 1){
       n = n + 1;
   } else{
       cy.elements(edge[edge_index]).data('name', sname );
       cy.elements(edge[edge_index]).data('val', '');
   }
}

var i = 0;
function myFunction2() {
   myVar = setTimeout(myFunction2, 1000);
   var seq_keys = Object.keys(seq);
   for (var stream in seq_keys){
      window.alert(stream);
      var val = seq[stream][i];
      
      window.alert(val);
      //var sname = cy.elements(edge[edge_index]).data('stream');
      cy.elements(edge['source =' + stream]).data('name', stream + ': ' + val);
      setTimeout(function(){cy.elements(edge['source =' + stream]).data('name', stream + ': ');}, 500);
   
   if (i < seq_keys[0].length - 1){
       i = i + 1;
    }
   }
}

myFunction();
    
}); // on dom ready