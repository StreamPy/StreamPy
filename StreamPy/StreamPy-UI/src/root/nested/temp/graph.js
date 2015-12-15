$(function(){ // on dom ready

$('#cy').cytoscape({
  style: cytoscape.stylesheet()
    .selector('node')
      .css({
        'content': 'data(name)',
        'text-valign': 'center',
        'color': 'black',
        'font-size': '5',
	'shape': 'rectangle',
	'background-color': 'orange',
	'width': 20,
	'height': 20,
	
      })
    .selector('edge')
      .css({
	'content': 'data(name)',
        'target-arrow-shape': 'triangle',
	'font-size': '5'
      })
    .selector(':selected')
      .css({
        'background-color': 'black',
        'line-color': 'black',
        'target-arrow-color': 'black',
        'source-arrow-color': 'black'
      })
    .selector('.faded')
      .css({
        'opacity': 0.25,
        'text-opacity': 0
      }),
  
  elements: {
    nodes: [
	{ data: { id: 'print_stream', name:'print_stream '} },
	{ data: { id: 'print_stream1', name:'print_stream1 '} },
	{ data: { id: 'multiply_elements_in_stream', name:'multiply_elements_in_stream '} },
	{ data: { id: 'generate_stream_of_random_integers', name:'generate_stream_of_random_integers '} }],
edges: [
	{ data: { source: 'multiply_elements_in_stream', target: 'print_stream', name:'stream_name: value'} },
	{ data: { source: 'generate_stream_of_random_integers', target: 'multiply_elements_in_stream', name:'stream_name: value'} },
	{ data: { source: 'generate_stream_of_random_integers', target: 'print_stream1', name:'stream_name: value'} }]
  },
  
  layout: {
    name: 'dagre',
    //name: 'breadthfirst',
    //name: 'preset',
    padding: 10
  },
  
  // on graph initial layout done (could be async depending on layout...)
  ready: function(){
    window.cy = this;
    
    // giddy up...
    
    cy.elements().unselectify();
    
    cy.on('tap', 'node', function(e){
      var node = e.cyTarget; 
      var neighborhood = node.neighborhood().add(node);
      
      cy.elements().addClass('faded');
      neighborhood.removeClass('faded');
    });
    
    cy.on('tap', function(e){
      if( e.cyTarget === cy ){
        cy.elements().removeClass('faded');
      }
    });
  }
});

}); // on dom ready
