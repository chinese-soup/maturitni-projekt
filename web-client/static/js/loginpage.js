/* function loaded on page load */
function loginPageOnLoad()
{
    var login_form = document.getElementById("login-form");
    login_form.addEventListener("submit", login); // bind submit in the form to a function

    checkUserAlreadyLoggedIn();

}


var hostname = location.hostname; // maybe temporary(?): get the current hostname so we know where to make api calls (same host, different port)


window.onhashchange = function()
{
  switch(location.hash) {
    case "#regsuccess":
        general_dialog("Registration success", "You have successfully registered an account. You can now login using this page.", "success", 0);
    break;
    case "#has2":
      //do something else
    break;
    default:
        console.log("default");
    break;

  }
}

$.ajaxSetup({
    crossDomain: true,
    xhrFields: {
        withCredentials: true // very important, needed to be able to send POST data
    }
});


function checkUserAlreadyLoggedIn()
{
    var posting = $.post("http://" + hostname + ":5000/check_session",
    {
       email: $("#login-form input[id=email_login]").val(),
       password: $("#login-form input[id=password_login]").val()
    }, dataType="text"
    );

    posting.done(function(data)
    {
        console.log(data);
        if(data["reason"] == "alive_loggedin")
        {
            $("#content-form").hide();
            $("#content-user-already-logged-in-button").fadeIn(500);
        }
        else if(data["reason"] == "alive_not_loggedin")
        {

        }
        disableLoginFormWhileAjax(false);
    });

    posting.fail(function()
    {
        disableLoginFormWhileAjax(false);
    });

}

/*
 * disable the form inputs when a logging in attempt is happening
 */

function disableLoginFormWhileAjax(toggle)
{
    if(Boolean(toggle) == true)
    {
        $("#login-form input[id=email_login]").prop('disabled', true);
        $("#login-form input[id=password_login]").prop('disabled', true);
    }
    else if(Boolean(toggle) == false)
    {
        $("#login-form input[id=email_login]").prop('disabled', false);
        $("#login-form input[id=password_login]").prop('disabled', false);
    }
}


/*
 *  login(event): function called upon submitting the login form;
 *  makes an api call to login an account
 */
function login(event)
{
    disableLoginFormWhileAjax(true);
    var posting = $.post("http://" + hostname + ":5000/login",
    {
       email: $("#login-form input[id=email_login]").val(),
       password: $("#login-form input[id=password_login]").val()
    }, dataType="text"
    );

    posting.done(function(data)
    {
        console.log(data);
        if(data["status"] == "ok")
        {
            if(data["reason"] == "already_loggedin")
            {
                general_dialog("Already logged in.", data["message"], "error");
                window.location.href = "chat.html";
            }
            else if(data["reason"] == "cookie_ok")
            {
                console.log("Server set your cookie of localhost:5000 to:" + data["sessionid"])
                window.location.href = "chat.html";
            }
        }
        else if(data["status"] == "error")
        {
            if(data["reason"] == "badlogin")
            {
                general_dialog("Bad login credentials", data["message"], "error");
            }
            else if(data["reason"] == "loginerror")
            {
                general_dialog("General error", data["message"], "error");
            }

        }
        disableLoginFormWhileAjax(false);
    });

    posting.fail(function()
    {
        disableLoginFormWhileAjax(false);
        general_dialog("Login failed", "An error occurred while trying to contact the API server.", "error", 0);
    });

    event.preventDefault();
    return false;
}
