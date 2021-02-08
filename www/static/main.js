$(document).ready(function() {

  $("#topResHeader").on("click", function() {
    $("#topRes").slideToggle();
  });

  $("#inListHeader").on("click", function() {
    $("#inList").slideToggle();
  });

  $("#notInListHeader").on("click", function() {
    $("#notInList").slideToggle();
  });

});
