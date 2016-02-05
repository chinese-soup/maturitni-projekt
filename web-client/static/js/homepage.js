/*window.onhashchange = function()
{
  switch(location.hash) {
    case '#register':
        register();
    break;
    case '#has2':
      //do something else
    break;

  }
}*/
function homePageOnLoad()
{
    var signup_form = document.getElementById("signup-form");
    signup_form.addEventListener("submit", register);
}

/*  makes an api call to register an account */
function register(event)
{

    $.post("http://localhost:5000/register",
    {
        email: $("#signup-form input[id=email]").val(),
        password: $("#signup-form input[id=pwd]").val()
    },
    function(data)
    {
        console.log(data);
    },
       'json'
    );
    event.preventDefault();
    return false;
}



