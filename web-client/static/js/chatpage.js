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


function loadServers()
{
    console.log("loadServers();");
    var posting = $.post("http://localhost:5000/get_server_list",
    {
    }, dataType="text"
    );

    posting.done(function(data)
    {
        console.log(data);
    });
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