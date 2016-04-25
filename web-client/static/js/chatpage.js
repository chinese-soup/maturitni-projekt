$.ajaxSetup({
    crossDomain: true,
    xhrFields: {
        withCredentials: true // very important, needed to be able to send POST data
    }
});


// Global variables
var hostname = location.hostname; // maybe temporary(?): get the current hostname so we know where to make api calls (same host, different port)
var already_loaded_backlog = []; // list of channels that already have backlog pulled so that we don't pull it again
var global_settings = {"hilight_words": null, "username": null, "realname": null, "nickname": null, "show_joinpartquit_messages": null, "show_seconds": null, "show_video_previews": null, "show_image_previews": null}; // currently inplace global settings, loaded upon loading, changed when the settings are changed
var channel_messages = {}; // list of channel messages

var channel_ids = []; // list of channel IDs of the user

var last_message_id = {}; // dictionary, key: channelID, value: ID of the last message in a channel
var last_message_id_servers = -1; // int; last message of the status window

var current_status_window_serverID = -1; // int; current server selected in the status window (sends commands and stuff to the selected server)

var currently_visible_message_window = -1; // int; which channel window is currently selected (-1 = status, always -1 upon load)


/*
    overrides the default string function in javascript to include formatting support
*/
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
    checkIfUserIsLoggedInOnStart(); // check if the user is logged in upon loading the DOM, if he is not, redirect him to the login page
    loadSettingsIntoVariable(); // load settings into the global_settings variable, for further use (e.g. show seconds? show previews?)

    $("#button_send_message").off("click"); // kill the click event of the chat message, just to be sure
    $("#button_send_message").click({channelID:-1}, sendTextBoxCommand); // bind the click event of the Send button to sendTextBoxCommand and channelID of the status window

    $("#input-msgline").off("keypress");
    $("#input-msgline").keypress({channelID:-1}, sendTextBoxCommand); // bind the same as above, but pressing enter key while the message textbox is focused

    setTimeout(ping, 1500); // set the initial timer to call the ping method in 1500 ms
}


/*
    called when the user presses send/enter/etc. to send the textbox content to the server
*/
function sendTextBoxCommand(event)
{
    if (event.keyCode == 13 || event.keyCode == null)
    {
        console.log("Enter key");

        channelID = event.data.channelID;
        textBoxData = $("#input-msgline").val(); // get the textbox data the user wants to send
        if(textBoxData != "" && textBoxData != null)
        {
            log("sendTextBoxCommand({0})".format(channelID, textBoxData));

            if(channelID == -1 && current_status_window_serverID != -1) // if the channel is the status window
            {
                serverID = current_status_window_serverID; // we  need to get the current server that is selected in the status window
            }
            else
            {
                serverID = -1; // otherwise we just send an invalid server value (-1 because laziness)
            }

            var posting = $.post("http://{0}:5000/send_textbox_io".format(hostname),
            {
               serverID: serverID,
               channelID: channelID,
               textBoxData: textBoxData
            }, dataType="text"
            );

            posting.done(function(data)
            {
                console.log(data);
                if(data["reason"] == "textbox_io_server_window_inserted" || data["reason"] == "textbox_io_channel_window_inserted")
                {
                    $("#input-msgline").val(""); // reset the message textbox to an empty string

                }
                else if(data["reason"] == "not_loggedin")
                {
                    general_dialog("Access denied: You are not logged in.", data["message"], "error", -1); // the user is not logged in
                }
            });

            posting.fail(function()
            {
                log("There was an error sending the textbox input.")
        })
        }
    }

}


/*
    called in order to send an IO message (any non-textbox one)
     "userID": result[0],
                    "commandType": result[1],
                    "argument1": result[2],
                    "argument2": result[3],
                    "argument3": result[4],
                    "timeSent": result[5],
                    "processed": bool(result[6]),
                    "timeReceived": result[7],
                    "fromClient": bool(result[8]),
                    "serverID": result[9],
                    "channelID": result[10],
                    "messageID": result[11]
*/
function sendCommand(ioType, argument1, argument2, argument3, serverID, channelID)
{
    var posting = $.post("http://{0}:5000/send_io".format(hostname),
    {
       ioType: ioType,
       argument1: argument1,
       argument2: argument2,
       argument3: argument3,
       serverID: serverID,
       channelID: channelID,
    }, dataType="text"
    );

    posting.done(function(data)
    {
        console.log(data);
        log(data["message"]);
        if(data["reason"] == "textbox_io_server_window_inserted" || data["reason"] == "textbox_io_channel_window_inserted")
        {

        }
        else if(data["reason"] == "not_loggedin")
        {
            general_dialog("Access denied: You are not logged in.", data["message"], "error", -1); // the user is not logged in
        }
    });

    posting.fail(function()
    {
        log("There was an error sending the textbox input.")
    })

}


/*
   loading settings into variables
   for when the user opens the edit global settings window
*/
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
        toggle_center_column("messages"); // show the messages window instead of global settings, because we can't load user's current settings, so we don't want him to change them
        log("Could not load global settings.")
    })
}

function ping()
{
    //console.log("ping()");
    getNewMessages();
    getNewServerMessages();
    setTimeout(ping, 1500);
}


function getNewServerMessages()
{
    var posting = $.post("http://{0}:5000/get_server_messages".format(hostname),
    {
       serverID: -1, // TODO: dummy, need to remove from API
       limit: 1000000000,
       backlog: 0,
       sinceTimestamp: last_message_id_servers,
    }, dataType="text"
    );

    posting.done(function(data)
    {
        if(data["status"] == "error")
        {
            log(data["reason"]);
        }
        else if(data["status"] == "ok")
        {
           if(data["reason"] == "listing_other_messages")
           {
                var messages = data["message"];
                for (var i=0; i < messages.length; i++)
                {
                    last_message_id_servers = messages[i]["messageID"];
                    var msgid = messages[i]["messageID"];
                    if( $("div#server_log_msgid_{0}".format(msgid)).length ) // check if the msg isnt already printed out to prevent double posting
                    {
                        continue;
                    }

                     addMessageToServerChannel(
                        messages[i]["messageID"],
                        convertDBTimeToLocalTime(messages[i]["timeReceived"]),
                        "-!- [{0}] {1}".format(messages[i]["serverName"], messages[i]["fromHostmask"]),
                        "ok",
                        "({0}): {1}".format(messages[i]["commandType"], messages[i]["messageBody"]),
                        -1
                    );


                }
           }
        }

    });

    posting.fail(function()
    {
         log("An error occurred while trying to contact the API server. Try reloading the page.", "error");
    });
}



function getNewMessages()
{
    for(var i=0; i < channel_ids.length; i++)
    {
        var channelID = channel_ids[i]; // TODO: REPLACE ME
        if(channelID in last_message_id)
        {
            var posting = $.post("http://{0}:5000/get_messages".format(hostname),
            {
               channelID: channelID,
               limit: 1000000000,
               backlog: 0,
               sinceTimestamp: last_message_id[channelID]
            }, dataType="text"
            );

            posting.done(function(data)
            {
                if(data["status"] == "error")
                {
                    log(data["reason"]);
                }
                else if(data["status"] == "ok")
                {
                   if(data["reason"] == "listing_new_messages")
                   {
                        var messages = data["message"];
                        /*if(currently_visible_message_window != channelID && currently_visible_message_window != -1)
                        {
                            $("#channel_{0}".format(channelID)).find(".channel_item_active_msg_count").show(); // show new message count in the channel list
                            var current_count = parseInt($("#channel_{0}".format(channelID)).find(".channel_item_active_msg_count").text()); // get the current_count
                            $("#channel_{0}".format(channelID)).find(".channel_item_active_msg_count").text("{0}".format(current_count + messages.length)); // set the new message count in the channel list
                        }*/

                        for (var i=0; i < messages.length; i++)
                        {
                            var msgid = messages[i]["messageID"];
                            if( $("div#log_msgid_{0}".format(msgid)).length ) // check if the msg isnt already printed out to prevent double posting
                            {
                                console.log("UŽ EXISTUJE");
                                continue;
                            }

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
                            else if(messages[i]["commandType"] == "JOIN" || messages[i]["commandType"] == "QUIT" || messages[i]["commandType"] == "PART")
                            {
                                addJoinPartQuitToChannel(
                                    messages[i]["messageID"],
                                    convertDBTimeToLocalTime(messages[i]["timeReceived"]),
                                    messages[i]["commandType"],
                                    messages[i]["fromHostmask"],
                                    messages[i]["messageBody"],
                                    messages[i]["IRC_channels_channelID"]
                                );

                            }
                            else if(messages[i]["commandType"] == "ACTION")
                            {
                                 addActionMessage(
                                    messages[i]["messageID"],
                                    convertDBTimeToLocalTime(messages[i]["timeReceived"]),
                                    getNicknameFromHostmask(messages[i]["fromHostmask"]),
                                    "ok",
                                    linkifyMessage(messages[i]["messageBody"]),
                                    messages[i]["IRC_channels_channelID"]
                                );
                            }
                            else if(messages[i]["commandType"] == "NAMREPLY") // pokud se jedná /me zprávu
                            {
                                 addActionMessage(
                                    messages[i]["messageID"],
                                    convertDBTimeToLocalTime(messages[i]["timeReceived"]),
                                    messages[i]["fromHostmask"],
                                    "ok",
                                    messages[i]["messageBody"],
                                    messages[i]["IRC_channels_channelID"]
                                );

                            }
                            else if(messages[i]["commandType"] == "KICK") // pokud se jedná /me zprávu
                            {
                                  addActionMessage(
                                    messages[i]["messageID"],
                                    convertDBTimeToLocalTime(messages[i]["timeReceived"]),
                                    getNicknameFromHostmask(messages[i]["fromHostmask"]),
                                    "ok",
                                    "has kicked {0} from this channel.".format(messages[i]["messageBody"]),
                                    messages[i]["IRC_channels_channelID"]
                                );

                            }
                            last_message_id[messages[i]["IRC_channels_channelID"]] = messages[i]["messageID"];


                        }
                   }

                }


            });

            posting.fail(function()
            {
                 log("An error occurred while trying to contact the API server. Try reloading the page.", "error");


            });
        }
    }

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

function addActionMessage(messageID, timestamp, sender, senderColor, message, channelID)
{
    var html =
    '<div class="log_message log_message_even" id="log_msgid_{0}">'.format(messageID) +
    '    <span class="timestamp">{0}</span>'.format(timestamp) +
    '    <span class="message-body"><span class="message-sender message-sender-{0}">* {1}</span> {2}</span>'.format(senderColor, sender, message) +
    '</div>';


    var element = $("#channel_window_{0}".format(channelID));
    element.append(html);

    var element2 = $(".center_messages_container");
    element2.prop("scrollTop", 500000000000); // scrollneme dolů, protože máme nové
}

function addJoinPartQuitToChannel(messageID, timestamp, messageType, sender, message, channelID)
{
    if(global_settings["show_joinpartquit_messages"] == true) // only write these messages if the user has enabled it in his settings
    {
        var verb = "";
        console.log("CUS NE", messageType);
        switch(messageType)
        {
            case "PART":
                verb = "left";
                break;
            case "JOIN":
                verb = "joined";
                break;
            case "QUIT":
                verb = "quit";
                break;
        }
        var hostmask = sender;
        var nickname = getNicknameFromHostmask(hostmask);
        if(message == "[]")
            message = "&lt;no reason&gt;";

        var html =
        '<div class="log_message log_message_odd" id="log_msgid_{0}">'.format(messageID) +
        '    <span class="timestamp">{0}</span>'.format(timestamp) +
        '    <span class="message-body"><span class="message-sender message-sender-{0}">{1}</span> <small>[{2}]</small> has {3} ({4})</span>'.format(2, nickname, hostmask, verb, message) +
        '</div>';

        var element = $("#channel_window_{0}".format(channelID));
        element.append(html);

        var element2 = $(".message_window");
        element2.prop("scrollTop", 500000000000); // scrollneme dolů, protože máme nové
    }
}


function addMessageToChannel(messageID, timestamp, sender, senderColor, message, channelID)
{
    var colorHash = new ColorHash({lightness: [0.65, 0.65, 0.65]});
    senderColor = colorHash.hex(sender);
    var MsgBGstyle = "odd";
    try
    {
        if(global_settings["hilight_words"] != "")
        {
            var hilight_words_array = global_settings["hilight_words"].split(";");

            for (i = 0; i < hilight_words_array.length; i++)
            {
                if(message.search(hilight_words_array[i]) != -1)
                {
                    MsgBGstyle = "hilight";
                }
            }
        }
    }
    catch(err)
    {
        MsgBGstyle = "odd";
    }
    var html =
    '<div class="log_message log_message_{0}" id="log_msgid_{1}">'.format(MsgBGstyle, messageID) +
    '    <span class="timestamp">{0}</span>'.format(timestamp) +
    '    <span class="message-body"><span class="message-sender message-sender-0" style="color: {0} !important;">{1}</span>: {2}</span>'.format(senderColor, sender, message) +
    '</div>';


    var element = $("#channel_window_{0}".format(channelID));
    element.append(html);

    var element2 = $(".center_messages_container");
    element2.prop("scrollTop", 500000000000); // scrollneme dolů, protože máme nové
}


function addMessageToServerChannel(messageID, timestamp, sender, senderColor, message, channelID)
{
    var colorHash = new ColorHash({lightness: [0.65, 0.65, 0.65]});
    senderColor = colorHash.hex(sender);
    var MsgBGstyle = "odd";
    try
    {
        if(global_settings["hilight_words"] != "")
        {
            var hilight_words_array = global_settings["hilight_words"].split(";");

            for (i = 0; i < hilight_words_array.length; i++)
            {
                if(message.search(hilight_words_array[i]) != -1)
                {
                    MsgBGstyle = "hilight";
                }
            }
        }
    }
    catch(err)
    {
        MsgBGstyle = "odd";
    }

    var html =
    '<div class="log_message log_message_{0}" id="server_log_msgid_{1}">'.format(MsgBGstyle, messageID) +
    '    <span class="timestamp">{0}</span>'.format(timestamp) +
    '    <span class="message-body"><span class="message-sender message-sender-0" style="color: {0} !important;">{1}</span>: {2}</span>'.format(senderColor, sender, message) +
    '</div>';


    var element = $("#channel_window_{0}".format(channelID));
    element.append(html);

    var element2 = $(".center_messages_container");
    element2.prop("scrollTop", 500000000000); // scrollneme dolů, protože máme nové
}

function switchCurrentChannel(toChannelID)
{
    $(".message_window").hide();
    $("#channel_window_{0}".format(toChannelID)).show();

    $("#button_send_message").off("click");
    $("#button_send_message").click({channelID:toChannelID}, sendTextBoxCommand);
    $("#input-msgline").off("keypress");
    $("#input-msgline").keypress({channelID:toChannelID}, sendTextBoxCommand);

    currently_visible_message_window = toChannelID;

    if(toChannelID == -1 && event.data.clickedServerID != null)
    {
        //$(".current_server_div").show();
        current_status_window_serverID = event.data.clickedServerID;
        $(".current_server_div_serverid").html(current_status_window_serverID);
        $(".current_server_div_servername").html(event.data.clickedServerName);
        $("#input-group-msgline .dark_input").prop("placeholder", "Send a command to {0}".format(event.data.clickedServerName));
        log("Server changed to {0}".format(event.data.clickedServerName));
        $(".header_room_topic").text("Send a command to {0}".format(event.data.clickedServerName));
    }
    else if(toChannelID != -1)
    {
        $(".current_server_div").hide();

        // change placeholder of the input textbox
        $("#input-group-msgline .dark_input").prop("placeholder", "Chat in {0}".format(toChannelName));
        $(".header_room_topic").text("Topic for {0}: {1}".format(toChannelName, "N/A"));

    }

}


/* this function makes links clickable, creates images previews, memes */
function linkifyMessage(messageBody)
{
    var regexp = /(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig;
    var image_url = "";
    var youtube_url = "";
    messageBody = messageBody.replace(regexp, function(url)
    {
        if(global_settings["show_image_previews"] == true)
        {
            image_url = url;
        }
        if(global_settings["show_video_previews"] == true)
        {
            youtube_url = url;
        }
        return("<a href=\"{0}\">{0}</a>".format(url));

    });
    if(image_url != "")
    {
        if(image_url.endsWith(".png") || image_url.endsWith(".jpg") || image_url.endsWith(".gif") || image_url.endsWith(".jpeg"))
        {
            messageBody = messageBody + "<span class=\"message-image-preview\"><a href=\"#\" onclick=\"preview_images('{0}');\"><img alt=\"Image preview\" title=\"Image\" src=\"{0}\" target=\"_blank\"></a></span>".format(image_url);
        }
    }
    if(youtube_url != "")
    {

        /* http://stackoverflow.com/questions/3452546/javascript-regex-how-to-get-youtube-video-id-from-url */
        var regExp = /.*(youtu\.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
        var match = youtube_url.match(regExp);
        if (match && match[2].length == 11)
        {
            messageBody = messageBody + '<br><iframe width="560" height="315" src="https://www.youtube.com/embed/{0}?rel=0" frameborder="0" allowfullscreen></iframe>'.format(match[2]);
        }
        else
        {

        }
    }
    return(messageBody);
}

/* this function is bound to several */
function switchCurrentChannelEventStyle(event)
{
    toChannelID = event.data.channelID; // get the channelID to change to from the event
    toChannelName = event.data.channelName; // get the name of the channel to change to from the event

    $("#button_send_message").off("click"); // reset click bind
    $("#button_send_message").click({channelID:toChannelID}, sendTextBoxCommand); // set the  click event with the new channelID

    $("#input-msgline").off("keypress"); // reset enter key bind
    $("#input-msgline").keypress({channelID:toChannelID}, sendTextBoxCommand); // set the keypress event with the new channelID

    log("Switching channel window to {0} ({1})".format(toChannelID, toChannelName));

    // hide all message window divs
    $(".message_window").hide();

    // show the requested message window div
    $("#channel_window_{0}".format(toChannelID)).fadeIn(200);

    // remove focused css for any previously focused window in the channel listing
    $(".channel_item".format(toChannelID)).toggleClass("channel_item_focused", false);

    // add focused css for the focused window in the channel listing
    $("#channel_{0}".format(toChannelID)).toggleClass("channel_item_focused", true);

    // change header room name TODO: Fix
    $(".header_room_name").html("{0} <small>({1})</small>".format(toChannelName, toChannelID))

    // save channelID to a variable
    currently_visible_message_window = toChannelID;

    // hide NEW MESSAGES count span
    $("#channel_{0}".format(toChannelID)).find(".channel_item_active_msg_count").hide();

    // reset the value
    $("#channel_{0}".format(toChannelID)).find(".channel_item_active_msg_count").text("0"); // set the new message count in the channel list


    if(toChannelID == -1 && event.data.clickedServerID != null)
    {
        //$(".current_server_div").show();
        current_status_window_serverID = event.data.clickedServerID;
        $(".current_server_div_serverid").html(current_status_window_serverID);
        $(".current_server_div_servername").html(event.data.clickedServerName);
        $("#input-group-msgline .dark_input").prop("placeholder", "Send a command to {0}".format(event.data.clickedServerName));
        log("Server changed to {0}".format(event.data.clickedServerName));
        $(".header_room_topic").text("Send a command to {0}".format(event.data.clickedServerName));

    }
    else if(toChannelID != -1)
    {
        $(".current_server_div").hide();

        // change placeholder of the input textbox
        $("#input-group-msgline .dark_input").prop("placeholder", "Chat in {0}".format(toChannelName));
        $(".header_room_topic").text("Topic for {0}: {1}".format(toChannelName, "N/A"));

    }

    // load backlog if it has not been loaded yet
    if($.inArray(toChannelID, already_loaded_backlog) == -1)
    {
        getBacklogForChannel(toChannelID, 50);
    }
    else
    {

    }

}

function convertDBTimeToLocalTime(dbUTCtime)
{
    var date = new Date(dbUTCtime);
    var date_now = new Date();

    if(date.toLocaleDateString() == date_now.toLocaleDateString()) // zkontrolujeme, jestli daný čas je dnes, pokud ne, vrátíme i datum
    {
        var local_date = date.toLocaleTimeString();
        if(global_settings["show_seconds"] == false)
        {
            local_date = local_date.replace(/\:[0-9]{2}$/g, ""); // remove seconds from the localtime as the user does not wish to see them, ugly hack, but whatever, i need to finish this soon
        }
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
    var asdf = hostmask.match(regexp);
    if(asdf == null)
    {
        return(hostmask);
    }
    else
    {
        return(asdf[1]);
    }

}


function getBacklogForServers(limit)
{
    console.log("backlogServers();");
    var posting = $.post("http://{0}:5000/get_server_messages".format(hostname),
    {
       serverID: -1,
       limit: limit,
       backlog: 1
    }, dataType="text"
    );

    posting.done(function(data)
    {
        console.log(data);

        if(data["status"] == "error")
        {
            if(data["reason"] == "not_loggedin")
            {
                log(data["reason"]);
            }
        }
        else if(data["status"] == "ok")
        {
           if(data["reason"] == "listing_other_messages")
           {
                log(data["message"]);
                console.log(data["message"]);

                var messages = data["message"];

               	for (var i=0; i < messages.length; i++)
                {

                    addMessageToServerChannel(
                        messages[i]["messageID"],
                        convertDBTimeToLocalTime(messages[i]["timeReceived"]),
                        "-!- [{0}] {1}".format(messages[i]["serverName"], messages[i]["fromHostmask"]),
                        "ok",
                        "({0}): {1}".format(messages[i]["commandType"], messages[i]["messageBody"]),
                        -1
                    );

                    last_message_id_servers = messages[i]["messageID"];

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

function getBacklogForChannel(channelID, limit)
{
    var posting = $.post("http://{0}:5000/get_messages".format(hostname),
    {
       channelID: channelID,
       limit: limit,
       backlog: 1
    }, dataType="text"
    );

    posting.done(function(data)
    {
        console.log(data);

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
                console.log(data["message"]);

                var messages = data["message"];

               	for (var i=0; i < messages.length; i++)
                {
                    // pokud se jedná o zprávu z kanálu



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
                    // pokud se jedná o JOIN, QUIT nebo PART zprávu
                    else if(messages[i]["commandType"] == "JOIN" || messages[i]["commandType"] == "QUIT" || messages[i]["commandType"] == "PART")
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
                    else if(messages[i]["commandType"] == "ACTION") // pokud se jedná /me zprávu
                    {
                         addActionMessage(
                            messages[i]["messageID"],
                            convertDBTimeToLocalTime(messages[i]["timeReceived"]),
                            getNicknameFromHostmask(messages[i]["fromHostmask"]),
                            "ok",
                            linkifyMessage(messages[i]["messageBody"]),
                            messages[i]["IRC_channels_channelID"]
                        );

                    }
                    else if(messages[i]["commandType"] == "NAMREPLY") // pokud se jedná /me zprávu
                    {
                         addActionMessage(
                            messages[i]["messageID"],
                            convertDBTimeToLocalTime(messages[i]["timeReceived"]),
                            messages[i]["fromHostmask"],
                            "ok",
                            messages[i]["messageBody"],
                            messages[i]["IRC_channels_channelID"]
                        );

                    }
                    else if(messages[i]["commandType"] == "KICK") // pokud se jedná /me zprávu
                    {
                         addActionMessage(
                            messages[i]["messageID"],
                            convertDBTimeToLocalTime(messages[i]["timeReceived"]),
                            getNicknameFromHostmask(messages[i]["fromHostmask"]),
                            "ok",
                            "has kicked {0} from this channel.".format(messages[i]["messageBody"]),
                            messages[i]["IRC_channels_channelID"]
                        );

                    }

                    last_message_id[messages[i]["IRC_channels_channelID"]] = messages[i]["messageID"]; // cut off 3 zeros at the end
                }

                if($.inArray(channelID, already_loaded_backlog) == -1 && messages.length != 0)
                {
                    already_loaded_backlog.push(channelID);
                }
                else
                {
                    log("not adding to the array because it already is in there");
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
                sendUserAway("login.html", 3000);
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
                '<li><a class="connect_link">Connect</a></li>' + /* disconnect_dialog(\'Freenode\', \'ID\');*/
                '<li role="separator" class="divider"></li>' +
                '<li><a class="remove_server_link"><i class="icon-remove"></i> Remove this server</a></li>' +
                '<li><a class="edit_server_link"><i class="icon-edit"></i> Edit</a></li>' +
            '</ul>' +
        '</div>' +
        '<ul class="channels_ul" style="width: 2px; margin: 2px; padding: 2px;"></ul>' +
    '</li>';
    return(html);
}

function generateChannelHTML(channelID)
{
    var html =  '<li id="channel_{0}" class="left_channels_flex_item channel_item"><div class="channel_item_active_msg_count">0</div>'.format(channelID) +
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

    $(".header_room_topic").val("Join another channel on this network")
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
                general_dialog("Channel added", data["message"], "ok", 2);
                log(data["message"]);
                /* TODO: call join from here */
                toggle_center_column("messages");
                loadServers();
           }
           else if(data["reason"] == "channel_was_not_added")
           {
                general_dialog("Channel not added", data["message"], "ok", 2);
                log(data["message"]);
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

    $(".left_channels_flex_container .loading-ajax").show(); // hide the loading servers icon
    $(".left_channels_flex_container .loading-ajax-message").hide(); // hide the "you have no servers" message

    $(".channel_list").empty(); // clear the server list so we don't dupe the server entries (beware of element id hazard)

    channel_ids = []; // empty the channel IDs array

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

                //$(".channel_list #server_{0} .dropdown .dropdown-menu .disconnect_link".format(serverID)).on("click", {serverName: serverName, serverID: serverID,  });
                //$(".channel_list #server_{0} .dropdown .dropdown-menu .remove_server_link".format(serverID)).on("click", remove_server_dialog(serverName, serverID));
                $(".channel_list #server_{0} .dropdown .dropdown-menu .edit_server_link".format(serverID)).click({serverName:serverName, serverID:serverID, isAnEdit: true}, edit_server);
                $(".channel_list #server_{0} .dropdown .dropdown-menu .disconnect_link".format(serverID)).click({serverName:serverName, serverID:serverID, connect:false}, disconnect_server);
                $(".channel_list #server_{0} .dropdown .dropdown-menu .connect_link".format(serverID)).click({serverName:serverName, serverID:serverID, connect:true}, disconnect_server);
                $(".channel_list #server_{0} .dropdown .dropdown-menu .join_another_channel_link".format(serverID)).click({serverName:serverName, serverID:serverID}, join_channel_dialog);
                $(".channel_list #server_{0} .network_name_link".format(serverID)).click({channelID:-1,
                channelName:"Status window", clickedServerID:serverID, clickedServerName:serverName},
                switchCurrentChannelEventStyle); /* causes
                the server                headers
                 to link to the main status window*/

                // change the selected server (in status window) to the latest one we got:
                current_status_window_serverID = serverID;
                $(".current_server_div_serverid").html(serverID);
                $(".current_server_div_servername").html(serverName);


                if(useSSL == 0)
                    $(".channel_list #server_{0} .networkipport".format(serverID)).html("({0}/{1})".format(serverIP, serverPort));
                else
                    $(".channel_list #server_{0} .networkipport".format(serverID)).html("({0}/{1}/SSL)".format(serverIP, serverPort));


                for (var chans = 0; chans < channels.length; chans++)
                {
                    console.log("CHEN");
                    console.log(channels["chan"]);
                    var channelID = channels[chans]["channelID"];
                    console.log(channelID);
                    var channelName = channels[chans]["channelName"];
                    var isJoined = channels[chans]["isJoined"];
                    var lastOpened = channels[chans]["lastOpened"];
                    var channelServerID = channels[chans]["serverID"];

                    console.log("Channel");
                    console.log(chans);

                    $(generateChannelHTML(channelID)).insertAfter($(".channel_list #server_{0}".format(channelServerID)));  // generate a dummy <li> list and append it to the server list
                    $(".channel_list #channel_{0} .channelName".format(channelID)).html(channelName);

                    $(generateChannelWindow(channelID)).insertAfter($(".message_window".format(channelServerID)));
                    already_loaded_backlog = []; // CLEAR ALL INFO ABOUT BACKLOGS BEING ALREADY LOADED

                    /* bind a click event to a channel in teh channel list*/
                    $(".channel_list #channel_{0} .channelName".format(channelID)).click(
                    {channelID:channelID, channelName:channelName, lastOpened: lastOpened,
                    channelServerID:channelServerID}, switchCurrentChannelEventStyle)

                    channel_ids.push(channelID);

                }
            }

            getBacklogForServers(50); // get the backlog for server messages


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
function disconnect_server(event)
{
    serverName = event.data.serverName;
    serverID = event.data.serverID;
    connect = event.data.connect;
    channelID = -1;
    if(connect == true)
    {
        sendCommand("CONNECT_SERVER", "", "", "", serverID, channelID);
    }
    else
    {
        sendCommand("DISCONNECT_SERVER", "", "", "", serverID, channelID);
    }
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

/* this function is called upon clicking the save button in the global settings window*/
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

/* this function is called upon clicking the save button in an edit server window  */
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

/* this function is called upon */
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
                //general_dialog("Logged out successfully.", data["message"], data["status"]);
                log("Logged out successfully.", "error");
                sendUserAway("login.html", 100);
           }
        }

    });

    posting.fail(function()
    {
         general_dialog("API endpoint error.", "An error occurred while trying to contact the API server.", "error", 2);
         log("An error occurred while trying to contact the API server. Try reloading the page.", "error");
    });
}


