betafarm.prepare_media = function(loc) {
    var bd = betafarm.data;
    return bd.MEDIA_URL + loc + '?build=' + bd.BUILD_ID; 
};

betafarm.navigation = function() {
    var init;
    init = function() {
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
                parent = current.parent(),
                grand = parent.parent();
            if (grand.is('ul.dropdown') && parent.is(':last-child')) {
                grand.parent().removeClass('hover');
            }
        });
    };

    return {
        'init': init
    };

}();

betafarm.areas = {
    common : [
        {
            elm : '#browserid',
            requires : 'https://browserid.org/include.js',
            onload : function() {
                $('#browserid').bind('click', function(e) {
                    e.preventDefault();
                    navigator.id.getVerifiedEmail(function(assertion) {
                        if (assertion) {
                            $('#id_assertion').val(assertion.toString());
                            $('#browserid_form').submit();
                        }
                    });
                });
            }
        }
    ],
    all_projects : {
        requires : [betafarm.prepare_media('js/include/ext/jquery.isotope.min.js'), betafarm.prepare_media('js/include/betafarm.topic-filters.js')],
        onload : function() {
            betafarm.topic_filters.init();
        }
    },
    dashboard : {
        requires : betafarm.prepare_media('js/include/betafarm.streams.js'),
        onload : function() {
            betafarm.streams.init();
        }
    },
    edit_user : {
        requires : betafarm.prepare_media('js/include/betafarm.admin-links.js'),
        onload : function() {
            betafarm.admin_links.init();
        }
    }
}

$(function($) {
    // sticky footer
    $(window).bind('load resize', function() {
        var h = $(window).height(),
            a = $('#site_meta').outerHeight();
        $('.wrapper:first').css({ 'min-height' : (h-a) });
        $('#ohnoes').css({'height': (h-a-71) });
    });
    // notification bar
    $('#notification_close').bind('click', function(e) {
        e.preventDefault();
        $(this).parents('.notification').fadeOut();
    });
    betafarm.navigation.init();
    betafarm.page.prepare(betafarm.areas.common);
});