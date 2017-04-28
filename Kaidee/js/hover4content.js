$(document).ready(function () {
    popoverOptions = {
        content: function () {
            return $(this).siblings('.my-popover-content').html();
        },
        trigger: 'hover',
        animation: false,
        placement: 'bottom'
    };
    $('.panel-heading').popover(popoverOptions);
    $('.ratingImg').popover(popoverOptions);
});