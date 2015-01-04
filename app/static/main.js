var TIME_SLOT=500;
var delay_factor = 1.0;

$(document).ready(function(){
    var robots = {};
    setInterval(function () {
        $.get('/v1/board/', function (data) {
            data['delay_factor'] = delay_factor;
            $('.debug').html( JSON.stringify(data) );
            for (k in data.robots) {
                if (data.robots.hasOwnProperty(k)) {
                    var name = data.robots[k].name;
                    if (!(name in robots)) {
                        robots[name] = data.robots[k];
                        $('.board').append('<div class="robot" id="'+name+'" title="'+name+'">+</div>');
                        $('#'+name).css({left:parseInt(robots[name].x), bottom:parseInt(robots[name].y)});
                    } else {
//                        if ($('#'+name).is(':animated')) {
//                            delay_factor -= 0.0078125;
//                        } else {
//                            delay_factor += 0.0078125;
//                        }
                        $('#'+name).animate(
                            {left:parseInt(data.robots[k].x)+'px', bottom:parseInt(data.robots[k].y)+'px'},
                            TIME_SLOT * delay_factor,
                            "linear"
                            );
                    }
                }
            }
        })
    }, TIME_SLOT);
});

