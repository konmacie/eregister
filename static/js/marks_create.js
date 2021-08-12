let markCreateModal = new bootstrap.Modal($("#markCreateModal"));
let markCreateForm = $("#mark-create > form");

// listen for click event on link for creating mark
$(".mark-add-link").click(function () {
  let id_parts = $(this).attr("id").split("-");
  let pk = $(id_parts).get(-1);
  $("#id_create-student").val(pk);
  markCreateModal.show();
});

function addMark(response) {
  let mark = $("#mark-empty").clone(1).removeClass("visually-hidden");
  mark.attr("id", "mark-" + response.pk);
  mark.find(".symbol-placeholder").replaceWith(response.symbol);
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
