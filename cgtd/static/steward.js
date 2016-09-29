var params = _.object(_.compact(_.map(location.search.slice(1).split('&'), function(item) {  if (item) return item.split('='); })));

$('document').ready(function() {
  var stewardTemplate = _.template($("#steward-template").html());
  var submissionTemplate = _.template($("#submission-template").html());

  $("#progressDialog").modal("show");

  if ("submission" in params) {
    $("#progress").html("Getting submission...");
    $.getJSON("/ipfs/" + params.submission, function(submission) {
      $("#progressDialog").modal("hide");
      $("#submission").html(submissionTemplate({fields: submission.fields, files: submission.files}));
    })
    .error(function() { 
      $("#progressDialog").modal("hide");
      $("#submission").html("Submission " + params.submission + " Unreachable");
    });
  } else {
    $("#progress").html("Finding steward and getting latest index...");
    $.getJSON("steward" in params ? "/ipns/" + params.steward : "/v0/" , function(steward) {
      $("#progressDialog").modal("hide");
      $("#steward").html(stewardTemplate({steward: steward}));
    })
    .error(function() { 
      $("#progressDialog").modal("hide");
      $("#steward").html("Steward " + params.steward + " Unreachable");
    });
  }
});
