$.ajaxSetup({
    crossDomain: true,
    xhrFields: {
        withCredentials: true
    }
});

var hostname = location.hostname; // maybe temporary(?): get the current hostname so we know where to make api calls (same host, different port)

function onChatLoad()
{
    console.log("onChatLoad();");
    checkIfUserIsLoggedInOnStart();

}


$body = $("body");

$(document).on({
    ajaxStart: function() { console.log("ajaxStart();"); /* $body.addClass("loading"); */ },
     ajaxStop: function() { console.log("ajaxStop();");  /* $body.removeClass("loading"); */ }
});


/* target element is in jquery style */
function showLoadingMemeCircleInsteadOfTheElement(target_element)
{

}

function sendUserAway(url, time)
{
    setTimeout(sendUserAwayTimeout, time, url);
}

function sendUserAwayTimeout(url)
{
    window.location.href = url;
}

/* call before some commands just to see if the user is still logged in */
/* returns true (loggedin) /false (notloggedin) */
function isUserLoggedIn()
{
    var posting = $.post("http://" + hostname + "/check_session", {}, datatype="text");
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
    var posting = $.post("http://" + hostname + ":5000/upon_login",
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
    var html = '<li id="server_' + serverID + '" class="left_channels_flex_item server_item">' +
        '<a href="#"><span class="networkname">Memes</span> <small class="networkipport">(irc.freenode.org/6667)</small></a>' +
        '<div class="dropdown">' +
            '<button class="btn dropdown-toggle dropdown_server_wheel" type="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">' +
                '<i class="icon-settingsfour-gearsalt"></i>' +
            '</button>' +
            '<ul class="dropdown-menu dropdown-menu-right">' +
                '<li><a class="join_another_channel_link" href="#" onclick="#">Join another channel&hellip;</a></li>' + /*join_channel_dialog(\'Freenode\',\'ID\' ); */
                '<li><a class="disconnect_link" href="#" onclick="#">Disconnect</a></li>' + /* disconnect_dialog(\'Freenode\', \'ID\');*/
                '<li role="separator" class="divider"></li>' +
                '<li><a href="#" onclick="toggle_center_column(\'edit_server\');">Edit</a></li>' +
            '</ul>' +
        '</div>' +
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

    var posting = $.post("http://" + hostname + ":5000/get_server_list",
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

                $(".channel_list").append(generateServerHTML(serverID));  // generate a dummy <li> list and append it to the server list
                $(".left_channels_flex_container .loading-ajax").hide(); // hide the loading servers icon
                $(".channel_list #server_" + serverID + " .networkname").html(serverName);

                /* TODO: IDS for  onclicks and stuff!!! */

                if(useSSL == 0)
                    $(".channel_list #server_" + serverID + " .networkipport").html("(" + serverIP + "/" + serverPort + ")");
                else
                    $(".channel_list #server_" + serverID + " .networkipport").html("(" + serverIP + "/" + serverPort + "/SSL)");

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


function loadSettingsIntoInputs()
{
    console.log("loadSettingsIntoInputs();")
    var posting = $.post("http://" + hostname + ":5000/get_global_settings",
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
            /*for (key in settings)
            {
                value = servers[key];
                /*show_previews, highlight_words, whois_username, whois_realname,
                global_nickname, Registred_users_userID, autohide_channels,
                hide_joinpartquit_messages,
                show_seconds,
                Registred_users_userID, id*/

            $("#global-settings-form #hilight_words_input").val(settings[0]);
            $("#global-settings-form #username").val(settings[1]);
            $("#global-settings-form #realname").val(settings[2]);
            $("#global-settings-form #nickname").val(settings[3]);
            $("#global-settings-form #show_joinpartquit_messages").prop("checked", Boolean(settings[4]));
            $("#global-settings-form #show_seconds_checkbox").prop("checked", Boolean(settings[5]));
            $("#global-settings-form #show_video_previews_checkbox").prop("checked", Boolean(settings[6]));
            $("#global-settings-form #show_image_previews_checkbox").prop("checked", Boolean(settings[7]));

                /*$(".channel_list > #server_3 .networkname")*/
           // }
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
    var posting = $.post("http://" + hostname + ":5000/save_global_settings",
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
                general_dialog("Access denied: You are not logged in.", data["message"], "error", 2)
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
   var posting = $.post("http://" + hostname + ":5000/logout",
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
                general_dialog("Couldn't log you out.", data["message"], data["status"]);
                sendUserAway("login.html", 4000);
            }
        }
        else if(data["status"] == "ok")
        {
           if(data["reason"] == "loggedout")
           {
                general_dialog("Logged out successfully.", data["message"], data["status"]);
                sendUserAway("login.html", 1000);
           }
        }

    });

    posting.fail(function()
    {
         general_dialog("API endpoint error.", "An error occurred while trying to contact the API server.", "error", 2);
    });
}


