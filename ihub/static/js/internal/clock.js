// main function
function dutyClock(serverNow, duty_end){
    var t = getDateTime(duty_end) - getDateTime(serverNow);
    var clientEnd = new Date().getTime() + t;
    var displayElem = $(".timer-display");

    var x = setInterval(function(){
        let clientNow = new Date().getTime();
        let _t = clientEnd - clientNow;

        // stop when timer's up
        if(_t <= 0.0){
            clearInterval(x);
            displayElem.html(`EXPIRED`);
            return;
        };

        // duration time parsing
        let {hours, minutes, seconds} = durationToRepresentation(_t);
        [hours, minutes, seconds] = [hours, minutes, seconds].map(
            num => twoMoreDigitInt(num)
        );

        // display
        let displayed_countdown = `${hours}:${minutes}:${seconds}`;
        displayElem.html(displayed_countdown);
    });
}


function twoMoreDigitInt(n){
    return n > 9 ? "" + n: "0" + n;
}

function durationToRepresentation(duration){
    var hours = Math.floor((duration % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    var minutes = Math.floor((duration % (1000 * 60 * 60)) / (1000 * 60));
    var seconds = Math.floor((duration % (1000 * 60)) / 1000);
    
    return {
        hours: hours,
        minutes: minutes,
        seconds: seconds
    }
};

function getDateTime(datetime){
    const [date, time] = datetime.split(" ")
    const [mon, day, year] = date.split("/").map(e=>parseInt(e, 10));
    const [hour, min, sec] = time.split(":").map(e=>parseInt(e, 10));;
    var result = new Date(
        year, mon-1, day,
        hour, min, sec
    );
    return result
};
