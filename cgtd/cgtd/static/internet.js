$('document').ready(function() {
  $("#progressDialog").modal("show");
  $("#progress").html("Finding and authenticating stewards...");
  // $.getJSON("/v0/stewards", function(stewards) {
  $.getJSON("/stewards_temp.json", function(stewards) {
    $("#progressDialog").modal("hide");
    if (stewards.length == 0) {
      alert("No stewards found");
    } else {
			var cy = cytoscape({
				container: document.getElementById('cy'),
				style: [{
					selector: 'node',
					style: {
						shape: 'hexagon',
						'background-color': 'red',
						label: 'data(label)'
					}
				}],
			});

      let addresses = _.keys(stewards);
      for (var i=0; i < addresses.length; i++) {
				cy.add({data: {id: addresses[i], label: stewards[addresses[i]].domain}});
      }

      for (var i=0; i < addresses.length; i++) {
        var peers = stewards[addresses[i]].peers;
        for (var j=0; j < peers.length; j++) {
					cy.add({data: {id: 'edge' + i + j, source: addresses[i], target: peers[j]}});
        }
      }
			cy.layout({
					name: 'grid'
			});
    }
  });
});
