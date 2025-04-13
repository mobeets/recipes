var DEFAULT_YEAR = 'all';
var DEFAULT_LIST = 'all';
var DEFAULT_TAG = [];
var DEFAULT_LOC = '';

var year = 'all'; // '2016';
var list = DEFAULT_LIST;
var tag = DEFAULT_TAG;
var loc = DEFAULT_LOC;
var query = '';

function init() {
    $('#search-box').on('input propertychange paste', update_textbox);
    $('.btn-list').click(update_list);
    $('.btn-tag').click(update_tag);
    $('.btn-clear').click(clear_filters);
    set_default();
    $(".comments").shorten({
        "showChars" : 100,
        "moreText"  : "[+]",
        "lessText"  : "[-]",
    });
    update(list, year, tag, loc, query);
}

function makeUpdateUrl(list, year, tag, loc) {
    url = "#year=" + year + "&list=" + list;
    if (tag.length > 0) url = url + "&tag=" + tag.join(','); // Join array with commas
    if (loc.length > 0) url = url + "&loc=" + loc;
    return url;
}

function clear_filters() {
    year = DEFAULT_YEAR;
    list = DEFAULT_LIST;
    tag = []; // Reset to empty array
    loc = DEFAULT_LOC;
    query = '';
    window.location.href = makeUpdateUrl(list, year, tag, loc);
    update(list, year, tag, loc, query);
    console.log('resetting.');
    console.log(makeUpdateUrl(list, year, tag, loc));
}

function update_tag() {
    var clickedTag = $(this).data('tag');
    var tagIndex = tag.indexOf(clickedTag);
    
    if (tagIndex === -1) {
        // Add tag if not already selected
        tag.push(clickedTag);
        $(this).addClass('btn-active').removeClass('btn-inactive');
    } else {
        // Remove tag if already selected
        tag.splice(tagIndex, 1);
        $(this).addClass('btn-inactive').removeClass('btn-active');
    }
    
    window.location.href = makeUpdateUrl(list, year, tag, loc);
    update(list, year, tag, loc, query);
    return false;
}

function update_list() {
    lastlist = $(this).data('list');
    if (lastlist == list) {
        list = 'all';
    } else {
        list = lastlist;
    }
    window.location.href = makeUpdateUrl(list, year, tag, loc);
    update(list, year, tag, loc, query);
}

function update_textbox() {
    query = $('#search-box').val();
    update(list, year, tag, loc, query);
}

$(document).ready(init);
