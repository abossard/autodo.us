$(function () {
    // if the function argument is given to overlay, it is assumed to be the onBeforeLoad event listener
    $("a[rel]").overlay(function () {
        // grab wrapper element inside content
        var wrap = this.getContent().find("div.wrap");

        // load only for the first time it is opened
        if (wrap.is(":empty")) {
            wrap.load(this.getTrigger().attr("href"));
        }
    });
});