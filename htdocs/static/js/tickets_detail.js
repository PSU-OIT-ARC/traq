function Timer(onTick){
    var interval = null;
    this.seconds = 0;
    var that = this;

    this.toString = function(){
        var minutes = Math.floor(this.seconds / 60.0)
        var seconds = this.seconds % 60;
        var hours = Math.floor(minutes / 60.0)
        var minutes = minutes % 60;

        if(minutes < 10) minutes = "0" + minutes;
        if(seconds < 10) seconds = "0" + seconds;
        if(hours < 10) hours
        return hours.toString() + ":" + minutes.toString() + ":" + seconds.toString()
    }

    this.start = function(){
        onTick(that)
        interval = setInterval(function(){
            that.seconds++
            onTick(that)
        }, 1000);
    }
}
