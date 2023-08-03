/* Counts the number of items in an unordered 
list and displays that number*/
function listen() {
    var numLi = (document.getElementById
        ("sortable2").getElementsByTagName("li"));
    var addNumPlayers = document.getElementById('numPlayers').innerHTML;
    addNumPlayers = addNumPlayers.substr(0, 64) + numLi.length;
    document.getElementById('numPlayers').innerHTML = addNumPlayers;

    if (numLi.length <= 1) { 
        document.getElementById('launchButton').disabled = true;
    } else { 
        document.getElementById('launchButton').disabled = false;
    }
}

/* Used to drag and drop the available players' list to the registered 
players' list */
$( function() {
    $( "#sortable1, #sortable2" ).sortable({
      connectWith: ".connectedSortable",
      stop: listen
    }).disableSelection();
    numLi()
} );

/* Adds registred players to after using drag and drop */
function addPlayers() {
	var names = []
    $.each($('#sortable2').find('li'), function() {
        var data = $(this).text();
	    names.push(data)
    });
    submitNewTournament(names)
}

/* Submits registred players to views.py */
function submitNewTournament(names) {
    var token = '{{csrf_token}}';
    var tournament_name = $('input[name="tournament_name"]').val();
    var season_name = $('#season_name :selected').text();
    var tournament_type = $('#tournament_type :selected').text();
    $.ajax({
        method: 'POST',
	    url: "",
	    data: {'playernames': names, 
            'tournament_name': tournament_name,
            'tournament_type': tournament_type,
            'season_name': season_name, 
            csrfmiddlewaretoken: $("input[name='csrfmiddlewaretoken']").val()},
        
        success: function(response) {
            if (response.success) {
                window.location.href= ("/tournamentspage/tournamentstats/"
                 + response.url);
            } else {
                window.location.href= ""
            }
        },
    },);
}

/*Disables button that submits a new player if the input field is empty from the
playerspage*/
function success() {
    if(document.getElementById("username").value==="") { 
        document.getElementById('playerButton').disabled = true; 
    } else { 
        document.getElementById('playerButton').disabled = false;
    }
}

// Load google charts
google.charts.load('current', {'packages':['corechart']});
google.charts.setOnLoadCallback(drawChart);

// Draw the pie chart and set the chart values
function drawChart() {
    var rank50 = document.getElementById('top50').value
    var rank8 = document.getElementById('top8').value
    var rank4 = document.getElementById('top4').value
    var rankTop = document.getElementById('tops').value
    var data = google.visualization.arrayToDataTable([
    ["Ratio", 'Number of times in ratio'],
    ["Top 50%", parseInt(rank50)],
    ["Top 8%", parseInt(rank8)],
    ["Top 4%", parseInt(rank4)],
    ["Top Player%", parseInt(rankTop)],
]);

  // Optional; add a title and set the width and height of the chart
  var options = {
    'width':1200, 
    'height':600,
    is3D: true,
    backgroundColor: 'transparent',
    'legend': {
        textStyle: {
            color: 'white',
            fontSize: 18,
        },
        position: 'right', alignment: 'center',
        size: 100,
    },
  };

  // Display the chart inside the <div> element with id="piechart"
  var chart = new google.visualization.PieChart(document.getElementById('piechart'));
  chart.draw(data, options);
}

/*Adapts button in ongoing tournament page based on selected radios*/
/* id parameter is the radios id */
/* name is the name associated with an input tag 
(which will be the match name) */
function adaptButton(matchName, isundo) {
    var radioId = 'radioCheck';
    var checkedboxes = document.querySelectorAll(
        'input[id=' + radioId +']:checked').length;
    var allcheckboxes = document.querySelectorAll(
        'input[id=' + radioId + ']').length;
    var isDraw = document.getElementById(matchName + 'draw').disabled;
    
    var numDraws = document.getElementsByName("drawButton").length;
    var selectedDraw = 0;
    for (i = 0; i < numDraws; i++) {
        if (document.getElementsByName("drawButton")[i].value != "") {
            selectedDraw++;
        }
    }
    checkedboxes += selectedDraw
    if (checkedboxes == 0) { 
        document.getElementById('endMatchbutton').disabled = true;
    } else {
        if (!isundo) {
            document.getElementById(matchName + 'undo').disabled = false;
            document.getElementById(matchName + 'draw').disabled = true;
        }
        document.getElementById('endMatchbutton').disabled = false;
        if ((allcheckboxes / 2) == checkedboxes) {
            document.getElementById('endMatchbutton').innerHTML = 'End Round';
        } else if (checkedboxes == 1) {
            document.getElementById('endMatchbutton').innerHTML = 'End Match';
        } else if ((checkedboxes >= 2) && 
            (checkedboxes != (allcheckboxes / 2))) {
            document.getElementById('endMatchbutton').innerHTML = 'End Matches';
        }
    }
}
/* Displays show or hidden depending on whether an accordion has opened or
is collapsed respectivley */
function accordionStatus(id) {
    var status = document.getElementById(id).innerHTML
    var i = 0;
    for (i = 0; i < status.length; i++) {
        if (status.charAt(i) == '(') {
            break
        }
    }
    var newStatus = status.substr(0, i);
    if (status.includes('Show')) {
        document.getElementById(id).setAttribute('title', 'Click To Hide');
        document.getElementById(id).innerHTML = newStatus + '(Hide)';
    } else {
        document.getElementById(id).setAttribute('title', 'Click To Show');
        document.getElementById(id).innerHTML = newStatus + '(Show)';
    }
}
/* Undos a match or a checked radio (depends on whether a match has ended) */
/* name1 and name2 are the names for the input radio*/
function undo(matchName) {
    var radioName1 = document.getElementsByName(matchName)[0].checked;
    var radioName2 = document.getElementsByName(matchName)[1].checked;
    if (radioName1) {
        document.getElementsByName(matchName)[0].checked = false;
    } else if (radioName2) {
        document.getElementsByName(matchName)[1].checked = false;
    } else if (document.getElementById(matchName + "drawInput").value != "") {
        document.getElementById(matchName + "draw").style.background = "white";
        document.getElementById(matchName + "draw").style.color = '#212529';
        document.getElementById(matchName + "drawInput").value = "";
        document.getElementById(matchName + "draw").value = "";
        document.getElementsByName(matchName)[0].disabled = false;
        document.getElementsByName(matchName)[1].disabled = false;
    }
    document.getElementById(matchName + 'draw').disabled = false;
    document.getElementById(matchName + "undo").disabled = true;
    adaptButton(matchName, true)
}
/*Finds the available players in order to use autocomplete for the tournament
creation search bar*/
function getPlayers() {
    var availablePlayers = [];
    $.each($('#sortable1').find('li'), function() {
        var data = $(this).text();
        availablePlayers.push(data)
    });
    $( "#availablePlayers" ).autocomplete({
        source: availablePlayers,
    });

    if (event.keyCode === 13) {
        // Cancel the default action, if needed
        event.preventDefault();
        // Trigger the button element with a click
        document.getElementById("addToRegistered").click();
        document.getElementById("availablePlayers").value = "";
    }
}

/*Moves player to registred player list when 'Add Player' button is clicked*/
function moveToSortable2(id) {
    var text = document.getElementById(id).value;
    var playerExist = false;
    var availablePlayers = [];
    $.each($('#sortable1').find('li'), function() {
        var data = $(this).text();
        if (data == text) {
            playerExist = true;
            return false;
        }
    });

    if (playerExist) {
        var addli = $("<li class='ui-state-default'/>").text(text);
        $('li').filter( function() 
        { 
            return $.text([this]) === text; 
        }).remove();
        $("#sortable2").append(addli);
        listen()
        document.getElementById("availablePlayers").value = "";
    }   
}

/*Prevents launch button from being clicked when pressing enter*/
$("#launchButton").ready(function() {
  $(window).keydown(function(event){
    if(event.keyCode == 13) {
      event.preventDefault();
      return false;
    }
  });
});

/* Fixes navbar to top of a page when scrolling */
// When the user scrolls the page, execute myFunction
$( function() {
    window.onscroll = function() {myFunction()};

    // Get the navbar
    var navbar = document.getElementById("navbar");

    // Get the offset position of the navbar
    var sticky = navbar.offsetTop;

    // Add the sticky class to the navbar when you reach its scroll position. Remove "sticky" when you leave the scroll position
    function myFunction() {
      if (window.pageYOffset >= sticky) {
        navbar.classList.add("sticky")
      } else {
        navbar.classList.remove("sticky");
      }
    }
} );

/* Disables and highlights the drawbutton on click. Also disables the radio
checkboxes*/
function drawMatch(matchName) {
    document.getElementById(matchName + "draw").style.background = "#008000";
    document.getElementById(matchName + "draw").disabled = true;
    document.getElementById(matchName + "undo").disabled = false;
    document.getElementById(matchName + "draw").style.color = "black";
    document.getElementById(matchName + "drawInput").value = "drawInput";
    document.getElementById(matchName + "draw").value = "drawButton";
    document.getElementsByName(matchName)[0].disabled = true;
    document.getElementsByName(matchName)[1].disabled = true;
    adaptButton(matchName, false)
}

function chgDrawColour(player1, player2) {
    document.getElementById(player1).style.background = "#43464B";
    document.getElementById(player2).style.background = "#43464B";
}

function chgEndMatchColour(winner, loser) {
    document.getElementById(winner).style.background = "#013220";
    document.getElementById(loser).style.background = "#bb1b1b";
}

function undoColour(player1, player2) {
    document.getElementById(player1).style.background = "#020432";
    document.getElementById(player2).style.background = "#020432";
}

function goToPage() {
    $.each($('#pageInput').find('option'), function() {
        var data = $(this).val().replace( /^\D+/g, '');
        if (this.selected)
            window.location.href = "?page=" + data;
    });
}

function addInputToOption(selectId, inputId) {
    var inputValue = document.getElementById(inputId).value;
    var swapSelected = $(selectId + " option:selected" ).text();
    $(selectId + " option:selected" ).text(inputValue)
    $(selectId).append($('<option>', {
        text: swapSelected
    }));
}