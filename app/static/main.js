
// TOSET
var TIME_SLOT       = 500; // time interval between ajax data request
var REFRESH_RATE    = 30; // how many times boards must be refreshed in a second
var REFRESH_TIME    = 1000/REFRESH_RATE; // time interval between updates
var TIME_SLOT_RATE  = 1000/TIME_SLOT; // how many data request in a second
var delay_factor    = 1.0;
var delta_time      = 0.50;

// FPS variable
var FPScounter = 0;
var lastTime;


// DEBUG
var getDataRobot = true,
    getDataRadar = true,
    getDataMissiles = true,
    getDataExplosions = true;
var drawRobot = true,
    drawRadar = true,
    drawMissiles = true,
    drawExplosions = true,
    drawDmgPopup = true;

// Robots
var robots = [];

function Robot(name,hp,x,y,dx,dy) {
    this.name=name;
    this.hp=hp;
    this.x=x;
    this.y=y;
    this.dx=dx;
    this.dy=dy;
    this.destx=x;
    this.desty=y;
    this.interval=null;
}

function RobotMove (i) {
    robots[i].x += robots[i].dx;
    robots[i].y += robots[i].dy;
}
/**
 * @param i unique name
 * This function avoid the accumulation of errors in the robots' positions
 * caused by adding dx and dy values, so i force destination x and y
 * to be the actual coordinates for the robot.
 */
function ResetRobotPosition (i) {
    robots[i].x = robots[i].destx;
    robots[i].y = robots[i].desty;
}


// Radars
var radars = [];

function Radar(x, y, dist, degree, res) {
    this.x=x;
    this.y=y;
    this.distance=dist;
    this.degree=degree;
    this.resolution=res;
    this.opacity=1.0;
}

// Missiles
var missiles = [];

function Missile(x, y, degree, distance, speed) {
    this.x = x;
    this.y = y;
    this.step = Math.ceil((distance/(speed*delta_time))*REFRESH_RATE);
    this.dx = (distance*Math.cos(degree))/this.step;
    this.dy = -(distance*Math.sin(degree))/this.step; // - because 0,0 is top left
    this.active=true;
}

function MissileMove(i) {
    missiles[i].x += missiles[i].dx;
    missiles[i].y += missiles[i].dy;
    --missiles[i].step;
}

// Explosions
var explosions = [];

function Explosion(x, y, dmg) {
    this.x=x;
    this.y=y;
    this.radius=dmg;
    this.opacity=1.0;
    this.active=true;
}

// Damage Popup
var damagepop = [];

function DamagePop(x, y, dmg) {
    this.x=x;
    this.y=y;
    this.dmg=dmg;
    this.opacity=1.0;
    this.step = Math.ceil(2*REFRESH_RATE); // 2s for the popup to disappear
}



// Canvas
var c2d = document.getElementById("board"),
    ctx = c2d.getContext("2d");

// Cross-browser support for requestAnimationFrame
var w = window;
requestAnimationFrame = w.requestAnimationFrame || w.webkitRequestAnimationFrame || w.msRequestAnimationFrame || w.mozRequestAnimationFrame;

// The main game loop
var main = function () {

    render();

    // fps counter
    if (Date.now()-lastTime > 1000) {
        $('#fps').html(FPScounter);
        FPScounter=0;
        lastTime = Date.now();
    }
    ++FPScounter;

    // Request to do this again ASAP
    requestAnimationFrame(main);
};

var render = function () {
    // reset the canvas
    var k;
    var tempfont;
    ctx.clearRect(0, 0, c2d.width, c2d.height);
    if (drawRobot) {
        for (k in robots) {
            if (robots.hasOwnProperty(k)) {
                ctx.fillStyle = "#008800";
                ctx.strokeStyle = "#008800";

                // draw robot's NAME + HP
                tempfont = ctx.font;
                ctx.font="16px Verdana";
                ctx.fillText(k+" "+robots[k].hp+"hp", robots[k].x+10, robots[k].y-10);
                ctx.font = tempfont;

                // draw robot's shape
                ctx.beginPath();
                ctx.lineWidth = 1;
                ctx.arc(
                    robots[k].x,
                    robots[k].y,
                    3, 0, Math.PI*2
                );
                ctx.fill();
                ctx.stroke();
                ctx.closePath();
            }
        }
    }
    if (drawRadar) {
        for (k in radars) {
            if (radars.hasOwnProperty(k)) {
                var radius      = radars[k].distance;
                var xRobot      = parseInt(radars[k].x);
                var yRobot      = parseInt(radars[k].y);
                var degreeRad   = Math.PI*radars[k].degree/180.0;
                var resRad      = Math.PI*radars[k].resolution/180.0;
                var degreeStart = 2*Math.PI-degreeRad-resRad;
                var degreeEnd   = 2*Math.PI-degreeRad+resRad;
                var xStartScan  = xRobot+radius*Math.cos(degreeStart);
                var yStartScan  = yRobot+radius*Math.sin(degreeStart);
                var xEndScan    = xRobot+radius*Math.cos(degreeEnd);
                var yEndScan    = yRobot+radius*Math.sin(degreeEnd);

                ctx.fillStyle = "#6464FF";
                ctx.strokeStyle = "#6464FF";
                ctx.lineWidth = 1;
                ctx.globalAlpha = radars[k].opacity;

                // Create the shape of the scan by adding a triangle and an arc
                // create a triangle of the scan
                ctx.beginPath();
                ctx.moveTo(xRobot, yRobot);
                ctx.lineTo(xStartScan, yStartScan);
                ctx.lineTo(xEndScan, yEndScan);
                ctx.lineTo(xRobot, yRobot);
                ctx.closePath();
                ctx.fill();
                ctx.stroke();
                // add a filled arc to the triangle
                ctx.beginPath();
                ctx.arc(xRobot, yRobot, radius, degreeStart, degreeEnd, false);
                ctx.closePath();
                ctx.fill();
                ctx.stroke();

                ctx.globalAlpha = 1.0;
            }
        }
    }
    if (drawMissiles) {
        for (k in missiles) {
            if (missiles.hasOwnProperty(k)) {
                if (missiles[k].step > 0) {
                    ctx.fillStyle = "#880000";
                    ctx.strokeStyle = "#880000";
                    ctx.lineWidth = 1;

                    ctx.beginPath();
                    ctx.arc(
                        parseInt(missiles[k].x),
                        parseInt(missiles[k].y),
                        3, 0, Math.PI*2
                    );
                    ctx.fill();
                    ctx.stroke();
                    ctx.closePath();
                }
            }
        }
    }
    if (drawExplosions) {
        for (k in explosions) {
            if (explosions.hasOwnProperty(k)) {
                if(explosions[k].active) {
                    ctx.fillStyle = "#880000";
                    ctx.strokeStyle = "#880000";
                    ctx.lineWidth = 1;
                    ctx.globalAlpha = explosions[k].opacity;

                    ctx.beginPath();
                    ctx.arc(
                        parseInt(explosions[k].x),
                        parseInt(explosions[k].y),
                        explosions[k].radius, 0, Math.PI*2
                    );
                    ctx.fill();
                    ctx.stroke();
                    ctx.closePath();

                    ctx.globalAlpha = 1.0;
                }
            }
        }
    }
    if (drawDmgPopup) {
        for (k in damagepop) {
            if (damagepop.hasOwnProperty(k)) {
                ctx.fillStyle = "#880000";
                ctx.strokeStyle = "#880000";
                //ctx.globalAlpha = explosions[k].opacity;

                tempfont = ctx.font;
                ctx.font=16+(damagepop[k].dmg/5)+"px Verdana";
                ctx.fillText("-"+damagepop[k].dmg, damagepop[k].x-10, damagepop[k].y-10);
                ctx.font = tempfont;
                //ctx.globalAlpha = 1.0;
            }
        }
    }
};

var update = function () {
    var k;
    for (k in robots) {
        if (robots.hasOwnProperty(k)) {
            RobotMove(k);
        }
    }
    for (k in radars) {
        if (radars.hasOwnProperty(k)) {
            radars[k].opacity-=0.1;
            if (radars[k].opacity <= 0) {
                delete radars[k];
            }
        }
    }
    for (k in missiles) {
        if (missiles.hasOwnProperty(k)) {
            if(missiles[k].active) {
                MissileMove(k);
                if (missiles[k].step <= 0) {
                    missiles[k].active = false;
                }
            }
        }
    }
    for (k in explosions) {
        if (explosions.hasOwnProperty(k)) {
            if(explosions[k].active) {
                explosions[k].opacity-=0.1;
                if (explosions[k].opacity <= 0) {
                    explosions[k].active = false;
                }
            }
        }
    }
    for (k in damagepop) {
        if (damagepop.hasOwnProperty(k)) {
            damagepop[k].y-=1;
            --damagepop[k].step;
            if (damagepop[k].step <= 0) {
                delete damagepop[k];
            }
        }
    }
};

$(document).ready(function(){
    var interval = setInterval(function () {
        $.get('/v1/board/', function (data) {
            $('.robot-list').html('');
            data['delay_factor'] = delay_factor;
            if (getDataRobot) {
                for (k in data.robots) {
                    if (data.robots.hasOwnProperty(k)) {

                        var name = data.robots[k].name;
                        var destinationX = parseInt(data.robots[k].x);
                        var destinationY = 1000 - parseInt(data.robots[k].y); // canvas 0,0 is top left
                        var hp = parseInt(data.robots[k].hp);
                        var speed = parseInt(data.robots[k].speed);

                        // robot not already added, add and create new robot
                        if (!(name in robots)) {
                            robots[name] = new Robot(name, hp, destinationX, destinationY, 0, 0);
                        } else {
                            // update robot's positions
                            ResetRobotPosition(name);   // see notes above this function implementation
                            var currentX = robots[name].x;
                            var currentY = robots[name].y;
                            var dx = (destinationX-currentX)/(REFRESH_RATE/TIME_SLOT_RATE);
                            var dy = (destinationY-currentY)/(REFRESH_RATE/TIME_SLOT_RATE);
                            robots[name].destx=destinationX;
                            robots[name].desty=destinationY;
                            robots[name].dx=dx;
                            robots[name].dy=dy;
                            // took damage?
                            if (hp != robots[name].hp) {
                                damagepop[k] = new DamagePop(currentX, currentY, robots[name].hp - hp);
                                robots[name].hp = hp;
                            }
                        }

                        // stats
                        $('.robot-list').append('<li id="'+name+'"></li>');
                        var extra = '';
                        if (name in data.kdr) {
                            extra = ' - KDR: ' + data.kdr[name].kill + '/' + data.kdr[name].death;
                        }
                        $('.robot-list li#'+name).html(name+' - HP: '+hp+' - SP: '+ speed + extra);
                    }
                }
            }
            if (getDataRadar) {
                for (k in data.radar) {
                    if (data.radar.hasOwnProperty(k)) {
                        var radar = data.radar[k];
                        radars[k] = new Radar(radar.xy[0], 1000-radar.xy[1], radar.distance, radar.degree, radar.resolution);
                    }
                }
            }
            if (getDataMissiles) {
                for (k in data.missiles) {
                    if (data.missiles.hasOwnProperty(k)) {
                        var missile = data.missiles[k];
                        if (!(k in missiles)) {
                            missiles[k] =
                                new Missile(
                                    parseInt(missile.x),
                                    1000 - parseInt(missile.y),
                                    Math.PI*missile.degree/180.0,
                                    missile.distance,
                                    missile.speed
                                );
                        }
                    }
                }
                for (k in missiles) {
                    if (!(k in data.missiles)) {
                        if (missiles.hasOwnProperty(k)) {
                            delete missiles[k];
                        }
                    }
                }
            }
            if (getDataExplosions) {
                for (k in data.explosions) {
                    if (data.explosions.hasOwnProperty(k)) {
                        if (!(k in explosions)) {
                            var explosion = data.explosions[k];
                            var radius = parseInt(explosion.damage[0][0]);
                            var x = parseInt(explosion.x);
                            var y = 1000 - parseInt(explosion.y);
                            explosions[k] = new Explosion(x,y,radius);
                            //$('.debug').html($('.debug').text()+Date.now()+" - new explosion<br>");
                        }
                    }
                }
                for (k in explosions) {
                    if (!(k in data.explosions)) {
                        if (explosions.hasOwnProperty(k)) {
                            delete explosions[k];
                        }
                    }
                }
            }

        })
    }, TIME_SLOT);

    $('.reset-game').click( function(e) {
        e.preventDefault();
        $.post('/v1/board/reset', {}, function (data) {robots = {};});
        $('.board').html('');
        $('.robot-list').html('');
        return false;
    });

    lastTime = Date.now();
    main();
    var updateInterval = setInterval(update, REFRESH_TIME);
});