$.ajaxSetup({
    crossDomain: true,
    xhrFields: {
        withCredentials: true
    }
});

var hostname = location.hostname; // maybe temporary(?): get the current hostname so we know where to make api calls (same host, different port)



/* maybe move to util.js? */
/* overrides the default string function in javascript */
String.prototype.format = function() {
    var formatted = this;
    for (var i = 0; i < arguments.length; i++) {
        var regexp = new RegExp('\\{'+i+'\\}', 'gi');
        formatted = formatted.replace(regexp, arguments[i]);
    }
    return formatted;
};

/* function called upon DOM load */
function onChatLoad()
{
    console.log("onChatLoad();");
    checkIfUserIsLoggedInOnStart();
}


/* never used (yet?) */
$body = $("body");
$(document).on({
    ajaxStart: function() { console.log("ajaxStart();"); /* $body.addClass("loading"); */ },
     ajaxStop: function() { console.log("ajaxStop();");  /* $body.removeClass("loading"); */ }
});


/* target element is in jquery style, TODO: remove? */
function showLoadingMemeCircleInsteadOfTheElement(target_element)
{

}

/* function to time a redirect (for log out, etc.) */
function sendUserAway(url, time)
{
    setTimeout(sendUserAwayTimeout, time, url);
}

/* function called upon sendUserAway time period timing out */
function sendUserAwayTimeout(url)
{
    window.location.href = url;
}

/* call before some commands just to see if the user is still logged in */
/* returns true (loggedin) /false (notloggedin) */
function isUserLoggedIn()
{
    var posting = $.post("http://{0}/check_session".format(hostname), {}, datatype="text");
    posting.done(function(data)
    {
        console.log("Hello");
        if(data["status"] == "ok" && data["reason"])
        {
            return true;
        }

    })

    posting.fail(function(data)
    {
        console.log("Checking user's session failed.");
        return false;
    })

    return false;
}

function checkIfUserIsLoggedInOnStart()
{
    var posting = $.post("http://{0}:5000/upon_login".format(hostname),
    {
    }, dataType="text"
    );

    posting.done(function(data)
    {
        console.log(data);
        if(data["status"] == "error")
        {
            if(data["reason"] == "not_loggedin")
            {
                general_dialog("Access denied: You are not logged in.", data["message"], "error");
                /*sendUserAway("login.html", 3000);*/
                sendUserAway("login.html", 2000);
            }
        }
        else if(data["status"] == "ok")
        {
           if(data["reason"] == "loggedin_email_status")
           {
                //general_dialog("OK", "OK", "success");
                $("#loggedin_email_status").text(data["message"]);
                loadServers();
           }
        }

    });

    posting.fail(function()
    {
         general_dialog("API endpoint error.", "An error occurred while trying to contact the API server.", "error", 2);
    });
}

/* no formatting in js? :( */
function generateServerHTML(serverID)
{
    var html = '<li id="server_{0}" class="left_channels_flex_item server_item">'.format(serverID) +
        '<a href="#"><span class="networkname">Loading..</span> <small class="networkipport">(irc.freenode.org/6667)</small></a>' +
        '<div class="dropdown">' +
            '<button class="btn dropdown-toggle dropdown_server_wheel" type="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">' +
                '<i class="icon-settingsfour-gearsalt"></i>' +
            '</button>' +
            '<ul class="dropdown-menu dropdown-menu-right">' +
                '<li><a class="join_another_channel_link" href="#">Join another channel&hellip;</a></li>' + /*join_channel_dialog(\'Freenode\',\'ID\' ); */
                '<li><a class="disconnect_link">Disconnect</a></li>' + /* disconnect_dialog(\'Freenode\', \'ID\');*/
                '<li role="separator" class="divider"></li>' +
                '<li><a class="remove_server_link">Remove this server</a></li>' +
                '<li><a class="edit_server_link">Edit</a></li>' +
            '</ul>' +
        '</div>' +
        '<ul class="channels_ul"></ul>'
    '</li>';
    return(html);
}

function generateChannelHTML(channelID)
{
    var html =  '<li id="channel_{0}" class="left_channels_flex_item channel_item">'.format(channelID) +
                '   <a href="#" class="channelName">#channelName</a>' +
                '</li>';
    return(html);
}


/* function to reload the server and channel list */
/* called when servers or channels are changed/added/removed */
/* called when user first loads chat.html */
/* NOT CALLED when a channel has new activity */
function loadServers()
{
    console.log("loadServers();");
    $(".left_channels_flex_container .loading-ajax").show(); // hide the loading servers icon
    $(".left_channels_flex_container .loading-ajax-message").hide();

    $(".channel_list").empty(); // clear the server list so we don't dupe the server entries (beware of element id hazard)

    var posting = $.post("http://{0}:5000/get_server_list".format(hostname),
    {
    }, dataType="text"
    );

    posting.done(function(data)
    {
        if(data["reason"] == "listing_servers")
        {
            console.log(data["message"][0]);
            servers = data["message"];

            for (key in servers)
            {
                value = servers[key];
                serverID = servers[key]["serverID"];
                serversessionID = servers[key]["serversessionID"];
                serverName = servers[key]["serverName"];
                serverIP =  servers[key]["serverIP"];
                serverPort = servers[key]["serverPort"];
                useSSL = servers[key]["useSSL"];
                channels = servers[key]["channels"];

                $(".channel_list").append(generateServerHTML(serverID));  // generate a dummy <li> list and append it to the server list
                $(".left_channels_flex_container .loading-ajax").hide(); // hide the loading servers icon
                $(".channel_list #server_" + serverID + " .networkname").html(serverName);

                /* onclick definitions, very important, do NOT mess up ARGUMENTS FOR EACH FUNCTION ALWAYS HAVE TO BE (SERVERNAME, SERVERID)*/
                console.log(serverID);

                //$(".channel_list #server_{0} .dropdown .dropdown-menu .join_another_channel_link".format(serverID)).on("click", {serverName: serverName, serverID}, join_channel_dialog);
                //$(".channel_list #server_{0} .dropdown .dropdown-menu .disconnect_link".format(serverID)).on("click", {serverName: serverName, serverID: serverID,  });
                //$(".channel_list #server_{0} .dropdown .dropdown-menu .remove_server_link".format(serverID)).on("click", remove_server_dialog(serverName, serverID));
                $(".channel_list #server_{0} .dropdown .dropdown-menu .edit_server_link".format(serverID)).click({serverName:serverName, serverID:serverID, isAnEdit: true}, edit_server);

                for (chans in channels)
                {
                    channelID = channels[chans]["channelID"];
                    channelName = channels[chans]["channelName"];
                    isJoined = channels[chans]["isJoined"];
                    lastOpened = channels[chans]["lastOpened"];
                    channelServerID = channels[chans]["serverID"];

                    $(generateChannelHTML(channelID)).insertAfter($(".channel_list #server_{0}".format(channelServerID)));  // generate a dummy <li> list and append it to the server list
                    $(".channel_list #channel_{0} .channelName".format(channelID)).html(channelName);

                }

                if(useSSL == 0)
                    $(".channel_list #server_{0} .networkipport".format(serverID)).html("({0}/{1})".format(serverIP, serverPort));
                else
                    $(".channel_list #server_{0} .networkipport".format(serverID)).html("({0}/{1}/SSL)".format(serverIP, serverPort));
            }
        }
        else if(data["reason"] == "no_servers_to_list")
        {
            $(".left_channels_flex_container .loading-ajax").hide(); // hide the spinning wheel
            $(".left_channels_flex_container .loading-ajax-message").show(); // show the div with the message below
            $(".left_channels_flex_container .loading-ajax-message").html("No servers to be listed (yet).<br>Use the <strong>Join another server</strong> option.");
        }
        else if(data["reason"] == "not_loggedin")
        {
            $(".left_channels_flex_container .loading-ajax").hide(); // hide the spinning wheel
            $(".left_channels_flex_container .loading-ajax-message").show();// show the div with the message below
            $(".left_channels_flex_container .loading-ajax-message").html("You are not logged in.");
        }


    });

    posting.fail(function()
    {
        console.log("Failed to load servers.")
    })
}
/*toggle_center_column(\'edit_server\');*/
/* isAnEdit  =  a boolean value deciding if we are adding a new server or not */
function edit_server(event)
{
    serverName = event.data.serverName;
    serverID = event.data.serverID;
    isAnEdit = event.data.isAnEdit;

    console.log("edit_server({0}, {1}, {2})".format(serverName, serverID, isAnEdit));
    toggle_center_column("edit_server");

    $("#save_server_settings").html("<i class='icon-check'></i> Save changes LOL");
    $("#save_server_settings").click({serverID:serverID}, save_server);

    var posting = $.post("http://{0}:5000/get_server_settings".format(hostname),
    {
        serverID: serverID
    },  dataType="text"
    );

    posting.done(function(data)
    {
        if(data["reason"] == "listing_server_info")
        {
            console.log(data["message"][0]);
            settings = data["message"];
            console.log(settings);

            $("#server-edit-form #server_edit_nickname").val(settings[2]);
            $("#server-edit-form #server_edit_label").val(settings[6]);
            $("#server-edit-form #server_edit_ip").val(settings[7]);
            $("#server-edit-form #server_edit_portno").val(settings[8]);
            $("#server-edit-form #use_tls_ssl_checkbox").prop("checked", Boolean(settings[9]));
            $("#server-edit-form #server_edit_password").val(settings[10]);
        }

    });

    posting.fail(function()
    {
        general_dialog("API endpoint error.", "An error occurred while trying to retrieve this server's global settings.", "error", 2);
        toggle_center_column("messages"); // show the messages window instead of global settings, because we can't load user's settings
        console.log("Failed to load servers.");
    })

}

function save_server(event)
{
    /*{"serverName":"", "nickname":"", "serverPassword":"", "serverIP":"", "serverPort":"", "useSSL":""*/
    serverName = $("#server-edit-form #server_edit_label").val();
    nickname = $("#server-edit-form #server_edit_nickname").val();
    serverPassword = $("#server-edit-form #server_edit_password").val();
    serverIP = $("#server-edit-form #server_edit_ip").val();
    serverPort = $("#server-edit-form #server_edit_portno").val();
    useSSL = Boolean($("#server-edit-form #use_tls_ssl_checkbox").prop("checked"));

    serverID = event.data.serverID;
    console.log("SERVERID=" + serverID);

    var posting = $.post("http://{0}:5000/edit_server_settings".format(hostname),
    {
        serverID: serverID,
        serverName: serverName,
        nickname: nickname,
        serverPassword: serverPassword,
        serverIP: serverIP,
        serverPort: serverPort,
        useSSL: useSSL

    }, dataType="text"
    );

    posting.done(function(data)
    {
        console.log(data);
        if(data["status"] == "error")
        {
            general_dialog("Server settings", data["message"], "error", 2);
        }
        else if(data["status"] == "ok")
        {
           if(data["reason"] == "server_settings_edited_successfully")
           {
                general_dialog("Server settings", data["message"], "ok", 2);
                /* TODO: CALL RECONNECT from HERE */
                /* TODO: CALL RECONNECT from HERE */
                toggle_center_column("edit_server");
           }
           else if(data["reason"] == "server_settings_not_edited")
           {
                general_dialog("Server settings", data["message"], "ok", 2);

                toggle_center_column("edit_server");
           }
        }

    });

    posting.fail(function()
    {
         general_dialog("API endpoint error.", "An error occurred while trying to contact the API server.", "error", 2);
    });
}

function add_server()
{
    $("#save_server_settings").html("<i class='icon-check'></i> Add a new server");
    /* clear the fields cuz they could be set to some stuff becasue of editing a server before */
    $("#server-edit-form #server_edit_nickname").val("");
    $("#server-edit-form #server_edit_password").val("");
    $("#server-edit-form #server_edit_label").val("");
    $("#server-edit-form #server_edit_ip").val("");
    $("#server-edit-form #server_edit_portno").val("");
    $("#server-edit-form #use_tls_ssl_checkbox").prop("checked", Boolean(false));
    toggle_center_column("edit_server");

}


function loadSettingsIntoInputs()
{
    console.log("loadSettingsIntoInputs();")
    var posting = $.post("http://{0}:5000/get_global_settings".format(hostname),
    {
    }, dataType="text"
    );

    posting.done(function(data)
    {
        if(data["reason"] == "listing_settings")
        {
            console.log(data["message"][0]);
            settings = data["message"][0];
            console.log(settings);

            $("#global-settings-form #hilight_words_input").val(settings[0]);
            $("#global-settings-form #username").val(settings[1]);
            $("#global-settings-form #realname").val(settings[2]);
            $("#global-settings-form #nickname").val(settings[3]);
            $("#global-settings-form #show_joinpartquit_messages").prop("checked", Boolean(settings[4]));
            $("#global-settings-form #show_seconds_checkbox").prop("checked", Boolean(settings[5]));
            $("#global-settings-form #show_video_previews_checkbox").prop("checked", Boolean(settings[6]));
            $("#global-settings-form #show_image_previews_checkbox").prop("checked", Boolean(settings[7]));
        }

    });

    posting.fail(function()
    {
        general_dialog("API endpoint error.", "An error occurred while trying to retrieve your account's global settings.", "error", 2);
        toggle_center_column("messages"); // show the messages window instead of global settings, because we can't load user's settings
        console.log("Failed to load servers.");
    })
}

function save_global_settings()
{
    console.log($("#global-settings-form input[id=hilight_words_input]").val());
    var posting = $.post("http://{0}:5000/save_global_settings".format(hostname),
    {
       /* WARNING: order and names of the data items here matter for the API as it uses the order to insert it into the database */
       highlight_words: $("#global-settings-form input[id=hilight_words_input]").val(),
       whois_username: $("#global-settings-form input[id=username]").val(),
       whois_realname: $("#global-settings-form input[id=realname]").val(),
       global_nickname: $("#global-settings-form input[id=nickname]").val(),
       show_joinpartquit_messages: $("#global-settings-form input[id=show_joinpartquit_messages]").prop("checked"),
       show_seconds: $("#global-settings-form input[id=show_seconds_checkbox]").prop("checked"),
       show_video_previews: $("#global-settings-form input[id=show_video_previews_checkbox]").prop("checked"),
       show_image_previews: $("#global-settings-form input[id=show_image_previews_checkbox]").prop("checked")
    }, dataType="text"
    );

    posting.done(function(data)
    {
        console.log(data);
        //global-settings-form
        if(data["status"] == "ok")
        {
            general_dialog("Global settings", data["message"], data["status"], 2);
            if(data["reason"] == "global_settings_saved")
            {
                toggle_center_column("messages");

            }
            else if(data["reason"] == "global_settings_notupdated")
            {
                toggle_center_column("messages");
            }
        }
        else if(data["status"] == "error")
        {
            if(data["reason"] == "not_loggedin")
            {
                general_dialog("Access denied: You are not logged in.", data["message"], "error", 2);
            }
        }
    })

    posting.fail(function(data)
    {
        general_dialog("API endpoint error.", "An error occurred while trying to contact the API server.", "error", 2)
    })
}


function logout()
{
   var posting = $.post("http://{0}:5000/logout".format(hostname),
    {
    }, dataType="text"
    );

    posting.done(function(data)
    {
        console.log(data);
        if(data["status"] == "error")
        {
            if(data["reason"] == "not_loggedin")
            {
                general_dialog("Couldn't log you out. I don't think you are logged in.", data["message"], data["status"]);
                sendUserAway("login.html", 4000);
            }
        }
        else if(data["status"] == "ok")
        {
           if(data["reason"] == "loggedout")
           {
                general_dialog("Logged out successfully.", data["message"], data["status"]);
                sendUserAway("login.html", 500);
           }
        }

    });

    posting.fail(function()
    {
         general_dialog("API endpoint error.", "An error occurred while trying to contact the API server.", "error", 2);
    });
}


