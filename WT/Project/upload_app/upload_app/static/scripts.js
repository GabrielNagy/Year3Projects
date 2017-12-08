function start_task(uuid) {
    div = $('<div class="progress-' + uuid + '"><div class="result"></div><samp><div class="replace-with-code">Your task has been placed in the queue and is running. Be patient...</div></samp><div></div></div>');
    $('#progress-' + uuid).append(div);
    $('.btn-' + uuid).prop('disabled', true);
    $.ajax({
        type: 'POST',
        url: '/run/' + uuid,
        success: function(data, status, request) {
            status_url = request.getResponseHeader('Location');
            update_progress(status_url, div[0]);
        },
        error: function() {
              alert('Unexpected error');
        }
    });
}

function update_progress(status_url, status_div) {
    $.getJSON(status_url, function(data) {
        console.log('status: ' + data['status']);
        console.log('result: ' + data['result']);
        console.log('state: ' + data['state']);
        if (typeof(data['status']) === "string") {
            $(status_div.childNodes[1]).text(data['status']);
        } else {
            $(status_div.childNodes[1]).html(data['status'].join('\r<br />'));
        }
        if (data['state'] != 'PENDING' && data['state'] != 'PROGRESS') {
            if ('result' in data) {
                $(status_div.childNodes[0]).text(data['result']);
            }
        }
        else {
            setTimeout(function() {
                update_progress(status_url, status_div);
            }, 2000);
        }
    });
}

// Set the date we're counting down to
var countDownDate = new Date("Dec 9, 2017 09:00:00").getTime();

// Update the count down every 1 second
var x = setInterval(function() {

    // Get todays date and time
    var now = new Date().getTime();

    // Find the distance between now an the count down date
    var distance = countDownDate - now;

    // Time calculations for days, hours, minutes and seconds
    //var days = Math.floor(distance / (1000 * 60 * 60 * 24));
    var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    var seconds = Math.floor((distance % (1000 * 60)) / 1000);

    // Output the result in an element with id="demo"
    //days + "d " +
    document.getElementById("demo").innerHTML = hours + "h "
    + minutes + "m " + seconds + "s ";

    // If the count down is over, write some text
    if (distance < 0) {
        clearInterval(x);
        document.getElementById("demo").innerHTML = "EXPIRED";
    }
}, 1000);
