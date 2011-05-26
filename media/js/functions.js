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

    // keyboard shortcuts
    $(document.documentElement).keyup(function (event) {
        if (event.keyCode == 71) {
            $('#grid').fadeToggle(100); // G toggles grid
        }
    });
    
});