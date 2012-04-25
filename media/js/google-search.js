google.load('search', '1', {style : google.loader.themes.V2_DEFAULT});
google.setOnLoadCallback(function() {
    var customSearchOptions = {};
    var customSearchControl = new google.search.CustomSearchControl(
        '003721718359151553648:qipcq6hq6uy', customSearchOptions);
    customSearchControl.setResultSetSize(google.search.Search.FILTERED_CSE_RESULTSET);
    var options = new google.search.DrawOptions();
    options.enableSearchResultsOnly();
    customSearchControl.draw('cse', options);
    function parseParamsFromUrl() {
        var params = {};
        var parts = window.location.search.substr(1).split('\x26');
        for (var i = 0; i < parts.length; i++) {
            var keyValuePair = parts[i].split('=');
            var key = decodeURIComponent(keyValuePair[0]);
            params[key] = keyValuePair[1] ?
                decodeURIComponent(keyValuePair[1].replace(/\+/g, ' ')) :
                keyValuePair[1];
        }
        return params;
    }

    var urlParams = parseParamsFromUrl();
    var queryParamName = "q";
    if (urlParams[queryParamName]) {
        customSearchControl.execute(urlParams[queryParamName]);
        $('#searchbox').val(urlParams[queryParamName]);
    }
}, true);
