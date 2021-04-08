var movies = [];
var groundTruth = {};
var evaluation = [];
var precisionsAt3 = [];
var precisionsAtR = [];
var averagePrecisions = [];

var docsPromise;
var overviewTablePromise;

$(document).ready(function() {

  $("div#detailsbox").hide();
  $("div#resultsbox").hide();

  // Click on README link should open dialog box which renders MD as HTML.
  $("a.readme").click(function(e) {
    // Prevent that the link is opened as it normally would in a browser.
    e.preventDefault();
    // The time is added to prevent caching.
    $.get($(this).attr("href") + "?_=" + new Date().getTime(), function(markdown) {
      var md2html = new showdown.Converter();
      md2html.setFlavor("github");
      console.log(showdown.getDefaultOptions());
      $("div.readme").html(md2html.makeHtml(markdown));
      $("div.readme a").attr("target", "_blank");
      $("div.readme").dialog({ width: 1000, height: "auto" });
    });
  });

  docsPromise = readDocs();
  // Just for testing purposes. This should be removed at some point.
  docsPromise.then(function() {
    console.log("Finished reading docs.");
  });

  // As soon as benchmark is ready, for each mode, compute the measures P@3, P@R and AP for each query and the mean.
  overviewTablePromise = readBenchmark().then(function() {
    console.log("Finished reading benchmark.");
    return new Promise(function(resolve, reject) {
      fillOutPrecisions();
      appendRowsToOverviewTable();
      resolve();
      console.log("P@3:", precisionsAt3);
      console.log("P@R:", precisionsAtR);
      console.log("AP :", averagePrecisions);
    });
  })
});

function readDocs() {
  return new Promise(function(resolve, reject) {
    // Read and process the movie documents from the movies file.
    $.get("../input/movies.tsv", function(docs) {
      // Get lines. Omit empty part after the last \n.
      var lines = docs.split("\n").slice(0, -1);
      // Add each entry (title and description) to the (global) movies array.
      $.each(lines, function(i, line) {
        // Replace all " by ', since they will cause problems in html code otherwise.
        line = line.replaceAll('"', "'");
        [title, desc] = line.split("\t");
        movies.push([title.trim(), desc.trim()]);
      });
      console.log("Docs file read, #lines =", lines.length);
      resolve();
    })
  });
}

function readBenchmark() {
  return new Promise(function(resolve, reject) {
    // Read and process the evaluation data.
    $.get("../output/movies-benchmark_evaluation.tsv", function(data) {
      // Get lines. Omit empty part after the last \n.
      var lines = data.split("\n").slice(0, -1);
      // The first line contains the headers ("k", "b" and the keyword queries).
      var header = lines[0].split("\t");
      var body = lines.slice(1, -1);
      // The last line contains the ground truth.
      var gt = lines[lines.length - 1].split("\t");
      console.log("Evaluation file read, #modes =", body.length);
      // Read the ground truth. Since there is no k or b, we start at i = 2.
      for (var i = 2; i < header.length; i++) {
        groundTruth[header[i]] = JSON.parse(gt[i]);
      }
      $.each(body, function(i, line) {
        line = line.split("\t");
        var mode = {};
        for (var i in line) {
          if (i != 0 && i != 1) {
            // The entries containing the result ids for the different queries.
            mode[header[i]] = JSON.parse(line[i]);
          } else {
            // The entries containing k and b.
            // Leave floats as string, since we do not need them for computations.
            mode[header[i]] = line[i];
          }
        }
        evaluation.push(mode);
      });
      console.log("Evaluation  :", evaluation);
      console.log("Ground Truth:", groundTruth);
      resolve();
    })
  });
}

function fillOutPrecisions() {
  $.each (evaluation, function(i, mode) {
    var pAt3 = {};
    var pAtR = {};
    var AP = {};
    for (query in groundTruth) {
      pAt3[query] = precisionAtK(mode[query], groundTruth[query], 3);
      pAtR[query] = precisionAtK(mode[query], groundTruth[query], groundTruth[query].length);
      AP[query] = averagePrecision(mode[query], groundTruth[query]);
    }
    precisionsAt3.push(pAt3);
    precisionsAtR.push(pAtR);
    averagePrecisions.push(AP);
  });
}

function precisionAtK(resultIds, relevantIds, k) {
  // Compute the measure P@k for the given list of result ids as it was
  // returned by the inverted index for a single query, and the fiven set of
  // relevant document ids.
  if (k == 0) { return 0; }
  numRelevantResults = 0;
  for (var i = 0; i < Math.min(k, resultIds.length); i++) {
    if (relevantIds.includes(resultIds[i])) {
      numRelevantResults += 1;
    }
  }
  return numRelevantResults / k;
}

function averagePrecision(resultIds, relevantIds) {
  // Compute the average precision (AP) for the given list of result ids as
  // is was returned by the inverted index for a single query, and the given
  // set of relevant document ids.
  sumAP = 0;
  numRelevantResults = 0;
  for (var i = 0; i < resultIds.length; i++) {
    if (relevantIds.includes(resultIds[i])) {
      numRelevantResults += 1;
      sumAP += numRelevantResults / (i + 1);
    }
  }
  return sumAP / relevantIds.length;
}

function appendRowsToOverviewTable() {
  // First append head.
  var row = '<tr>'
    + '<th title="Mode ID">#</th>'
    + '<th colspan="2" title="k and b from the BM25 score formula">Mode</th>'
    + '<th title="Mean Precision at 3 over all queries">MP@3</th>'
    + '<th title="Mean Precision at R over all queries">MP@R</th>'
    + '<th title="Mean Average Precision over all queries">MAP</th>'
    + '<th title="Minimum Average Precision over all queries">MinAP</th>'
    + '<th title="Maximum Average Precision over all queries">MaxAP</th>'
    + '<th title="The percentage of queries with Average Precision > 0.5">AP > 0.5</th>'
    + '</tr>'
  $('#overviewTable thead').append(row);
  // Then append body.
  for (var i = 0; i < evaluation.length; i++) {
    var pAt3 = Object.values(precisionsAt3[i])
    var pAtR = Object.values(precisionsAtR[i])
    var AP = Object.values(averagePrecisions[i])
    row = '<tr id="' + i + '" class="overview-row clickable"> '
      + '<td>' + eval("1+" + i) + '</td>'
      + '<td> k = ' + evaluation[i]['k'] + '</td>'
      + '<td> b = ' + evaluation[i]['b'] + '</td>'
      + '<td>' + getAverage(pAt3).toFixed(3) + '</td>'
      + '<td>' + getAverage(pAtR).toFixed(3) + '</td>'
      + '<td>' + getAverage(AP).toFixed(3) + '</td>'
      + '<td>' + Math.min(...AP).toFixed(3) + '</td>'
      + '<td>' + Math.max(...AP).toFixed(3) + '</td>'
      + '<td>' + getPercentageGreaterThan(AP, 0.5).toFixed(2) + ' %</td>'
      + '</tr>';
    $('#overviewTable tbody').append(row);
  }
}

function getAverage(array) {
  if (array.length == 0) { return 0; }
  var sum = array.reduce((a, b) => a + b, 0);
  return sum / array.length;
}

function getPercentageGreaterThan(array, threshold) {
  if (array.length == 0) { return 0; }
  accepted = 0;
  for (element of array) {
    if (element > threshold) {
      accepted += 1;
    }
  }
  return accepted / array.length * 100;
}

// Variables for the query and mode that is currently displayed in the Result table.
var currentlyShowingQuery;
var currentlyShowingMode;
var nMax;
var n;

$(document).ready(function() {
  
  overviewTablePromise.then(function() {
    $('.overview-row').click(function() {

      // Mark the currently selected row.
      // $(this).siblings().removeClass("selected");
      $(this).toggleClass('selected');

      $('div#detailsbox').show();

      showDetails();
    });
  });

});

function showDetails() {
  var html = '';
  $('div#resultsbox').hide();
  $('.overview-row.selected').each(function() {
    index = $(this).attr('id');
    html += '<h3>Mode #' + eval("1+" + index) + ': Used <i>k = ' + evaluation[index]['k'] + '</i> and <i>b = ' + evaluation[index]['b'] + '</i> for the BM25 scores.</h3>';
    var head = '<tr>'
      + '<th>Keyword Query</th>'
      + '<th title="Precision at 3">P@3</th>'
      + '<th title="Precision at R">P@R</th>'
      + '<th title="Average Precision">AP</th>'
      + '</tr>';
    var body = '';
    for (query in groundTruth) {
      //body += '<tr class="clickable query-row ' + query.replace(/ /g, '_') + '">'
      body += '<tr class="clickable query-row ' + query.replace(/ /g, '_') + '" id="' + query.replace(/ /g, '_') + '-' + index + '">'
        + '<td>' + query + '</td>'
        + '<td>' + precisionsAt3[index][query].toFixed(3) + '</td>'
        + '<td>' + precisionsAtR[index][query].toFixed(3) + '</td>'
        + '<td>' + averagePrecisions[index][query].toFixed(3) + '</td>'
        + '</tr>';
    }
    var foot = '<tr>'
      + '<td>Mean</td>'
      + '<td>' + getAverage(Object.values(precisionsAt3[index])).toFixed(3) + '</td>'
      + '<td>' + getAverage(Object.values(precisionsAtR[index])).toFixed(3) + '</td>'
      + '<td>' + getAverage(Object.values(averagePrecisions[index])).toFixed(3) + '</td>'
      + '</tr>';
    html += '<table class="details"><thead>' + head + '</thead><tbody>' + body + '</tbody><tfoot>' + foot + '</tfoot></table>';
  });
  if (html == '') {
    $('div#detailsbox').hide();
  } else {
    $('#details').html(html);
    makeQueryRowsClickable();
    checkForHovering();
  }
}

function checkForHovering() {
  for (let query in groundTruth) {
    query = query.replace(/ /g, '_');
    $('.' + query).hover(
      function() {
        $('.' + query).addClass('likeHovering');
      }, function() {
        $('.' + query).removeClass('likeHovering');
      }
    );
  }
}

function makeQueryRowsClickable() {
  $('.query-row').click(function() {

    // Mark only the currently selected row.
    //$(this).siblings().removeClass('selected');
    $('.query-row.selected').removeClass('selected');
    $(this).addClass('selected');

    $('div#resultsbox').show();

    [currentlyShowingQuery, currentlyShowingMode] = $(this).attr('id').split('-');
    currentlyShowingQuery = currentlyShowingQuery.replace(/_/g, ' ');
    console.log('Requested results for query: "' + currentlyShowingQuery + '" and mode ' + currentlyShowingMode);

    buildResultTable();

  });
}

function buildResultTable() {
  var html = '<p>The table below shows the ranking of the results for the query <b>"'
    + currentlyShowingQuery + '"</b>. '
    + 'Movies that do not occur in the ground truth and are therefore not relevant are '
    + '<span class="wrong">highlighted</span>. '
    + 'You can sort the table by the ranking of a different mode by clicking on the corresponding header.</p>';
  html += '<table id="resultTable" class="results"><thead></thead><tbody></tbody></table>';
  $('div#results').html(html);
  var head = '<tr>';
  for (mode = 0; mode < evaluation.length; mode++) {
    head += '<th title="Position in the result of mode with '
      + 'k = ' + evaluation[mode]['k']
      + ' and b = ' + evaluation[mode]['b']
      + '" class="clickable sorting" id="sortByMode_' + mode + '">'
      + 'Mode #' + (mode + 1)
      + '</th>';
  }
  head += '<th>Movie Title</th>';
  head += '</tr>';
  $('#resultTable thead').append(head);
  nMax = movies.length;
  n = Math.min(16, nMax);
  appendRows(0, n);
  makeResultTableScrollable();
  makeTableSortable();
}

function makeResultTableScrollable() {
  $('#resultTable tbody').scroll(function() {
    var scrollTop = Math.round($(this).scrollTop());
    var bodyHeight = parseInt($(this).css('height'));
    var scrollHeight = $(this).prop('scrollHeight');
    var scrollPrec = Math.round(100 * scrollTop / (scrollHeight - bodyHeight));
    if (scrollPrec == 100) {
      var nNew = Math.min(2 * n, nMax);
      appendRows(n, nNew);
      n = nNew;
    }
  });
}

function appendRows(k, n) {
  for (i = k; i < n; i++) {
    movieId = evaluation[currentlyShowingMode][currentlyShowingQuery][i];
    var row = '<tr>';
    for (mode = 0; mode < evaluation.length; mode++) {
      row += '<td>';
      // Check if the movieId is in the result of mode. (Will be -1 if not found.)
      var pos = evaluation[mode][currentlyShowingQuery].indexOf(movieId);
      if (pos != -1) {
        var posOneBased = pos + 1;
        row += posOneBased;
      }
      row += '</td>';
    }
    row += '<td title="' + movies[movieId - 1][1] + '"';
    if (!groundTruth[currentlyShowingQuery].includes(movieId)) {
      row += 'class="wrong"';
    }
    row += '>' + movies[movieId - 1][0] + '</td>';
    row += '</tr>';
    $('#resultTable tbody').append(row);
  }
}

function makeTableSortable() {
  $('.sorting').click(function() {
    currentlyShowingMode = $(this).attr('id').split('_')[1];
    buildResultTable();
  });
}
