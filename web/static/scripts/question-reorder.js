$(function() {
  var questionIds
    , ul
    , input
    , submitButton
    , cancelButton
    , numQuestions
    , reorder
    , init;

  ul = $('#ul-reorder');
  input = $('#question-ids');
  submitButton = $('#submit-reorder');
  cancelButton = $('#cancel-reorder');
  numQuestions = parseInt(ul.data('questionCount'), 10);

  ul.find('li').on('tap', function() {
    var questionId = parseInt($(this).data('questionId'), 10);
    var index = questionIds.indexOf(questionId);
    var countBubble = $(this).find('.ui-li-count');

    if (index === -1) {
      questionIds.push(questionId);
      countBubble.text(questionIds.length);
    } else {
      questionIds.splice(index, 1);
      countBubble.text('');
      reorder();
    }

    if (questionIds.length < numQuestions) {
      submitButton.attr('disabled', 'disabled');
      input.val('');
    } else {
      submitButton.removeAttr('disabled');
      input.val(questionIds.join(','));
    }
  });

  reorder = function() {
    ul.find('li').each(function() {
      if ($(this).data('role') === 'list-deivider') return true;
      var questionId = parseInt($(this).data('questionId'), 10);
      var index = questionIds.indexOf(questionId);
      if (index !== -1) $(this).find('.ui-li-count').text(index + 1);
    });
  };

  init = function() {
    questionIds = [];
    input.val('');
    ul.find('.ui-li-count').text('');
  };
  init();
  cancelButton.on('tap', init);
});
