$(function() {
  var inputPassword
    , inputConfirmPassword
    , errorPassword
    , buttonSubmit
    , isValidPassword
    , validateForm;

  inputPassword = $('#password');
  inputConfirmPassword = $('#confirm-password');
  errorPassword = $('#error-password');
  buttonSubmit = $('#submit');

  isValidPassword = function() {
    if (inputConfirmPassword.val() === '') return false;
    return inputPassword.val() === inputConfirmPassword.val();
  };

  validateForm = function() {
    if (!isValidPassword()) {
      errorPassword.show();
      buttonSubmit.addClass('ui-disabled');
    } else {
      errorPassword.hide();
      buttonSubmit.removeClass('ui-disabled');
    }
  };
  inputPassword.on('keyup', validateForm);
  inputConfirmPassword.on('keyup', validateForm);
});
