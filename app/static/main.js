var svg;
$(document).ready(function(){
    svg = document.getElementsByTagName('svg')[0];

    setInterval(function () {
        $.get('/v1/board/', function (data) {
            $('.debug').html( JSON.stringify(data) );
        })
    }, 500)
});

