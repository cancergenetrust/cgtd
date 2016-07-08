$(document).ready(function() {
  var droppedFiles = [];

  $("#dropbox").on('drag dragstart dragend dragover dragenter dragleave drop', function(e) {
    e.preventDefault();
    e.stopPropagation();
  })
  .on('dragover dragenter', function() {
    $(this).addClass("active");
  })
  .on('dragleave dragend drop', function() {
    $(this).removeClass("active");
  })
  .on('drop', function(e) {
    droppedFiles = e.originalEvent.dataTransfer.files;
    $("#file-count").html(droppedFiles.length + " files ready for upload");
  });


  $("#upload-button").on("click", function(e) {
    e.preventDefault();

    var formData = new FormData(document.querySelector("#upload-form"));

    for (var i = 0; i < droppedFiles.length; i++) {
      formData.append("files[]", droppedFiles[i]);
    }

    $.ajax({
      url: "/v0/submissions",
      data: formData,
      type: "POST",
      contentType: false,
      processData: false,
      beforeSend: function() {
        $("#progressDialog").modal("show");
        $("#progress").html("Sending and signing submission with steward's private key...");
      },
      success: function(data) {
        $("#progressDialog").modal("hide");
        if (data.status === "error") {
          window.alert(data.msg);
          return;
        } else {
          window.location.href = "/submission.html?multihash=" + data.multihash;
        }
      },
      error: function(request, status, error) {
        $("#progressDialog").modal("hide");
        alert(request.responseJSON.message);
      }
    })
  });
});
