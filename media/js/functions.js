$(document).ready(function($) {

    // header dropdowns
    $('.mainItem a, ul.dropdown').hover(function() {
        $(this).parent().toggleClass('hover');
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
});