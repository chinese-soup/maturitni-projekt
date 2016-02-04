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
    var signup_form = document.getElementsByName("signup-form")[0];
    signup_form.addEventListener("submit", register);
}

/*  makes an api call to register an account */
function register(event)
{
    $.post( 'http://localhost:5000/register', $('form#signup-form').serialize(), function(data)
    {
        console.log(data);
    },
       'json'
    );
    event.preventDefault();
    return false;
}



