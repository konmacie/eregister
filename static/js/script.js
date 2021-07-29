$(document).ready(function () {
  $(".add-prev").each(function () {
    var href = $(this).attr("href");
    var prev = encodeURIComponent(
      window.location.pathname + window.location.search
    );

    href += "?prev=" + prev;
    $(this).attr("href", href);
  });
});
