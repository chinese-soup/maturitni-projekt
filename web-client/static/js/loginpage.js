/* function loaded on page load */
function loginPageOnLoad()
{
    var login_form = document.getElementById("login-form");
    login_form.addEventListener("submit", login);
}



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


/*
 *  login(event): function called upon submitting the login form;
 *  makes an api call to login an account
 */
function login(event)
{
    var posting = $.post("http://localhost:5000/login",
    {
        email: $("#login-form input[id=email]").val(),
        password: $("#login-form input[id=pwd]").val()
    }, dataType='json'
    );

    posting.done(function(data)
    {
        console.log(data);
        json_parsed = data;

    });

    posting.fail(function()
    {
         general_dialog("Login failed", "An error occurred while trying to contact the API server.", "error", 2);
    });

    event.preventDefault();
    return false;
}
