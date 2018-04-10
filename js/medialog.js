var DEFAULT_YEAR = 'all';
var DEFAULT_LIST = 'all';
var DEFAULT_TAG = '';
var DEFAULT_LOC = '';

var year = 'all'; // '2016';
var list = DEFAULT_LIST;
var tag = DEFAULT_TAG;
var loc = DEFAULT_LOC;

function init() {
    $('.btn-list').click(update_list);
    $('.btn-tag').click(update_tag);
    $('.btn-clear').click(clear_filters);
    set_default();
    $(".comments").shorten({
        "showChars" : 100,
        "moreText"  : "[+]",
        "lessText"  : "[-]",
    });
    update(list, year, tag, loc);
}

function makeUpdateUrl(list, year, tag, loc) {
    url = "#year=" + year + "&list=" + list;
    if (tag.length > 0) url = url + "&tag=" + tag;
    if (loc.length > 0) url = url + "&loc=" + loc;
    return url;
}

function clear_filters() {
    year = DEFAULT_YEAR;
    list = DEFAULT_LIST;
    tag = DEFAULT_TAG;
    loc = DEFAULT_LOC;
    window.location.href = makeUpdateUrl(list, year, tag, loc);
    update(list, year, tag, loc);
    console.log('resetting.');
    console.log(makeUpdateUrl(list, year, tag, loc));
}

function update_tag() {
    lasttag = $(this).data('tag');
    if (lasttag == tag) {
        tag = '';
    } else {
        tag = lasttag;
    }
    window.location.href = makeUpdateUrl(list, year, tag, loc);
    update(list, year, tag, loc);
}

function update_list() {
    lastlist = $(this).data('list');
    if (lastlist == list) {
        list = 'all';
    } else {
        list = lastlist;
    }
    window.location.href = makeUpdateUrl(list, year, tag, loc);
    update(list, year, tag, loc);
}

$(document).ready(init);
