window.onhashchange = function()
{
  switch(location.hash) {
    case '#regsuccess':
        general_dialog("Registration success", "You have successfully registered an account. You can now login using this page.", "success", 2);
    break;
    case '#has2':
      //do something else
    break;
    default:
        console.log("default");
    break;

  }
}

/* function loaded on page load */
function homePageOnLoad()
{
    var signup_form = document.getElementById("login-form");
    signup_form.addEventListener("submit", register);
}

/*
 *  register(event): function called upon submitting the registration form;
 *  makes an api call to register an account
 */
function login(event)
{
    if()
    var posting = $.post("http://localhost:5000/login",
    {
        email: $("#login-form input[id=email]").val(),
        password: $("#login-form input[id=pwd]").val()
    }, dataType='json'
    );

    posting.success(function(data)
    {
        console.log(data);
        json_parsed = data;
        if(json_parsed["status"] == "ok" && json_parsed["reason"] == "reg_success")
        {
            window.location = "login.html#regsuccess";
        }
        else if(json_parsed["status"] == "error")
        {
            console.log(json_parsed["message"]);
            general_dialog("Registration failed", json_parsed["message"], "error", 2);
        }
    });

    posting.error(function()
    {
         general_dialog("Registration failed", "An error occurred while trying to contact the API server.", "error", 2);
    });

    event.preventDefault();
    return false;
}
