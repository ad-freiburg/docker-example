$(document).ready(function() {

  $("#topResHeader").click(function() {
    $("#topRes").slideToggle();
  });

  $("#inListHeader").click(function() {
    $("#inList").slideToggle();
  });

  $("#notInListHeader").click(function() {
    $("#notInList").slideToggle();
  });

  $(".clickable-row").click(function() {
    window.location = $(this).data("href");
  })

  $("#" + query).addClass("selected");

});
