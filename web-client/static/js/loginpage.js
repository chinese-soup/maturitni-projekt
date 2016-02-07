/* function loaded on page load */
function loginPageOnLoad()
{
    var login_form = document.getElementById("login-form");
    login_form.addEventListener("submit", login);
}

window.onhashchange = function()
{
  switch(location.hash) {
    case "#regsuccess":
        general_dialog("Registration success", "You have successfully registered an account. You can now login using this page.", "success", 2);
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
        withCredentials: true
    }
});

/*
 *  login(event): function called upon submitting the login form;
 *  makes an api call to login an account
 */
function login(event)
{
    $("#login-form input[id=email_login]").prop('disabled', true);
    $("#login-form input[id=password_login]").prop('disabled', true);
    var posting = $.post("http://localhost:5000/login",
    {
        email: $("#login-form input[id=email_login]").val(),
        password: $("#login-form input[id=password_login]").val()
    }, dataType="text"
    );

    posting.done(function(data)
    {
        console.log(data);
        json_parsed = data;
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
                // Cookies.set("sessionid", data["sessionid"], { expires: 7, domain: "localhost" });*/
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
        $("#login-form input[id=email_login]").prop('disabled', false);
        $("#login-form input[id=password_login]").prop('disabled', false);

    });

    posting.fail(function()
    {
        $("#login-form input[id=email_login]").prop('disabled', false);
        $("#login-form input[id=password_login]").prop('disabled', false);
         general_dialog("Login failed", "An error occurred while trying to contact the API server.", "error", 2);
    });

    event.preventDefault();
    return false;
}
