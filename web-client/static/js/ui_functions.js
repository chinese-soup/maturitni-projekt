function toggle_center_column(what_to_show)
{	
	if(what_to_show == "center_content_global_settings")
	{
		$("#center_content_message").slideToggle(300);
		$("#center_content_global_settings").toggle();
	}
	else if(what_to_show == "center_content_")
	{

	}
	else
	{
		$("#center_content_message").slideToggle(300);
		$("#center_content_global_settings").toggle();
	}
}

function join_another_channel(server)
{

}

function on_load()
{
	// hack hack, hide  the wheels next to servers
	$(".dropdown_server_wheel").css("display", "none");
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
			$("#center_content_global_settings").slideToggle(500)
			$("#center_content_message").toggle();
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

function preview_images(url)
{
	var dialog = new BootstrapDialog({
		title: 'Image preview',
		buttons: [
		{
			label: 'Open image URL',
			action: function(dialog)
			{
				dialog.close();
				window.open(url, "_blank");
			}
		},
		{
			label: 'Close',
			action: function(dialog)
			{
				dialog.close();
			}
		}
		]
	});
	dialog.realize();
	dialog.setSize(BootstrapDialog.SIZE_WIDE);
	dialog.setMessage("<img class='img-responsive' src=" + url + ">")
	dialog.open();
}