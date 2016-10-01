// One line 'hack' to extract parameters from url
var params = _.object(_.compact(_.map(location.search.slice(1).split('&'), function(item) {  if (item) return item.split('='); })));

$('document').ready(function() {
  $.ajaxSetup({ timeout: 10000});
  var stewardTemplate = _.template($("#steward-template").html());
  var submissionTemplate = _.template($("#submission-template").html());

  $("#progressDialog").modal("show");

  if ("submission" in params) {
    $("#progress").html("Finding submission...");
    $.getJSON("/ipfs/" + params.submission, function(submission) {
      $("#progressDialog").modal("hide");
			$("#title").html("Submission");
      $("#submission").html(submissionTemplate({multihash: params.submission,
        fields: submission.fields, files: submission.files}));
    })
    .error(function() { 
      $("#progressDialog").modal("hide");
      $("#submission").html(submissionTemplate({multihash: "Unable to find " + params.submission,
        fields: [], files: []}));
    });
  } else {
    $("#progress").html("Finding steward...");
    $.getJSON("steward" in params ? "/ipns/" + params.steward : "/v0/" , function(steward) {
      $("#progressDialog").modal("hide");
			$("#title").html("Steward");
      $("#steward").html(stewardTemplate({address: params.steward, steward: steward}));
    })
    .error(function() { 
      $("#progressDialog").modal("hide");
      $("#steward").html(stewardTemplate(
        {address: params.steward, steward: {domain: "Unable to resolve " + params.steward, peers: [], submissions: []}}));
    });
  }
});
