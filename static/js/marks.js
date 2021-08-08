let markModal = new bootstrap.Modal($("#markModal"));
let markUpdateModal = new bootstrap.Modal($("#markUpdateModal"));
let markCreateModal = new bootstrap.Modal($("#markCreateModal"));
let markCreateForm = $("#mark-create > form");

function changeMark(response) {
  // if mark was changed, update displayed value
  let selector = "#mark-" + response.pk;
  $(selector).html(response.symbol);
  markUpdateModal.hide();
}

// handle errors for MarkChangeForm
function handleChangeErrors(response) {
  let errors = $.parseJSON(response.responseJSON.errors);
  // for every error, find related input and error message under it
  $.each(errors, function (key, val) {
    let field = $("#id_change-" + key);
    let message = val[0].message;
    console.log(val);
    let container = $('<div class="alert alert-danger mt-2"></div>');
    container.html(message);
    container.insertAfter(field);
  });
  // activate Save button (dissabled for duration of AJAX request)
  $("#change-mark-button").prop("disabled", false);
}

// parse data returned by MarkDetailView and add it to respective modal
function parseMarkData(response) {
  $("#mark-spinner").hide();
  let data = $(response);
  $("#mark-details").html(data.find("#response-mark-details"));
  $("#mark-history").html(data.find("#response-mark-history"));
  $("#mark-change").html(data.find("#response-mark-change"));

  $("#response-mark-change > form").submit(function () {
    $("#change-mark-button").prop("disabled", true);
    $(".alert-danger").remove();
    // create an AJAX call
    $.ajax({
      data: $(this).serialize(), // get the form data
      type: $(this).attr("method"),
      url: $(this).attr("action"),
      success: changeMark,
      error: handleChangeErrors,
    });
    return false;
  });
}

// listen for mark click event
$(".mark-link").click(function () {
  // clear modal
  $("#mark-details").html("");
  // get Mark instance pk
  let id_parts = $(this).attr("id").split("-");
  let pk = $(id_parts).get(-1);
  // show modal and spinner for the duration of AJAX request
  $("#mark-spinner").show();
  markModal.show();
  // create an AJAX call
  $.ajax({
    data: { pk: pk },
    type: "GET",
    url: $(this).attr("href"),
    success: parseMarkData,
    error: function (response) {
      alert(response.responseJSON.error_msg);
      markModal.hide();
    },
  });
  return false;
});

// listen for click event on link for creating mark
$(".mark-add-link").click(function () {
  let id_parts = $(this).attr("id").split("-");
  let pk = $(id_parts).get(-1);
  $("#id_create-student").val(pk);
  markCreateModal.show();
});

function addMark(response) {
  let mark = $(
    '<a href="#" class="mark-link btn btn-primary btn-sm py-1 my-1"></a>'
  );
  mark.attr("id", "mark-" + response.pk);
  mark.html(response.symbol);
  mark.insertBefore($("#student-" + response.student));
  markCreateModal.hide();
  markCreateForm[0].reset();
}

function handleAddErrors(response) {
  let errors = $.parseJSON(response.responseJSON.errors);
  $.each(errors, function (key, val) {
    let field = $("#id_create-" + key);
    let message = val[0].message;
    console.log(val);
    let container = $('<div class="alert alert-danger mt-2"></div>');
    container.html(message);
    container.insertAfter(field);
  });
  $("#change-mark-button").prop("disabled", false);
}

markCreateForm.submit(function () {
  $("#create-mark-button").prop("disabled", true);
  // remove alerts from previos request
  $(".alert-danger").remove();
  // create an AJAX call
  $.ajax({
    data: $(this).serialize(), // get the form data
    type: $(this).attr("method"),
    url: $(this).attr("action"),
    success: addMark,
    error: handleAddErrors,
  });
  $("#create-mark-button").prop("disabled", false);
  return false;
});
