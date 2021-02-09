$(document).ready(function() {

  $("#topResHead").click(function() {
    $("#topRes").slideToggle();
  });

  $("#inListHead").click(function() {
    $("#inList").slideToggle();
  });

  $("#notInListHead").click(function() {
    $("#notInList").slideToggle();
  });

  $(".clickable-row").click(function() {
    window.location = $(this).data("href");
  })

});
