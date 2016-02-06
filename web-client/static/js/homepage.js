/*window.onhashchange = function()
{
  switch(location.hash) {
    case '#exists':

    break;
  }
}*/

/* function loaded on page load */
function homePageOnLoad()
{
    var signup_form = document.getElementById("signup-form");
    signup_form.addEventListener("submit", register);
}

/*
 *  register(event): function called upon submitting the registration form;
 *  makes an api call to register an account
 */
function register(event)
{
    if()
    var posting = $.post("http://localhost:5000/register",
    {
        email: $("#signup-form input[id=email]").val(),
        password: $("#signup-form input[id=pwd]").val()
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



