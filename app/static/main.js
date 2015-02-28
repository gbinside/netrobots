
// -TO SET-
var TIME_SLOT           = 450; // time interval between ajax data request
var REFRESH_RATE        = 30; // how many times boards must be refreshed in a second
var statsTab            = true; // use TAB STATS or DIV STATS
// ROBOT GARBAGE
// max time for a robot to do something otherwise it'll considered dead
// simply will be reloaded if it appears again in the data from the ajax request
var MAX_TIME_ROBOT_DEAD = Math.ceil(2*REFRESH_RATE);


// -TO NOT SET-
var REFRESH_TIME        = 1000/REFRESH_RATE; // time interval between updates
var TIME_SLOT_RATE      = 1000/TIME_SLOT; // how many data request in a second
var DELAY_FACTOR        = 1.0;  // delay based on server's times intervals
// KEYBOARD variable
var showStatsTab = false;
var alwaysShowStatsTab  = true; // always show STATS
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
    drawDmgPopup = true,
    drawReloadingPopup = true;

// Robots
var robots = [];

var paletteColors = [
    '#CC00CC', // viola
    '#3333FF', // blu
    '#009999', // verde-acqua
    '#009933', // verde
    '#999966', // verde-grigio
    '#FF9900', // arancione
    '#CC3333', // rosso
    '#996633'  // marrone
];

function Robot(name,hp,x,y,dx,dy,speed,kdr) {
    this.name=name;
    this.hp=hp;
    this.x=x;
    this.y=y;
    this.dx=dx;
    this.dy=dy;
    this.destx=x;
    this.desty=y;
    this.speed=speed;
    this.kdr=kdr;
    this.interval=null;
    this.reloading_timer=0;
    this.step = MAX_TIME_ROBOT_DEAD;
    this.color = GetColor();
}
/**
 * @return {string}
*/
function GetColor () {
    var colors = paletteColors;
    for(var k in robots) {
        for(var i=0; i<colors.length; ++i) {
            if (robots.hasOwnProperty(k)) {
                if (robots[k].color==colors[i]) {
                    colors.splice(i, 1);
                }
            }
        }
    }
    if (colors.length>0) {
        return colors[Math.floor(Math.random()*colors.length)];
    } else {
        return paletteColors[Math.floor(Math.random()*paletteColors.length)];
    }
}

function RobotMove (i) {
    robots[i].x += robots[i].dx;
    robots[i].y += robots[i].dy;
}

function KDR(kill,death) {
    this.kill=kill;
    this.death=death;
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
    this.active=true;
}

// Missiles
var missiles = [];

function Missile(x, y, degree, distance, speed) {
    this.x = x;
    this.y = y;
    this.step = Math.ceil((distance/(speed*DELAY_FACTOR))*REFRESH_RATE);
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


// Reloading Popup
var reloadingpop = [];

function ReloadingPop(x, y, time) {
    this.x=x;
    this.y=y;
    this.time=time;
    this.opacity=1.0;
    this.step = Math.ceil(REFRESH_RATE); // 1s for the popup to disappear
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
                ctx.fillStyle = ctx.strokeStyle = robots[k].color;

                // draw robot's NAME + HP
                tempfont = ctx.font;
                ctx.font="16px Verdana";
                ctx.fillText(k+" "+robots[k].hp+"hp", robots[k].x+10, robots[k].y-10);
                ctx.font = tempfont;

                if (showStatsTab || alwaysShowStatsTab) {
                    // draw robot's SP, KDA
                    tempfont = ctx.font;
                    ctx.font="14px Verdana";
                    ctx.fillText("KDA: "+robots[k].kdr.kill+'/'+robots[k].kdr.death+", SP:"+robots[k].speed, robots[k].x+10, robots[k].y+10);
                    ctx.font = tempfont;
                }

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
                if(radars[k].active) {
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
                ctx.font=16+(damagepop[k].dmg/2)+"px Verdana";
                ctx.fillText("-"+damagepop[k].dmg, damagepop[k].x-10, damagepop[k].y-10);
                ctx.font = tempfont;
                //ctx.globalAlpha = 1.0;
            }
        }
    }
    if (drawReloadingPopup) {
        for (k in reloadingpop) {
            if (reloadingpop.hasOwnProperty(k)) {
                ctx.fillStyle = "#0066CC";
                ctx.strokeStyle = "#0066CC";
                //ctx.globalAlpha = explosions[k].opacity;

                tempfont = ctx.font;
                ctx.font="16px Verdana";
                ctx.fillText(reloadingpop[k].time, reloadingpop[k].x-10, reloadingpop[k].y+20);
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
            // consider robot dead if not found in data.robots for a
            // MAX_TIME_ROBOT_DEAD steps
            --robots[k].step;
            if (robots[k].step <= 0) {
                delete robots[k];
            }
        }
    }
    for (k in radars) {
        if (radars.hasOwnProperty(k)) {
            if(radars[k].active) {
                radars[k].opacity-=0.1;
                if (radars[k].opacity <= 0) {
                    radars[k].active = false;
                }
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
    for (k in reloadingpop) {
        if (reloadingpop.hasOwnProperty(k)) {
            reloadingpop[k].y+=1;
            --reloadingpop[k].step;
            if (reloadingpop[k].step <= 0) {
                delete reloadingpop[k];
            }
        }
    }
};

$(document).ready(function(){
    var interval = setInterval(function () {
        $.get('/v1/board/', function (data) {
            var k;
            $('.robot-list').html('');
            DELAY_FACTOR = data['delayfactor'];
            if (getDataRobot) {
                for (k in data.robots) {
                    if (data.robots.hasOwnProperty(k)) {

                        var name = data.robots[k].name;
                        var destinationX = data.robots[k].x;
                        var destinationY = 1000 - data.robots[k].y; // canvas 0,0 is top left
                        var hp = parseInt(data.robots[k].hp);
                        var speed = parseInt(data.robots[k].speed);
                        var kdr = (name in data.kdr) ? new KDR(data.kdr[name].kill, data.kdr[name].death) : new KDR(0,0);
                        var reloadTime = Math.floor(data.robots[k].reloading_timer);

                        // robot not already added, add and create new robot
                        if (!(name in robots)) {
                            robots[name] = new Robot(name, hp, destinationX, destinationY, 0, 0, speed, kdr);
                        } else {
                            // update robot's positions
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
                            // reloading time
                            if (reloadTime != parseInt(robots[name].reloading_timer)) {
                                reloadingpop[k] = new ReloadingPop(currentX, currentY, reloadTime);
                                robots[name].reloading_timer = reloadTime;
                            }
                            // kdr
                            robots[name].kdr = kdr;
                            robots[name].speed = speed;
                            // reset
                            robots[name].step = MAX_TIME_ROBOT_DEAD;
                        }

                        // stats
                        if (!statsTab) {
                            $('.robot-list').append('<li id="'+name+'"></li>');
                            $('.robot-list li#'+name).html(name+' - HP: '+hp+' - SP: '+ speed + ' - KDR: ' + kdr.kill + '/' + kdr.death);
                        }
                    }
                }
            }
            if (getDataRadar) {
                for (k in data.radar) {
                    if (data.radar.hasOwnProperty(k)) {
                        var radar = data.radar[k];
                        if (!(k in radars)) {
                            radars[k] =
                                new Radar(
                                    radar.xy[0],
                                    1000-radar.xy[1],
                                    radar.distance,
                                    radar.degree,
                                    radar.resolution
                                );
                        }
                    }
                }
                for (k in radars) {
                    if (!(k in data.radar)) {
                        if (radars.hasOwnProperty(k)) {
                            delete radars[k];
                        }
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

    $(document).keydown(function(e) {
        var keyCode = e.keyCode || e.which;
        if (keyCode == 9) {// TAB
            if(!alwaysShowStatsTab) {
                e.preventDefault();
                showStatsTab=true;
            }
        }else if (keyCode == 81 || keyCode == 113) {//q OR Q
            alwaysShowStatsTab = !alwaysShowStatsTab;
        }else if (keyCode == 87 || keyCode == 119) {//w OR W
            drawReloadingPopup = !drawReloadingPopup;
        }else if (keyCode == 69 || keyCode == 101) {//e OR E
            drawDmgPopup = !drawDmgPopup;
        }
    });
    $(document).keyup(function(e) {
        var keyCode = e.keyCode || e.which;
        if (keyCode == 9) {// TAB
            if(!alwaysShowStatsTab) {
                e.preventDefault();
                showStatsTab=false;
            }
        }
    });

    lastTime = Date.now();
    main();
    var updateInterval = setInterval(update, REFRESH_TIME);
});