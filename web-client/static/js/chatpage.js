$.ajaxSetup({
    crossDomain: true,
    xhrFields: {
        withCredentials: true
    }
});


// Global variables
var hostname = location.hostname; // maybe temporary(?): get the current hostname so we know where to make api calls (same host, different port)
var already_loaded_backlog = [];
var global_settings = {"hilight_words": null, "username": null, "realname": null, "nickname": null, "show_joinpartquit_messages": null, "show_seconds": null, "show_video_previews": null, "show_image_previews": null};


/* maybe move to util.js? */
/* overrides the default string function in javascript to include formatting support */
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
    loadSettingsIntoVariable();
    //setTimeout(ping, 1000);
}

function loadSettingsIntoVariable()
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


            global_settings["hilight_words"] = settings[0];
            global_settings["username"] = settings[1];
            global_settings["realname"] = settings[2];
            global_settings["nickname"] = settings[3];
            global_settings["show_joinpartquit_messages"] = Boolean(settings[4]);
            global_settings["show_seconds"] = Boolean(settings[5]);
            global_settings["show_video_previews"] = Boolean(settings[6]);
            global_settings["show_image_previews"] = Boolean(settings[7]);

        }
        else if(data["reason"] == "not_loggedin")
        {
            general_dialog("Access denied: You are not logged in.", data["message"], "error", -1);
        }
    });

    posting.fail(function()
    {
        //general_dialog("API endpoint error.", "An error occurred while trying to retrieve your account's global settings.", "error", 2);
        toggle_center_column("messages"); // show the messages window instead of global settings, because we can't load user's settings
        log("Could not load global settings.")
    })
}

function ping()
{
    log(isUserLoggedIn);
    setTimeout(ping, 1000);
}

/* never used (yet?) */
$body = $("body");

$(document).on({
    ajaxStart: function() { /*console.log("ajaxStart();"); */ /* $body.addClass("loading"); */ },
     ajaxStop: function() { /*console.log("ajaxStop();");  */ /* $body.removeClass("loading"); */ }
});

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
    var posting = $.get("http://{0}:5000/check_session".format(hostname), {}, datatype="text");
    var result = false;

    posting.done(function(data)
    {
        if(data["status"] == "ok" && data["reason"] == "alive_loggedin")
        {
            result = true;
        }
        else if(data["status"] == "error" && data["reason"] == "alive_not_loggedin")
        {
            result = false;
        }

    })

    posting.fail(function(data)
    {
        console.log("Checking user's session failed.");
        result = false;
    })

    return(result);

}

function addJoinPartQuitToChannel(messageID, timestamp, messageType, sender, message, channelID)
{
    if(show_joinpartquit_messages == true)
    {
        log("hello", messageID, timestamp, messageType, sender, message, channelID);
    }
}


function addMessageToChannel(messageID, timestamp, sender, senderColor, message, channelID)
{
    var html =
    '<div class="log_message log_message_even">' +
    '    <span class="timestamp">{0}</span>'.format(timestamp) +
    '    <span class="message-body"><span class="message-sender message-sender-{0}">{1}</span>: {2}</span>'.format(senderColor, sender, message) +
    '</div>';


    var element = $("#channel_window_{0}".format(channelID));
    element.append(html);

    var element2 = $(".center_messages_container");
    element.scrollTop(element2.scrollHeight); // scrollneme dolů, protože máme nové
}


function switchCurrentChannel(toChannelID)
{
    $(".message_window").hide();
    $("#channel_window_{0}".format(toChannelID)).show();
}

function linkifyMessage(messageBody)
{
    var regexp = /(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig;

    return messageBody.replace(regexp, function(url)
    {
        if(global_settings["show_image_previews"])
        {
            return("<span class=\"message-image-preview\"><a href=\"#\" onclick=\"preview_images('{0}');\"><img alt=\"Image preview\" title=\"Image\" src=\"{0}\" target=\"_blank\"></a></span>".format(url));
        }
        else if(global_settings[""])
        {

        }
    });
}



function switchCurrentChannelEventStyle(event)
{
    toChannelID = event.data.channelID;
    toChannelName = event.data.channelName;
    console.log("Orange juice: ");
    console.log(toChannelID);

    log("Switching channel window to {0} ({1})".format(toChannelID, toChannelName));

    $(".message_window").hide();
    $("#channel_window_{0}".format(toChannelID)).show();
    $(".channel_item".format(toChannelID)).toggleClass("channel_item_focused", false); // defocus any previously focused window
    $("#channel_{0}".format(toChannelID)).toggleClass("channel_item_focused", true);
    $(".header_room_name").html("{0} <small>({1} @ {2})</small>".format(toChannelName, toChannelID, "FIXME"))


    /* load backlog if it has not been loaded yet */
    if($.inArray(toChannelID, already_loaded_backlog) == -1)
    {
        console.log("Getting backlog");
        getBacklogForChannel(toChannelID, 50);
    }
    else
    {
        console.log("NOT getting backlog");

    }

}

function convertDBTimeToLocalTime(dbUTCtime)
{
    var date = new Date(dbUTCtime);
    var date_now = new Date();


    if(date.toLocaleDateString() ==  date_now.toLocaleDateString()) // zkontrolujeme, jestli daný čas je dnes, pokud ne, vrátíme i datum
    {
        var local_date = date.toLocaleTimeString();
    }
    else
    {
        var local_date = date.toLocaleString();
    }


    return(local_date);
}

function getNicknameFromHostmask(hostmask)
{
    var regexp = /(.*)\!(~{0,1}.*)\@(.*)/;
    var asdf = hostmask.match(regexp)[1];
    if(asdf == null)
    {
        return("null");
    }
    else
    {
        return(asdf);
    }

}

function getBacklogForChannel(channelID, limit)
{
    var posting = $.post("http://{0}:5000/get_messages".format(hostname),
    {
       channelID: channelID,
       limit: limit,
       backlog: true
    }, dataType="text"
    );

    posting.done(function(data)
    {
        console.log(data);
        log(data["reason"], data["status"]);

        if(data["status"] == "error")
        {
            if(data["reason"] == "not_loggedin")
            {
                log(data["reason"]);
            }
        }
        else if(data["status"] == "ok")
        {
           if(data["reason"] == "listing_messages")
           {
                log(data["message"]);
                console.log(data["message"]);

                var messages = data["message"];

               	for (var i=0; i < messages.length; i++)
                {
                    log(i);
                    if(messages[i]["commandType"] == "PRIVMSG" || messages[i]["commandType"] == "PUBMSG")
                    {
                        addMessageToChannel(
                            messages[i]["messageID"],
                            convertDBTimeToLocalTime(messages[i]["timeReceived"]),
                            getNicknameFromHostmask(messages[i]["fromHostmask"]),
                            "ok",
                            linkifyMessage(messages[i]["messageBody"]),
                            messages[i]["IRC_channels_channelID"]
                        );
                    }
                    else if(messages[i]["commandType"] == "JOIN" || messages[i]["commandType"] == "QUIT" || messages[i]["commandType"] == "JOIN")
                    {
                        // messageID, timestamp, messageType, sender, message, channelID)
                        addJoinPartQuitToChannel(
                            messages[i]["messageID"],
                            convertDBTimeToLocalTime(messages[i]["timeReceived"]),
                            messages[i]["commandType"],
                            messages[i]["fromHostmask"],
                            messages[i]["messageBody"],
                            messages[i]["IRC_channels_channelID"]
                        );
                    }
                }

                if($.inArray(channelID, already_loaded_backlog) == -1)
                {
                    already_loaded_backlog.push(channelID);
                }
                else
                {
                    log("not adding to the meme array (that is only temporary and needs a proper fix) because it already is in there");
                }
           }
        }

    });

    posting.fail(function()
    {
         general_dialog("API endpoint error.", "An error occurred while trying to contact the API server. Try reloading the page.", "error", 3);
         log("An error occurred while trying to contact the API server. Try reloading the page.", "error");
    });
}



// used for the status log window, not for actual IRC messages
// src: http://stackoverflow.com/questions/18229022/how-to-show-current-time-in-javascript-in-the-format-hhmmss
function getCurrentTimestamp()
{
    var time = new Date();
    return (("0" + time.getHours()).slice(-2)   + ":" +
    ("0" + time.getMinutes()).slice(-2) + ":" +
    ("0" + time.getSeconds()).slice(-2));

}

function log(message, status)
{
    var color = 2;
    if(status == "error")
    {
        color = 3;
    }
    addMessageToChannel(-1, getCurrentTimestamp(), "CloudChat", color, message, -1);
}


/* called upon loading the page, because the way this shit works is disgusting */
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
                log("You are logged in, loading server list.", "ok");
                loadServers();
           }
        }

    });

    posting.fail(function()
    {
         general_dialog("API endpoint error.", "An error occurred while trying to contact the API server. Try reloading the page.", "error", 3);
         log("An error occurred while trying to contact the API server. Try reloading the page.", "error");
         sendUserAway("login.html", 5000);
    });
}



/* generates HTML for a hidden window for a channel */
function generateChannelWindow(channelID)
{
    var html = '<span class="message_window" id="channel_window_{0}" style="display: none;"></span>'.format(channelID);
    return(html);
}

function removeChannelWindow(channelID)
{
    switchCurrentChannel(-1); // switch to the status window before removing current channel
    $("#channel_window_{0}".format(channelID)).remove();
}


function generateServerHTML(serverID)
{
    var html = '<li id="server_{0}" class="left_channels_flex_item server_item">'.format(serverID) +
        '<a class="network_name_link" href="#"><span class="networkname">Loading..</span> <small class="networkipport">(irc.freenode.org/6667)</small></a>' +
        '<div class="dropdown">' +
            '<button class="btn dropdown-toggle dropdown_server_wheel" type="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">' +
                 '<i class="icon-settingsfour-gearsalt"></i>' +
            '</button>' +
            '<ul class="dropdown-menu dropdown-menu-right">' +
                '<li><a class="join_another_channel_link" href="#">Join another channel&hellip;</a></li>' + /* join_channel_dialog(\'Freenode\',\'ID\' ); */
                '<li><a class="disconnect_link">Disconnect</a></li>' + /* disconnect_dialog(\'Freenode\', \'ID\');*/
                '<li role="separator" class="divider"></li>' +
                '<li><a class="remove_server_link">Remove this server</a></li>' +
                '<li><a class="edit_server_link">Edit</a></li>' +
            '</ul>' +
        '</div>' +
        '<ul class="channels_ul"></ul>' +
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


// initialiaze the join channel form and stuff
function join_channel_dialog(event)
{
    serverID = event.data.serverID;
    serverName = event.data.serverName;
    toggle_center_column("join_channel");

    // empty fields
    $("#channel-join-form #channel_to_join_input_channel").val("");
    $("#channel-join-form #channel_to_join_input_password").val("");
    $("#channel-join-form #channel_to_join_submit_button").one("click", {serverName:serverName, serverID:serverID}, join_channel);
    console.log("join_channel_dialog();");
}


/* actually call to join the channel */
function join_channel(event)
{
    console.log("join_channel();");
    serverID = event.data.serverID;
    serverName = event.data.serverName;
    channelName = $("#channel-join-form #channel_to_join_input_channel").val();
    channelPassword = $("#channel-join-form #channel_to_join_input_password").val();

    toggle_center_column("messages");

    var posting = $.post("http://{0}:5000/add_channel".format(hostname),
    {
        serverID: serverID,
        channelName: channelName,
        channelPassword: channelPassword

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
           if(data["reason"] == "channel_added_sucessfully")
           {
                general_dialog("Server settings", data["message"], "ok", 2);
                /* TODO: call join from here */
                /* TODO: call join from here */
                toggle_center_column("messages");
                loadServers();
           }
           else if(data["reason"] == "channel_was_not_added")
           {
                general_dialog("Channel added", data["message"], "ok", 2);
                toggle_center_column("messages");
           }
        }

    });

    posting.fail(function()
    {
         general_dialog("API endpoint error.", "An error occurred while trying to contact the API server.", "error", 2);
         log("An error occurred while trying to contact the API server. Try reloading the page.", "error");
    });


    // empty fields


}


/* function to reload the server and channel list */
/* called when servers or channels are changed/added/removed */
/* called when user first loads chat.html */
/* NOT CALLED when a channel has new activity */
function loadServers()
{
    console.log("loadServers();");
    log("loadServers();")
    $(".left_channels_flex_container .loading-ajax").show(); // hide the loading servers icon
    $(".left_channels_flex_container .loading-ajax-message").hide(); // hide the "you have no servers" message

    $(".channel_list").empty(); // clear the server list so we don't dupe the server entries (beware of element id hazard)

    var posting = $.post("http://{0}:5000/get_server_list".format(hostname),
    {
    }, dataType="text"
    );

    posting.done(function(data)
    {
        log(data["reason"], data["status"]);
        if(data["reason"] == "listing_servers")
        {
            console.log(data["message"][0]);
            servers = data["message"];

            for (key in servers)
            {
                var serverID = servers[key]["serverID"];

                var serversessionID = servers[key]["serversessionID"];
                var serverName = servers[key]["serverName"];
                var serverIP =  servers[key]["serverIP"];
                var serverPort = servers[key]["serverPort"];
                var useSSL = servers[key]["useSSL"];
                var channels = servers[key]["channels"];
                console.log("Channels:");
                console.log(channels);
                console.log(channels.length);

                // TODO: IMPLEMENT iSCONNECTED

                $(".channel_list").append(generateServerHTML(serverID));  // generate a dummy <li> list and append it to the server list
                $(".left_channels_flex_container .loading-ajax").hide(); // hide the loading servers icon
                $(".channel_list #server_{0} .networkname".format(serverID)).html(serverName); // set the network name of the server

                log(serverID, "ok");

                //$(".channel_list #server_{0} .dropdown .dropdown-menu .disconnect_link".format(serverID)).on("click", {serverName: serverName, serverID: serverID,  });
                //$(".channel_list #server_{0} .dropdown .dropdown-menu .remove_server_link".format(serverID)).on("click", remove_server_dialog(serverName, serverID));
                $(".channel_list #server_{0} .dropdown .dropdown-menu .edit_server_link".format(serverID)).click({serverName:serverName, serverID:serverID, isAnEdit: true}, edit_server);
                $(".channel_list #server_{0} .dropdown .dropdown-menu .join_another_channel_link".format(serverID)).click({serverName:serverName, serverID:serverID}, join_channel_dialog);
                $(".channel_list #server_{0} .network_name_link".format(serverID)).click({channelID:-1, channelName:"Status window"}, switchCurrentChannelEventStyle); // causes the server headers to link to the main status window


                if(useSSL == 0)
                    $(".channel_list #server_{0} .networkipport".format(serverID)).html("({0}/{1})".format(serverIP, serverPort));
                else
                    $(".channel_list #server_{0} .networkipport".format(serverID)).html("({0}/{1}/SSL)".format(serverIP, serverPort));


                for (var chans = 0; chans < channels.length; chans++)
                {
                    console.log("CHEN");
                    console.log(channels["chan"]);
                    var channelID = channels[chans]["channelID"];
                    log(channelID);
                    var channelName = channels[chans]["channelName"];
                    var isJoined = channels[chans]["isJoined"];
                    var lastOpened = channels[chans]["lastOpened"];
                    var channelServerID = channels[chans]["serverID"];

                    console.log("Channel");
                    console.log(chans);

                    $(generateChannelHTML(channelID)).insertAfter($(".channel_list #server_{0}".format(channelServerID)));  // generate a dummy <li> list and append it to the server list
                    $(".channel_list #channel_{0} .channelName".format(channelID)).html(channelName);

                    $(generateChannelWindow(channelID)).insertAfter($(".message_window".format(channelServerID)));
                    already_loaded_backlog = []; // CLEAR ALL MEMES

                    /* bind a click event to a channel in teh channel list*/
                    $(".channel_list #channel_{0} .channelName".format(channelID)).click(
                    {channelID:channelID, channelName:channelName, lastOpened: lastOpened, channelServerID:channelServerID},
                    switchCurrentChannelEventStyle)
                }
            }
            $(".dropdown_server_wheel").css("display", "flex");

            $(".dropdown_server_wheel").css("width", "10px");
        }
        else if(data["reason"] == "no_servers_to_list")
        {
            $(".left_channels_flex_container .loading-ajax").hide(); // hide the spinning wheel
            $(".left_channels_flex_container .loading-ajax-message").show(); // show the div with the message below
            $(".left_channels_flex_container .loading-ajax-message").html("No servers to be listed at the moment.<br>Use the <strong>Join another server</strong> option.");
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

        console.log("Failed to load servers.");
        log("Failed to load servers.");
    })
}
/*toggle_center_column(\'edit_server\');*/
/* isAnEdit  =  a boolean value deciding if we are adding a new server or not */
function edit_server(event)
{
    serverName = event.data.serverName;
    serverID = event.data.serverID;
    isAnEdit = event.data.isAnEdit;

    console.log("edit_server({0}, {1}, {2});".format(serverName, serverID, isAnEdit));
    log("edit_server({0}, {1}, {2});".format(serverName, serverID, isAnEdit));
    toggle_center_column("edit_server");

    $("#save_server_settings").html("<i class='icon-check'></i> Save changes"); /* just to be sure, as it could be Add server from before */
    $("#save_server_settings").one("click", {serverID:serverID}, save_server); /* change onClick event for the save button so that we know what server we are editing */

    $(".header_room_topic .header_room_topic_server_label").html(serverName);

    var posting = $.post("http://{0}:5000/get_server_settings".format(hostname),
    {
        serverID: serverID
    },  dataType="text"
    );

    posting.done(function(data)
    {
        log(data["reason"], data["status"]);
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
        general_dialog("API endpoint error.", "An error occurred while trying to retrieve this server's settings.", "error", 2);
        log("An error occurred while trying to contact the API server. Try reloading the page.", "error");

        toggle_center_column("messages"); // show the messages window instead of global settings, because we can't load user's settings
        console.log("Failed to load server info.");
        log("Failed to load server info.");
    })
}



function add_server()
{
    $("#save_server_settings").html("<i class='icon-check'></i> Add a new server");
    /* clear the fields cuz they could be set to some stuff becasue of editing a server before */
    $("#server-edit-form #server_edit_nickname").val("");
    $("#server-edit-form #server_edit_password").val("");
    $("#server-edit-form #server_edit_label").val("");
    $("#server-edit-form #server_edit_ip").val("");
    $("#server-edit-form #server_edit_portno").val("6667");
    $("#server-edit-form #use_tls_ssl_checkbox").prop("checked", Boolean(false));
    log("toggle_center_column(edit_server);");

    toggle_center_column("edit_server");
    $("#save_server_settings").one("click", save_new_server);
}

function save_new_server()
{
    serverName = $("#server-edit-form #server_edit_label").val();
    nickname = $("#server-edit-form #server_edit_nickname").val();
    serverPassword = $("#server-edit-form #server_edit_password").val();
    serverIP = $("#server-edit-form #server_edit_ip").val();
    serverPort = $("#server-edit-form #server_edit_portno").val();
    useSSL = Boolean($("#server-edit-form #use_tls_ssl_checkbox").prop("checked"));

    var posting = $.post("http://{0}:5000/add_new_server_settings".format(hostname),
    {
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
                console.log("Why2");
                general_dialog("Server settings", data["message"], "ok", 2);
                /* TODO: CALL RECONNECT from HERE */
                /* TODO: CALL RECONNECT from HERE */
                toggle_center_column("messages");
                loadServers();
           }
           else if(data["reason"] == "server_settings_not_edited")
           {
                console.log("Why");
                general_dialog("Server settings", data["message"], "ok", 2);

                toggle_center_column("messages");
           }
        }

    });

    posting.fail(function()
    {
         general_dialog("API endpoint error.", "An error occurred while trying to contact the API server.", "error", 2);
         log("An error occurred while trying to contact the API server. Try reloading the page.", "error");
    });
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
                loadServers();
                general_dialog("Server settings", data["message"], "ok", 2);
                /* TODO: CALL RECONNECT from HERE */
                /* TODO: CALL RECONNECT from HERE */
                toggle_center_column("messages");
           }

        }

    });

    posting.fail(function()
    {
         general_dialog("API endpoint error.", "An error occurred while trying to contact the API server.", "error", 2);
         log("An error occurred while trying to contact the API server. Try reloading the page.", "error");
    });
}


function loadSettingsIntoInputs()
{
    console.log("loadSettingsIntoInputs();")
    $(".center_settings_container .loading-ajax").show();

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

            $(".center_settings_container .loading-ajax").hide();

        }
        else if(data["reason"] == "not_loggedin")
        {
            general_dialog("Access denied: You are not logged in.", data["message"], "error", -1);
        }
    });

    posting.fail(function()
    {
        general_dialog("API endpoint error.", "An error occurred while trying to retrieve your account's global settings.", "error", 2);
        toggle_center_column("messages"); // show the messages window instead of global settings, because we can't load user's settings
        console.log("Failed to global settings.");
        log("An error occurred while trying to contact the API server. Try reloading the page.", "error");
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
                loadSettingsIntoVariable();
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
        log("An error occurred while trying to contact the API server. Try reloading the page.", "error");
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
                log("Logged out successfully.", "error");
                sendUserAway("login.html", 500);
           }
        }

    });

    posting.fail(function()
    {
         general_dialog("API endpoint error.", "An error occurred while trying to contact the API server.", "error", 2);
         log("An error occurred while trying to contact the API server. Try reloading the page.", "error");
    });
}


