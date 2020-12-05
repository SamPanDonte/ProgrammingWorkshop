$(document).ready(function () {
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                let cookies = document.cookie.split(';')
                for (let i = 0; i < cookies.length; ++i) {
                    let cookie = jQuery.trim(cookies[i]);
                    if (cookie.substring(0, 10) === 'csrftoken=') {
                         cookieValue = decodeURIComponent(cookie.substring(10));
                         break;
                     }
                }
            }
            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                xhr.setRequestHeader("X-CSRFToken", cookieValue);
            }
        }
    });
});

function del(url, id = null) {
    $.ajax({
        url: url,
        type: 'DELETE',
        success: function (data) {
            if (id !== null) {
                $(id).remove()
            }
            console.log(data)
        },
        error: function (data) {
            console.log(data)
        }
    });
}