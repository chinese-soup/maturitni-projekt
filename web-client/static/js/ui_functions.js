function toggle_center_column(what_to_show)
{	
	if(what_to_show == "center_content_global_settings")
	{
		$("#center_content_message").fadeToggle(500);
		$("#center_content_global_settings").fadeToggle(500);
	}
	else if(what_to_show == "center_content_")
	{

	}
	else
	{
		$("#center_content_message").fadeToggle(500);
		$("#center_content_global_settings").fadeToggle(500);
	}
}

function save_settings(what_settings)
{
	if(what_settings == "global")
	{
		// dummy:
		failed = false; //rename me and remove this declaration

		var dialog = new BootstrapDialog({
			title: 'Global settings',
			buttons: [{
				id: 'btn-1',
				label: 'OK',
				action: function(dialog) {
					dialog.close();
				}
			}]
		});
		dialog.realize();
		dialog.setSize(BootstrapDialog.SIZE_SMALL);
		dialog.open();

		if(failed == false)
		{
			dialog.setMessage("<span style='color: green;'>Settings saved sucessfully.</span>");
			setTimeout(function()
			{
				dialog.close();
			}, 2500);
			$("#center_content_global_settings").fadeToggle(500);
			$("#center_content_message").fadeToggle(500);
		}
		else if(failed == true)
		{
			dialog.setMessage("<span style='color: red;'>Settings failed to save. Reason: %s</span>");
		}
	}
}


function disconnect_dialog(what_server) /* make api calls from here as well??? */
{
	BootstrapDialog.show({
		message: '<span style="color: red">Hi Apple!</span>'
	});
}