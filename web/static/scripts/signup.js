$(function() {
  var inputPassword
    , inputConfirmPassword
    , errorPassword
    , inputTermOfUse
    , buttonSubmit
    , isValidPassword
    , isAgreed
    , validateForm;

  inputPassword = $('#password');
  inputConfirmPassword = $('#confirm-password');
  errorPassword = $('#error-password');
  inputTermOfUse = $('#term-of-use');
  buttonSubmit = $('#submit');

  isValidPassword = function() {
    if (inputConfirmPassword.val() === '') return false;
    return inputPassword.val() === inputConfirmPassword.val();
  };
  isAgreed = function() { return inputTermOfUse.prop('checked') };

  validateForm = function() {
    if (!isValidPassword()) {
      errorPassword.show();
      buttonSubmit.addClass('ui-disabled');
    } else if (!isAgreed()) {
      errorPassword.hide();
      buttonSubmit.addClass('ui-disabled');
    } else {
      errorPassword.hide();
      buttonSubmit.removeClass('ui-disabled');
    }
  };
  inputPassword.on('keyup', validateForm);
  inputConfirmPassword.on('keyup', validateForm);
  inputTermOfUse.on('change', validateForm);
});
