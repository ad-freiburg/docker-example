// File Paths
const moviesPath = '../input/movies.tsv';
const evaluationPath = '../output/movies-benchmark_evaluation.tsv';

// Configuration variables

// Number of decimal places shown for the precision values.
const decimalPlaces = 3;
// Threshold in the last column of the overview table. Should be between 0 and 1.
const threshold = 0.5;
// Number of rows appended after reaching the bottom of a table with lazy loading
const appendBy = 50;

/* Promise for reading the movies. Wait for this promise before building the
   result details table. */
const docsPromise = readDocs();

/* An array with one entry for each movie. Each entry consists of a pair
   containing (1) the title and (2) a description. */
let movies = [];

/* A dictionary with an entry for each query in the benchmark, where the
   key is a string containing the query and the value is an array containing
   the ground truth results. */
let groundTruth = {};

/* An array with one entry for each mode. Each entry is a dictionary. This
   dictionary contains the keys "k" and "b", where the value is the value
   for k and b, respectively, from the BM25 score.
   Moreover, it contains one entry for each query in the benchmark, where the
   key is a string containing the query and the value is an array containing
   the results and the order this mode returned. */
let evaluation = [];

/* These will be arrays with one entry for each mode.
   Each entry is a dictionary with one entry for each query,
   where the key is the query name and the value is the measure (P@3, P@R or AP). */
let precisionsAt3 = [];
let precisionsAtR = [];
let averagePrecisions = [];

// ============================================================================

$(document).ready(function() {

  $('div#detailsbox').hide();
  $('div#resultsbox').hide();

  /* Read the evaluation file.
     Then, compute the precision measures for each mode and build the overview table. */
  readEvaluation().then(function() {
    fillOutPrecisions();
    $('p#overviewWaitingMessage').remove();
    displayOverviewTable();
  });
                                                                         
  // Click on README link should open dialog box which renders MD as HTML.
  $("a.readme").click(function(e) {
    // Prevent that the link is opened as it normally would in a browser.
    e.preventDefault();
    // The time is added to prevent caching.
    $.get($(this).attr("href") + "?_=" + new Date().getTime(), function  (markdown) {
      let md2html = new showdown.Converter();
      md2html.setFlavor("github");
      $("div.readme").html(md2html.makeHtml(markdown));
      $("div.readme a").attr("target", "_blank");
      $("div.readme").dialog({ width: 1000, height: "auto" });
    });
  });

});

function readDocs() {
  return new Promise(function(resolve, reject) {
    // Read and process the movie documents from the movies file.
    $.get(moviesPath, function(docs) {
      // Get lines. Omit empty part after the last \n.
      let lines = docs.split("\n").slice(0, -1);
      // Add each entry (title and description) to the (global) movies array.
      $.each(lines, function(i, line) {
        // Replace all " by ', since they will cause problems in html code otherwise.
        line = line.replaceAll('"', "'");
        let title;
        let desc;
        [title, desc] = line.split("\t");
        movies.push([title.trim(), desc.trim()]);
      });
      console.log("Finished reading the movies file, #lines =", lines.length);
      resolve();
    });
  });
}

function readEvaluation() {
  return new Promise(function(resolve, reject) {
    /* Read and process the evaluation data. Look at an evaluation tsv-file to
       fully understand how this file is being processed here. */
    $.get(evaluationPath, function(data) {
      // Get lines. Omit empty part after the last \n.
      let lines = data.split("\n").slice(0, -1);
      // The first line contains the headers ("k", "b" and the keyword queries).
      let header = lines[0].split("\t");
      // The last line contains the ground truth.
      let gt = lines[lines.length - 1].split("\t");
      // Read the ground truth. Since there is no k or b, we start at i = 2.
      for (let i = 2; i < header.length; i++) {
        groundTruth[header[i]] = JSON.parse(gt[i]);
      }
      // Process each mode in the evaluation.
      let body = lines.slice(1, -1);
      $.each(body, function(index, line) {
        line = line.split("\t");
        let mode = {};
        for (let i = 0; i < line.length; i++) {
          if (i != 0 && i != 1) {
            // The entries containing the result ids for the different queries.
            mode[header[i]] = JSON.parse(line[i]);
          } else {
            /* The entries containing k and b.
               Leave floats as string, since we do not need them for computations. */
            mode[header[i]] = line[i];
          }
        }
        evaluation.push(mode);
      });
      console.log("Finished reading the evaluation file, #modes =", body.length);
      resolve();
    });
  });
}

function fillOutPrecisions() {
  /* Compute the measures precision at 3, precision at R and average precision
     for each query of each mode. Store them globally. */
  $.each (evaluation, function(i, mode) {
    let pAt3 = {};
    let pAtR = {};
    let AP = {};
    for (let query in groundTruth) {
      if (groundTruth.hasOwnProperty(query)) {
        pAt3[query] = precisionAtK(mode[query], groundTruth[query], 3);
        pAtR[query] = precisionAtK(mode[query], groundTruth[query], groundTruth[query].length);
        AP[query] = averagePrecision(mode[query], groundTruth[query]);
      }
    }
    // Add the computed measures to the corresponding global variables.
    precisionsAt3.push(pAt3);
    precisionsAtR.push(pAtR);
    averagePrecisions.push(AP);
  });
}

function displayOverviewTable() {
  // Append head.
  let head = $('<tr>');
  head.append($('<th>', {
    text: '#',
    title: 'Mode ID'
  }));
  head.append($('<th>', {
    text: 'Mode',
    title: 'k and b from the BM25 score formula', 
    colspan: '2'
  }));
  head.append($('<th>', {
    text: 'MP@3',
    title: 'Mean Precision at 3 over all queries'
  }));
  head.append($('<th>', {
    text: 'MP@R',
    title: 'Mean Precision at R over all queries; R is the number of relevant documents for a query'
  }));
  head.append($('<th>', {
    text: 'MAP',
    title: 'Mean Average Precision over all queries'
  }));
  head.append($('<th>', {
    text: 'MinAP',
    title: 'Minimum Average Precision over all queries'
  }));
  head.append($('<th>', {
    text: 'MaxAP',
    title: 'Max Average Precision over all queries'
  }));
  head.append($('<th>', {
    text: 'AP > ' + threshold,
    title: 'The percentage of queries with Average Precision > ' + threshold
  }));
  $('#overviewTable thead').append(head);

  // Append body.
  for (let i = 0; i < evaluation.length; i++) {
    let pAt3 = Object.values(precisionsAt3[i]);
    let pAtR = Object.values(precisionsAtR[i]);
    let AP = Object.values(averagePrecisions[i]);
    let row = $('<tr>', { id: 'overview_' + i, class: 'overview-row clickable' });
    row.append($('<td>', { text: parseInt(i) + 1 }));
    row.append($('<td>', { text: 'k = ' + evaluation[i].k }));
    row.append($('<td>', { text: 'b = ' + evaluation[i].b }));
    row.append($('<td>', { text: getAverage(pAt3).toFixed(decimalPlaces) }));
    row.append($('<td>', { text: getAverage(pAtR).toFixed(decimalPlaces) }));
    row.append($('<td>', { text: getAverage(AP).toFixed(decimalPlaces) }));
    row.append($('<td>', { text: Math.min(...AP).toFixed(decimalPlaces) }));
    row.append($('<td>', { text: Math.max(...AP).toFixed(decimalPlaces) }));
    row.append($('<td>', { text: getPercentageGreaterThan(AP, threshold).toFixed(2) + ' %' }));
    $('#overviewTable tbody').append(row);
  }

  // Make rows clickable.
  $('.overview-row').click(function() {
    // Mark the currently selected row(s).
    $(this).toggleClass('selected');
    $('div#detailsbox').show();
    displayDetails();
  });
}

function precisionAtK(resultIds, relevantIds, k) {
  /* Compute the measure P@k for the given list of result ids as it was
     returned by the inverted index for a single query, and the given set of
     relevant document ids. */
  if (k == 0) { return 0; }
  let numRelevantResults = 0;
  for (let i = 0; i < Math.min(k, resultIds.length); i++) {
    if (relevantIds.includes(resultIds[i])) {
      numRelevantResults += 1;
    }
  }
  return numRelevantResults / k;
}

function averagePrecision(resultIds, relevantIds) {
  /* Compute the average precision (AP) for the given list of result ids as
     is was returned by the inverted index for a single query, and the given
     set of relevant document ids. */
  let sumAP = 0;
  let numRelevantResults = 0;
  for (let i = 0; i < resultIds.length; i++) {
    if (relevantIds.includes(resultIds[i])) {
      numRelevantResults += 1;
      sumAP += numRelevantResults / (i + 1);
    }
  }
  return sumAP / relevantIds.length;
}

function getAverage(array) {
  // Compute the average of a given array.
  if (array.length == 0) { return 0; }
  let sum = array.reduce((a, b) => a + b, 0);
  return sum / array.length;
}

function getPercentageGreaterThan(array, threshold) {
  /* Return the percentage of elements in the array that are greater than
     the given threshold. */
  if (array.length == 0) { return 0; }
  let accepted = 0;
  for (let element of array) {
    if (element > threshold) {
      accepted += 1;
    }
  }
  return accepted / array.length * 100;
}

function displayDetails() {
  $('div#resultsbox').hide();
  $('div#details').empty();
  // Add details (description and table) for each selected mode.
  $('.overview-row.selected').each(function() {
    // The mode index (0-based)
    let index = $(this).attr('id').split("_")[1];
    // Create description
    let desc = $('<h4>', {
      text: 'Mode #' +
          (parseInt(index) + 1) +
          ': Used k = ' +
          evaluation[index].k +
          ' and b = ' +
          evaluation[index].b +
          ' for the BM25 scores.'
    });
    $('div#details').append(desc);
    // Create table
    let table = $('<table>', { class: 'details' });
    // Create table head
    let thead = $('<thead>');
    let row = $('<tr>');
    row.append($('<th>', { text: 'Keyword Query' }));
    row.append($('<th>', { text: 'P@3', title: 'Precision at 3' }));
    row.append($('<th>', { text: 'P@R', title: 'Precision at R, where R is the number of relevant documents for this query.' }));
    row.append($('<th>', { text: 'AP', title: 'Average Precision' }));
    thead.append(row);
    table.append(thead);
    // Create table body
    let tbody = $('<tbody>');
    for (let query in groundTruth) {
      if (groundTruth.hasOwnProperty(query)) {
        row = $('<tr>', {
          // The id with the query name and mode is used when user clicks on row.
          id: query.replace(/ /g, '_') + '-' + index,
          /* The class with the query name is used to copy the "hover look" to
             all rows corresponding to that query. */
          class: 'clickable query-row ' + query.replace(/ /g, '_')
        });
        row.append($('<td>', { text: query }));
        row.append($('<td>', { text: precisionsAt3[index][query].toFixed(decimalPlaces) }));
        row.append($('<td>', { text: precisionsAtR[index][query].toFixed(decimalPlaces) }));
        row.append($('<td>', { text: averagePrecisions[index][query].toFixed(decimalPlaces) }));
        tbody.append(row);
      }
    }
    table.append(tbody);
    // Create table foot
    let tfoot = $('<tfoot>');
    row = $('<tr>');
    row.append($('<td>', { text: 'Mean' }));
    row.append($('<td>', { text: getAverage(Object.values(precisionsAt3[index])).toFixed(decimalPlaces) }));
    row.append($('<td>', { text: getAverage(Object.values(precisionsAtR[index])).toFixed(decimalPlaces) }));
    row.append($('<td>', { text: getAverage(Object.values(averagePrecisions[index])).toFixed(decimalPlaces) }));
    tfoot.append(row);
    table.append(tfoot);
    $('div#details').append(table);
  });
  if ($('div#details').is(':empty')) {
    $('div#detailsbox').hide();
  } else {
    // Make rows clickable.
    $('.query-row').click(function() {
      // Remove highlighting from other row, if there is one.
      $('.query-row.selected').removeClass('selected');
      $(this).addClass('selected');
      $('div#resultsbox').show();
      let chosenQuery;
      let chosenMode;
      [chosenQuery, chosenMode] = $(this).attr('id').split('-');
      chosenQuery = chosenQuery.replace(/_/g, ' ');
      displayResultTable(chosenQuery, chosenMode);
    });
    checkForHovering();
  }
}

function checkForHovering() {
  for (let query in groundTruth) {
    if (groundTruth.hasOwnProperty(query)) {
      query = query.replace(/ /g, '_');
      $('.' + query).hover(
        function() {
          $('.' + query).addClass('hoverLook');
        }, function() {
          $('.' + query).removeClass('hoverLook');
        }
      );
    }
  }
}

function displayResultTable(chosenQuery, chosenMode) {
  let explanation = 'The table below shows the ranking of the results for the query <b>"' +
      chosenQuery + '"</b>. ' +
      'There are <b>' + groundTruth[chosenQuery].length + ' relevant movies</b> for this query. ' +
      'Movies that do not occur in the ground truth and are therefore not relevant are ' +
      '<span class="wrong">highlighted</span>. ' +
      'You can sort the table by the ranking of a different mode by clicking on the corresponding header. ' +
      'Each movie title provides a tooltip with the description of the movie.';
  $('#resultsParagraph').html(explanation);
  $('div#results').html('<table id="resultTable" class="results scrollable"><thead></thead><tbody></tbody></table>');
  let head = $('<tr>');
  for (let mode = 0; mode < evaluation.length; mode++) {
    let properties = {
      text: 'Mode #' + (mode + 1),
      title: 'Position in the result of mode with k = ' + evaluation[mode].k +
          ' and b = ' + evaluation[mode].b +
          '; click to sort by this row',
      class: 'clickable sorting',
      id: 'sortByMode_' + mode
    };
    if (mode == chosenMode) {
      properties.class += ' currentlySortedBy';
    }
    head.append($('<th>', properties));
  }
  head.append($('<th>', { text: 'Movie Title' }));
  $('#resultTable thead').append(head);
  docsPromise.then(function() {
    let resultsCounter = 0;
    resultsCounter = appendRowsToResultTable(resultsCounter, chosenQuery, chosenMode);
    makeResultTableScrollable(resultsCounter, chosenQuery, chosenMode);
    makeTableSortable(chosenQuery, chosenMode);
    displayRelevantNotInResults(chosenQuery, chosenMode);
    // Turn off old click event first and then create a new click event.
    $('#showRelevant').off().on('click', function() { displayResultTable(chosenQuery, chosenMode); });
  });
}

function appendRowsToResultTable(resultsCounter, chosenQuery, chosenMode) {
  if ($('#showRelevant').is(':checked')) {
    return appendRows(resultsCounter, chosenQuery, chosenMode);
  } else {
    return appendOnlyRelevant(resultsCounter, chosenQuery, chosenMode);
  }
}

function appendOnlyRelevant(resultsCounter, chosenQuery, chosenMode) {
  let results = evaluation[chosenMode][chosenQuery];
  let inList = 0;
  while (resultsCounter < results.length) {
    let movieId = results[resultsCounter];
    resultsCounter++;
    if (groundTruth[chosenQuery].includes(movieId)) {
      inList++;
      let row = $('<tr>');
      for (let mode = 0; mode < evaluation.length; mode++) {
        // Check if the movieId is in the result of mode. (Will be -1 if not found.)
        let pos = evaluation[mode][chosenQuery].indexOf(movieId);
        if (pos != -1) {
          row.append($('<td>', { text: pos + 1 }));
        } else {
          row.append($('<td>'));
        }
      }
      row.append($('<td>', { text: movies[movieId - 1][0], title: movies[movieId - 1][1] }));
      $('#resultTable tbody').append(row);
    if (inList == appendBy) { break; }
    }
  }
  return resultsCounter;
}

function appendRows(resultsCounter, chosenQuery, chosenMode) {
  // Append rows beginning from row k and ending with row n.
  let results = evaluation[chosenMode][chosenQuery];
  let end = Math.min(resultsCounter + appendBy, results.length);
  for (let i = resultsCounter; i < end; i++) {
    let movieId = results[i];
    let row = $('<tr>');
    for (let mode = 0; mode < evaluation.length; mode++) {
      // Check if the movieId is in the result of mode. (Will be -1 if not found.)
      let pos = evaluation[mode][chosenQuery].indexOf(movieId);
      if (pos != -1) {
        row.append($('<td>', { text: pos + 1 }));
      } else {
        row.append($('<td>'));
      }
    }
    let properties = {
      text: movies[movieId - 1][0],
      title: movies[movieId - 1][1]
    };
    if (!groundTruth[chosenQuery].includes(movieId)) {
      properties.class = 'wrong';
    }
    row.append($('<td>', properties));
    $('#resultTable tbody').append(row);
  }
  return resultsCounter + appendBy;
}

function makeResultTableScrollable(resultsCounter, chosenQuery, chosenMode) {
  $('#resultTable tbody').scroll(function() {
    let scrollTop = Math.round($(this).scrollTop());
    let bodyHeight = parseInt($(this).css('height'));
    let scrollHeight = $(this).prop('scrollHeight');
    let scrollPrec = Math.round(100 * scrollTop / (scrollHeight - bodyHeight));
    if (scrollPrec == 100) {
      resultsCounter = appendRowsToResultTable(resultsCounter, chosenQuery, chosenMode);
    }
  });
}

function makeTableSortable(chosenQuery, chosenMode) {
  $('.sorting').click(function() {
    let newChosenMode = $(this).attr('id').split('_')[1];
    if (newChosenMode != chosenMode) {
      displayResultTable(chosenQuery, newChosenMode);
    }
  });
}

function displayRelevantNotInResults(chosenQuery, chosenMode) {
  let notInResults = [];
  let results = evaluation[chosenMode][chosenQuery];
  let gt = groundTruth[chosenQuery];
  for (let movieId of gt) {
    if (! results.includes(movieId)) {
      notInResults.push(movieId);
    }
  }
  if (notInResults.length == 0) {
    let p = '<p>There are no relevant movies that are not in the results for mode #' +
      (parseInt(chosenMode) + 1) +
      '.</p>';
    $('div#notInResults').html(p);
  } else {
    let p = notInResults.length +
      ' relevant movies that did not occur in the results for mode #' +
      (parseInt(chosenMode) + 1);
    $('div#notInResults').html('<br><br>');
    let table = $('<table>', { class: 'scrollable notInRes' });
    let thead = $('<thead>');
    let row = $('<tr>');
    row.append($('<th>', { text: p }));
    thead.append(row);
    table.append(thead);
    let tbody = $('<tbody>');
    // Sort the ids in alphabetical order of their movie titles.
    notInResults.sort(compare);
    for (let movieId of notInResults) {
      row = $('<tr>');
      row.append($('<td>', { text: movies[movieId - 1][0], title: movies[movieId - 1][1] }));
      tbody.append(row);
    }
    table.append(tbody);
    $('div#notInResults').append(table);
  }
}

function compare(id1, id2) {
  /* Return 1 if the movie title corresponding to id1 is (alphabetically)
     greater than the movie title corresponding to id2; return -1 if it is
     smaller and 0 otherwise. */
  if (movies[id1 - 1][0] > movies[id2 - 1][0]) { return 1; }
  if (movies[id1 - 1][0] < movies[id2 - 1][0]) { return -1; }
  return 0;
}
