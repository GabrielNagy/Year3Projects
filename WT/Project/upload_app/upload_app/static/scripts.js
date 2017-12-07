function start_task(uuid) {
    div = $('<div class="progress-' + uuid + '"><div class="result"></div><samp><div class="replace-with-code">running...</div></samp><div></div></div><hr>');
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
