$(document).ready(function($) {

    $('.projectList').isotope({
    // options
        itemSelector : '.project',
        layoutMode : 'fitRows'
    });

    $('.tags li, a.close').click(function(){
        var selector = $(this).attr('data-filter');
        $('.projectList').isotope({ filter: selector });
        return false;
    });

    $('.tag').click(function() {
        $('#projects, #topicDescription').addClass('shifted');
    });
    
    $('.tags .apps').click(function() {
        $('.topic.apps').addClass('visible');
        $('.topic.apps').siblings().removeClass('visible');
    });
    
    $('.tags .identity').click(function() {
        $('.topic.identity').addClass('visible');
        $('.topic.identity').siblings().removeClass('visible');
    });
    
    $('.tags .social').click(function() {
        $('.topic.social').addClass('visible');
        $('.topic.social').siblings().removeClass('visible');
    });
    
    $('.tags .platform').click(function() {
        $('.topic.platform').addClass('visible');
        $('.topic.platform').siblings().removeClass('visible');
    });
    
    $('.tags .media').click(function() {
        $('.topic.media').addClass('visible');
        $('.topic.media').siblings().removeClass('visible');
    });
    
    $('.tags .education').click(function() {
        $('.topic.education').addClass('visible');
        $('.topic.education').siblings().removeClass('visible');
    });
    
    $('a.close').click(function() {
        $('#projects, #topicDescription').removeClass('shifted');
    });
    
});