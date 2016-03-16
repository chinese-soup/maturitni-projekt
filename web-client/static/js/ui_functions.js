/* THIS FILE DEPENDS ON bootstrap-dialog */

function toggle_center_column(what_to_show)
{	
	if(what_to_show == "global_settings")
	{
		$("#center_content_message").hide();
		$("#center_content_edit_server").hide();
		$("#center_content_global_settings").fadeIn(300);
		$("#center_content_join_channel").hide();
		console.log("what_to_show = global_setting done");
		loadSettingsIntoInputs();
	}
	else if(what_to_show == "edit_server")
	{
		$("#center_content_message").hide();
		$("#center_content_global_settings").hide();
		$("#center_content_edit_server").fadeIn(300);
		$("#center_content_join_channel").hide();
		console.log("what_to_show = edit_server done");
	}
	else if(what_to_show == "join_channel")
	{
	    $("#center_content_message").hide();
		$("#center_content_global_settings").hide();
		$("#center_content_edit_server").hide();
        $("#center_content_join_channel").fadeIn(300);
        console.log("what_to_show = join_channel done");
	}
	else
	{
		$("#center_content_message").fadeIn(300);
		$("#center_content_edit_server").hide();
		$("#center_content_global_settings").hide();
		$("#center_content_join_channel").hide();
		console.log("what_to_show = messages done");
	}
}

function on_load()
{
	// hack hack, hide the wheels next to servers
	$(".dropdown_server_wheel").css("display", "none");
}

/*function save_settings(didSuccess)
{
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

    if(didSuccess == false)
    {
        dialog.setMessage("<span style='color: green;'>Settings saved sucessfully.</span>");
        setTimeout(function()
        {
            dialog.close();
        }, 2500);

    }
    else if(failed == true)
    {
        dialog.setMessage("<span style='color: red;'>Settings failed to save. Reason: %s</span>");
    }
}*/

function disconnect_dialog(what_server) /* make api calls from here as well??? */
{
	    var dialog = new BootstrapDialog({
	    title: 'Disconnecting from ' + what_server,
		buttons: [
		{
			label: 'Disconnect',
			action: function(dialog)
			{
				// disconnect
				dialog.close();
			}
		},
		{
			label: 'Cancel',
			action: function(dialog)
			{
				dialog.close();
			}
		}
		]
	});
	dialog.realize();
	dialog.getModalBody().css("color", "red");
	dialog.setMessage("Are you sure you want to disconnect from '" + what_server + "'?")
	dialog.open()

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
    dialog.getModalBody().css("padding", "0");
	dialog.getModalHeader().hide();
	dialog.getModalFooter().css("background-color", "transparent");
	dialog.open();
}