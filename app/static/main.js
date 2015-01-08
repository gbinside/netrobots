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
            for (k in data.radar) {
                if (data.radar.hasOwnProperty(k)) {
                    var radar = data.radar[k];
                    $('.board').append('<div class="radar" id="'+k+'"><div class="arc"></div></div>');
                    $('#'+k).fadeOut(1000, function() { $(this).remove(); });
                    var h = Math.sin(Math.PI*radar.resolution/180.0) * radar.distance;
                    $('#'+k).css({
                        left:parseInt(radar.xy[0]) - radar.distance, // + radar.distance/2.0*Math.cos(Math.PI*radar.degree/180.0)-radar.distance/2.0,
                        bottom:parseInt(radar.xy[1]) - h , //-radar.distance/2.0*Math.sin(Math.PI*radar.degree/180.0),
                        transform:'rotate('+((360-parseInt(radar.degree))%360)+'deg)'
                        });

                    $('#'+k+' .arc').css({
                        'border-left': radar.distance+'px solid transparent',
                        'border-right': radar.distance+'px solid rgba(100,100,255,0.5)',
                        'border-top': h+'px solid transparent',
                        'border-bottom': h+'px solid transparent'
                        });
                }
            }
        })
    }, TIME_SLOT);
});

