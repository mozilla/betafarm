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
        var a = $('#site_meta').outerHeight();
        $('.wrapper:first').css({ 'min-height' : (h-a) });
        $('#ohnoes').css({'height': (h-a-71) });
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

    // fetch a page of results and cache
    var fetch_and_cache = function(page) {
        $.get(document.URL + page + '/', function(data) {
            $('<div></div>').attr('id', 'activities_page_' + page)
                .append(data).hide().appendTo('body');
        }).error(function() {
            $('button.fetchActivity').detach();
        });
    };

    // fetch more activity
    $('button.fetchActivity').bind('click', function(e) {
        e.preventDefault();

        var page = parseInt($(this).attr('page')) + 1;
        var cached = $('#activities_page_' + page);

        if (!cached.length) {
            $.get(document.URL + page + '/', function(data) {
                $('ul.activityStream').append(data);
            });
        } else {
            $('ul.activityStream').append(cached.html());
        }

        fetch_and_cache(page + 1);
        $('button.fetchActivity').attr('page', page);
    });

    $('li.links').bind('click', function(event) {
        var that = $(event.target),
            csrf = that.closest('form').find('input[name=csrfmiddlewaretoken]');
        if (that.hasClass('delete')) {
            $.ajax({
                type:'POST',
                url: that.attr('href'),
                data: {
                    'csrfmiddlewaretoken':csrf.val()
                },
                success: function() {
                    parent = that.parent();
                    parent.fadeOut('slow', function() {
                        parent.remove();
                    });
                }
            });
            return false;
        }
        if (that.hasClass('add')) {
            $('#addLinkErrorList').detach();
            var parent = that.parent(),
                grand_parent = parent.parent(),
                name = parent.find('input[name=link_name]'),
                name_val = name.val(),
                url = parent.find('input[name=link_url]'),
                url_val = url.val(),
                message = false,
                loading;
            if (!message) {
                message = $('<div class="message">Adding link...</div>').prependTo(grand_parent);
            }
            loading = window.setTimeout(function() {
                loading = false;
                grand_parent.css('visibility','hidden');
                message.css('display','block');
                parent.css('display','none');
                grand_parent.css('visibility','visible');
            }, 500); 
            $.ajax({
                type:'POST',
                url:that.attr('href'),
                data: {
                    'name':name_val,
                    'url':url_val,
                    'csrfmiddlewaretoken':csrf.val()
                },
                success: function() {
                    if (!loading) {
                        message.css('display','none');
                        parent.css('display','block');
                        grand_parent.css('visibility','visible'); 
                    } else {
                        window.clearTimeout(loading);
                    }             
                    $.ajax({
                        type:'GET',
                        url:parent.attr('data-list-links'),
                        success : function(data) {
                            $('ul.yourLinks').replaceWith(data);
                            name.val('');
                            url.val('');
                        }
                    });
                },
                error: function(data) {
                    if (!loading) {
                        message.css('display','none');
                        parent.css('display','block');
                        grand_parent.css('visibility','visible');
                    } else {
                        window.clearTimeout(loading);
                    }
                    var response = $.parseJSON(data.responseText);
                    var errors = [];
                    if (response.hasOwnProperty('url')) {
                        errors.push({
                            'label': 'URL',
                            'msg': response.url,
                            'href': '#id_url'
                        });
                    }
                    if (response.hasOwnProperty('name')) {
                        errors.push({
                            'label': 'Title',
                            'msg': response.name,
                            'href': '#id_title'
                        });
                    }
                    var $errorList = $('<ul></ul>').addClass('errorlist')
                        .attr('id', 'addLinkErrorList');
                    $.each(errors, function(i, e) {
                        var $link = $('<a class="error"></a>').attr('href', e.href)
                            .append(e.label + ": " + e.msg.toString());
                        $errorList.append($('<li></li>').append($link));
                    });
                    $('div.addLink').before($errorList);
                }
            });
            return false;
        }
        if (that.hasClass('error')) {
            var input_id = '#' + that.attr('href').split('#')[1];
            $(input_id).focus();
            return false;
        }
    });
});
