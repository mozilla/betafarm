betafarm.topic_filters = function() {
    
    var init, filter, display,
        filtered = $('#projectList'),
        holder = $('#projects'),
        info,
        loader = false;

    filter = function(topic, aside) {
        info.find('.current').removeClass('current');
        aside.addClass('current');
        filtered.isotope({
            filter: '.' + topic
        });
    };
   
    display = function(topic, data) {
        var topic_info = $('#' + topic),
            loading;
        if (!loader) {
            loader = $('<div class="message">Loading topic data</div>').appendTo(info);
        }
        if (topic_info.length) {
            filter(topic, topic_info);
        } else {
            loading = window.setTimeout(function() {
                loading = false;
                info.addClass('loading');
            }, 500);
            $.ajax({
                type: 'GET',
                url: data + 'about/',
                success: function(data) {
                    info.prepend(data);
                    filter(topic, $('#' + topic));
                    if (!loading) {
                        info.removeClass('loading');
                    } else {
                        window.clearTimeout(loading);
                    }
                }
            });
        }
    };

    init = function() {
        
        if ($('#all_projects').length) {
            var area = $('section[role=main]');

            info = $('<div id="meta"><div class="close ajax_content"><a class="close" href="#">Show all topics</a></div></div>').prependTo(holder);
                        
            filtered.isotope({
                itemSelector : '.project',
                layoutMode : 'fitRows'
            });
        
            area.bind('click', function(e) {
                var target = $(e.target);
                if (target.is('a.tag')) {
                    holder.addClass('shift');
                    var url = target.attr('href'),
                        chunks = target.attr('href').split('/');
                    display(chunks[chunks.length-2], url);

                    return false;
                }
                if (target.is('a.close')) {
                    holder.removeClass('shift');
                    filtered.isotope({ filter: '*' });
                    return false;
                }
            });
        }
    };
    
    return {
        'init': init
    };
}();