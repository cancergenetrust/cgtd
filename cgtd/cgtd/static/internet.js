$('document').ready(function() {
  $("#progressDialog").modal("show");
  $("#progress").html("Finding and authenticating stewards...");
  $.getJSON("/v0/stewards", function(stewards) {
  // $.getJSON("/stewards_temp.json", function(stewards) {
    $("#progressDialog").modal("hide");
    if (stewards.length == 0) {
      alert("No stewards found");
    } else {
      var cy = cytoscape({
        container: document.getElementById('cy'),
        style: [
          {
            selector: 'node',
            style: {
              'content': 'data(id)',
              'text-opacity': 0.9,
              'text-valign': 'center',
              'text-halign': 'center',
              'text-wrap': 'wrap',
              'text-transform': 'lowercase',
              'text-margin-y': '8px',
              'background-color': '#11479e',
              'background-opacity': 0.5,
              label: 'data(label)'
            }
          },
          {
            selector: 'edge',
            style: {
              'width': 4,
              'target-arrow-shape': 'triangle',
              'line-color': '#9dbaea',
              'target-arrow-color': '#9dbaea',
              'curve-style': 'bezier'
            }
          }
        ],
      });

      let addresses = _.keys(stewards);
      for (var i=0; i < addresses.length; i++) {
        cy.add({data: {id: addresses[i],
                       label: stewards[addresses[i]].submissions.length + "\n" +
                              stewards[addresses[i]].domain}});
      }

      for (var i=0; i < addresses.length; i++) {
        var peers = stewards[addresses[i]].peers;
        for (var j=0; j < peers.length; j++) {
          cy.add({data: {id: 'edge' + i + j, source: addresses[i], target: peers[j]}});
        }
      }

      cy.layout({
        name: 'dagre'
      });

      cy.on('tap', 'node', function(event) {
        window.open("steward.html?address="+this.data("id"));
      });
    }
  });
});
