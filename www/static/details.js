$(document).ready(function() {

  // Highlight the row of the query currently chosen.
  $("#" + query).addClass("selected");

  // Insert the first 16 documents in the table containing the top results.
  var n_max = result_ids.length;
  var n = Math.min(16, n_max);
  append_rows(0, n);

  // Append more rows when scrolled to the bottom.
  $("#topRes tbody").scroll(function() {
    var scroll_top = Math.round($(this).scrollTop());
    var body_height = parseInt($(this).css("height"));
    var scroll_height = $(this).prop("scrollHeight");
    var scroll_perc = Math.round(100 * scroll_top / (scroll_height - body_height));
    if (scroll_perc == 100) {
      var n_new = Math.min(2 * n, n_max);
      append_rows(n, n_new);
      n = n_new;
    }
  });

  function append_rows(k, n) {
    for (i = k; i < n; i++) {
      var id = result_ids[i];
      var row = "<tr title=\"" + descriptions[id - 1] + "\">"
        + "<td>" + (i + 1) + "</td>";
      if (rel_in_res.includes(id)) {
        row += "<td>" + docs[id - 1] + "</td>";
      } else {
        row += "<td style=\"color: red;\">" + docs[id - 1] + "</td>";
      }
      row += "</tr>";
      $("#topRes tbody").append(row);
    }
  }

});
