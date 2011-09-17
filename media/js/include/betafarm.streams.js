betafarm.streams = function() {
    var fetch, init,
        loader = false;
    fetch = function(el, bucket) {
        var ajax_url = el.attr('href'),
            max_entries = bucket.attr('data-total-entries'),
            loading;
        if (!loader) {
            loader = $('<div class="message"><b>Loading older entries</b></div>').insertBefore(el);
        }
        loading = window.setTimeout(function() {
            loading = false;
            loader.css('display','block');
            el.css('display','none');
        }, 500);
        $.ajax({
            type:'GET',
            url: ajax_url,
            success: function(data) {
                bucket.append(data);
                var current_total = bucket.find('li').length,
                    more = current_total < max_entries;
                if (more) {
                    var page = parseInt(ajax_url.replace(/[^\d]+/,''), 10),
                        new_url = ajax_url.replace(/[\d]+/, page + 1);
                        el.attr('href',new_url);
                } else {
                    el.remove();
                }
                if (!loading) {
                    loader.css('display', 'none');
                    el.css('display','block');
                } else {
                    window.clearTimeout(loading);
                }
            }
        });
    };

    init = function() {
        $('a.fetchActivity').bind('click', function() {
            var current = $(this),
                ajax_hole = $('ul.activityStream');
            fetch(current, ajax_hole);
            return false;
        });
    };
    
    return {
        'init': init
    };

}();