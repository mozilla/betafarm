betafarm.admin_links = function() {
    var add, bin, init;
    add = function(el, csrf) {
        $('#addLinkErrorList').detach();
        var parent = el.parent(),
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
            url:el.attr('href'),
            data: {
                'name':name_val,
                'url':url_val,
                'csrfmiddlewaretoken':csrf
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
                var response = $.parseJSON(data.responseText),
                    errors = [],
                    $errorList = $('<ul id="addLinkErrorList" class="errorlist"></ul>');
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
                $.each(errors, function(i, e) {
                    var $link = $('<a class="error"></a>').attr('href', e.href)
                        .append(e.label + ": " + e.msg.toString());
                    $errorList.append($('<li></li>').append($link));
                });
                $('div.addLink').before($errorList);
            }
        });
    };

    bin = function(el, csrf) {
         $.ajax({
            type:'POST',
            url: el.attr('href'),
            data: {
                'csrfmiddlewaretoken':csrf
            },
            success: function() {
                var parent = el.parent();
                parent.fadeOut('slow', function() {
                    parent.remove();
                });
            }
        });
    };

    init = function() {
         $('li.links').bind('click', function(event) {
            var that = $(event.target),
                csrf = that.closest('form').find('input[name=csrfmiddlewaretoken]');
            if (that.hasClass('delete')) {
                bin(that, csrf.val());
                return false;
            }
            if (that.hasClass('add')) {
                add(that, csrf.val());
                return false;
            }
            if (that.hasClass('error')) {
                var input_id = '#' + that.attr('href').split('#')[1];
                $(input_id).focus();
                return false;
            }
         });
    };
        
    return {
        'init': init
    };

}();