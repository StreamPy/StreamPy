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
    nodes: [
	{ data: { id: 'print_value_stream', name:'print_value_stream '} },
	{ data: { id: 'multiply_elements', name:'multiply_elements '} },
	{ data: { id: 'generate_stream_of_random_integers', name:'generate_stream_of_random_integers '} }],
edges: [
	{ data: { stream: 'multiply_elements_PORT_product', source: 'multiply_elements', target: 'print_value_stream', name:'multiply_elements_PORT_product:'} },
	{ data: { stream: 'generate_stream_of_random_integers_PORT_out', source: 'generate_stream_of_random_integers', target: 'multiply_elements', name:'generate_stream_of_random_integers_PORT_out:'} }]
    },
  
  layout: {
    name: 'breadthfirst',
    directed: true,
    padding: 20
}
  });
  

var myVar;

var stream_names = ['multiply_elements_PORT_product', 'generate_stream_of_random_integers_PORT_out',];
var edge = ['edge[stream= "multiply_elements_PORT_product"]', 'edge[stream= "generate_stream_of_random_integers_PORT_out"]',];
var value = ['' ,'62' ,'62000.0' ,'' ,'62000.0' ,'83' ,'' ,'83' ,'83000.0' ,'' ,'83000.0' ,'1' ,'' ,'1' ,'1000.0' ,'' ,'1000.0' ,'39' ,'' ,'39' ,'39000.0' ,'' ,'39000.0' ,'35' ,'' ,'35' ,'35000.0' ,'' ,'35000.0' ,'69' ];
 
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