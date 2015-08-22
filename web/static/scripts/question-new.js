$(function() {
  var switchForm
    , adjustNumAnswers;

  switchForm = function() {
    var elements = $('.hide-on-from-type-text');
    if ($('#form-type-text').is(':checked')) {
      elements.hide();
    } else {
      elements.show();
    }
  };
  switchForm();
  $('#form-type-selection').on('change', switchForm);
  $('#form-type-text').on('change', switchForm);

  adjustNumAnswers = function() {
    var minNumAnswers
      , maxNumAnswers
      , target;

    minNumAnswers = $('#question-min-num-answers');
    maxNumAnswers = $('#question-max-num-answers');

    if (parseInt(minNumAnswers.val(), 10) > parseInt(maxNumAnswers.val(), 10)) {
      target = ($(this)[0] == minNumAnswers[0]) ? maxNumAnswers : minNumAnswers;
      target.val($(this).val()).slider('refresh');
    }
  };
  adjustNumAnswers();
  $('#new').on('change', '#question-min-num-answers', adjustNumAnswers);
  $('#new').on('change', '#question-max-num-answers', adjustNumAnswers);
});
