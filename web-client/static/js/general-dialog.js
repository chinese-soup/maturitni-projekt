/* THIS FILE DEPENDS ON BOOTSTRAP-DIALOG */

function general_dialog(_title, _message, _result, _timeout) /* make api calls from here as well??? */
{
	    var dialog = new BootstrapDialog({
	    title: _title,
		buttons: [
		{
			label: 'OK',
			action: function(dialog)
			{
				// disconnect
				dialog.close();
			}
		},
		]
	});
	dialog.realize();
	dialog.getModalBody().css("color", "black");
	if(_result == "success")
	{
        dialog.getModalHeader().css("background-color", "#00AA00");
        dialog.getModalHeader().css("color", "white");
	}
	else
    {
        dialog.getModalHeader().css("background-color", "#D12A3F");
        dialog.getModalHeader().css("color", "white");
    }
	dialog.setMessage(_message);
	dialog.open();
}