$.ajaxSetup({
    crossDomain: true,
    xhrFields: {
        withCredentials: true
    }
});


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

/* call before every command just to see if the user is still logged in */
/* returns true (loggedin) /false (notloggedin) */
function isUserLoggedIn()
{
    var posting = $.post("http://localhost:5000/check_session", {}, datatype="text");
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
    var posting = $.post("http://localhost:5000/upon_login",
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


function loadServers()
{
    console.log("loadServers();");
    $(".channel_list .loading-ajax").parent().show(); // hide the loading servers icon

    var posting = $.post("http://localhost:5000/get_server_list",
    {
    }, dataType="text"
    );

    posting.done(function(data)
    {
        if(data["result"] == "listing_servers")
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
            $(".channel_list .loading-ajax").parent().hide(); // hide the loading servers icon
            $(".channel_list #server_" + serverID + " .networkname").html(serverName);

            /*$(".channel_list > #server_3 .networkname")*/


        }


    });

    posting.fail(function()
    {
        console.log("Failed to load servers.")
    })
}


function logout()
{
   var posting = $.post("http://localhost:5000/logout",
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
           if(data["reason"] == "loggedin_email_status")
           {
                general_dialog("Logged out successfully.", data["message"], data["status"]);
                sendUserAway("login.html", 3000);
           }
        }

    });

    posting.fail(function()
    {
         general_dialog("API endpoint error.", "An error occurred while trying to contact the API server.", "error", 2);
    });
}