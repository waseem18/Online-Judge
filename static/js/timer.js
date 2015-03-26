start_time = getTimer();
countdown = 7200000;
onEnterFrame = function () {
	elapsed_time = getTimer()-start_time;
	_root.count.text = time_to_string(elapsed_time);
	_root.count_down.text = time_to_string(_root.countdown-elapsed_time);
};
function time_to_string(time_to_convert) {
	elapsed_hours = Math.floor(time_to_convert/3600000);
	remaining = time_to_convert-(elapsed_hours*3600000);
	elapsed_minutes = Math.floor(remaining/60000);
	remaining = remaining-(elapsed_minutes*60000);
	elapsed_seconds = Math.floor(remaining/1000);
	remaining = remaining-(elapsed_seconds*1000);
	elapsed_fs = Math.floor(remaining/10);
	if (elapsed_hours<10) {
		hours = "0"+elapsed_hours.toString();
	} else {
		hours = elapsed_hours.toString();
	}
	if (elapsed_minutes<10) {
		minutes = "0"+elapsed_minutes.toString();
	} else {
		minutes = elapsed_minutes.toString();
	}
	if (elapsed_seconds<10) {
		seconds = "0"+elapsed_seconds.toString();
	} else {
		seconds = elapsed_seconds.toString();
	}
	if (elapsed_fs<10) {
		hundredths = "0"+elapsed_fs.toString();
	} else {
		hundredths = elapsed_fs.toString();
	}
	return hours+":"+minutes+":"+seconds+":"+hundredths;
}