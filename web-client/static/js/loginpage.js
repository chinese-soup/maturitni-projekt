window.onhashchange = function()
{
  switch(location.hash) {
    case '#regsuccess':
        general_dialog("Registration successful", "You have successfully registered an account, you can now login using this page.", "success", 2);
    break;
    case '#has2':
      //do something else
    break;
    default:
        console.log("default");
    break;

  }
}