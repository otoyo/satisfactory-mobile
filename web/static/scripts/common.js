$(function() {
  $('.confirm-submit').on('tap', function() {
    var msg = $(this).data('msg');
    if (confirm(msg)) $(this).closest('form').trigger('submit');
  });
});
