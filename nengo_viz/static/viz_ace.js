
VIZ.Ace = function (args, script_code) {
	this.hidden = false;
	this.ws = VIZ.create_websocket(42) //to be args.uid
	var code_div = document.createElement('div')
	code_div.id = 'editor'
	document.getElementsByTagName("BODY")[0].appendChild(code_div);
	var editor = ace.edit('editor')
	editor.setTheme('ace/theme/monokai')
	editor.getSession().setMode("ace/mode/python");

	editor.setValue('texxxxxxxxxxxxxxxxxxxxxxxtt\nHiodsahfjiodsjfio');

	var bottom_margin = $(sim.div).height();
	console.log(bottom_margin);

	var left_margin = $(window).width()
	console.log(left_margin);
	code_div.style.bottom = bottom_margin;
	code_div.style.left = left_margin * 4 / 5
}

VIZ.Ace.prototype.show_editor = function () {
	var editor = document.getElementById('editor');
	editor.style.display = 'block';
	this.hidden = false;
}

VIZ.Ace.prototype.hide_editor = function () {
	var editor = document.getElementById('editor');
	editor.style.display = 'none';
	this.hidden = true;
}

VIZ.Ace.prototype.toggle_shown = function () {
	if (this.hidden) {
		this.show_editor();
	}
	else{
		this.hide_editor();
	}
}

setInterval(function(){gg.toggle_shown()}, 1000)