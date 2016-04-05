// JavaScript Document

var catcher = function() {
  var changed = false;
  $('form').each(function() {
    if ($(this).data('initialForm') != $(this).serialize()) {
      changed = true;
      $(this).addClass('changed');
    } else {
      $(this).removeClass('changed');
    }
  });
  if (changed) {
    return 'Tietoja tällä sivulla on muutettu. Oletko varma, että haluat siirtyä pois tältä sivulta ja hylätä muutokset?';
  }
};

$(function() {
  $('form').each(function() {
    $(this).data('initialForm', $(this).serialize());
  }).submit(function(e) {
  var formEl = this;
  var changed = false;
  $('form').each(function() {
    if (this != formEl && $(this).data('initialForm') != $(this).serialize()) {
      changed = true;
      $(this).addClass('changed');
    } else {
      $(this).removeClass('changed');
    }
  });
  if (changed && !confirm('Jotain toista lomaketta tällä sivulla on jo muokattu. Oletko varma, että haluat lähettää juuri tämän lomakkeen?')) {
    e.preventDefault();
  } else {
    $(window).unbind('beforeunload', catcher);
  }
  });
  $(window).bind('beforeunload', catcher);
});
