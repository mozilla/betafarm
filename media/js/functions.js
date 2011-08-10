$(document).ready(function($) {

    // header dropdowns
    var mainNav = $('#topNav');
    mainNav.delegate('a.dropdown','mouseover focus',function() {
        $(this).parent().addClass('hover');
    });
    mainNav.delegate('li','mouseleave', function() {
        var current = $(this);
        if (current.hasClass('hover')) {
            current.removeClass('hover');
        }
    });
    mainNav.delegate('a','blur',  function() {
        var current = $(this),
            parent = current.parent();
            grand = parent.parent();
        if (grand.is('ul.dropdown') && parent.is(':last-child')) {
            grand.parent().removeClass('hover');
        }
    });

    // sticky footer
    $(window).bind('load resize', function() {
        var h = $(window).height();
        var a = $('#about').outerHeight();
        $('#wrapper').css({ 'min-height' : (h-a) });
        $('#ohnoes').css({'height': (h-a-71) });
    });

    // vertical align class
    $(window).bind('load resize', function() {
        $('.vAlign').each(function() {
            var h = $(this).parent().siblings('.vMaster').outerHeight();
            var w = $(this).parent().width();
            $(this).css({ height : h });
            $(this).css({ width : w });
        });
    });

    // browserid
    $('#browserid').bind('click', function(e) {
        e.preventDefault();
        navigator.id.getVerifiedEmail(function(assertion) {
            if (assertion) {
                $('#id_assertion').val(assertion.toString());
                $('#browserid_form').submit();
            }
        });
    });

    // notification bar
    $('#notification_close').bind('click', function(e) {
        e.preventDefault();
        $(this).parents('.notification').fadeOut();
    });
});
