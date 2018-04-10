
function set_default_item(lochash, name, cur) {
    var val = lochash.substr(lochash.indexOf(name+'='))
      .split('&')[0]
      .split('=')[1];
    return val ? val : cur;
}

function set_default() {
    var lochash = location.hash.substr(1);
    year = set_default_item(lochash, 'year', year);
    list = set_default_item(lochash, 'list', list);
    loc = set_default_item(lochash, 'loc', loc);
    tag = set_default_item(lochash, 'tag', tag);
}

function update_btn_item(name, cur) {
    $('.btn-' + name).removeClass('btn-active');
    $('.btn-' + name).addClass('btn-inactive');
    $('.btn-' + name + '[data-' + name + '="' + cur + '"]').removeClass('btn-inactive');
    $('.btn-' + name + '[data-' + name + '="' + cur + '"]').addClass('btn-active');
}

function hide_items_not_matching_attr(name, cur) {
    if (cur.length > 0) {
        $('.media-item').not(':has(.btn-tag-' + cur + ')').hide();
    }
}

function hide_titles_with_no_items() {
    $(".list-group:visible").each(function () {
        if ($(this).children(".media-item:visible").length == 0) {
            $(this).hide();
        }
    });
}

function show_filter_status() {
    var comment = '';
    list_str = list === 'all' ? 'all entries' : list;
    year_str = year === 'all' ? '' : ' in ' + year;
    if (tag.length > 0) {
        comment += 'tagged "' + tag + '"';
    }
    if (loc.length > 0) {
        comment += 'at "' + loc + '"';
    }
    if (comment.length > 0 || !(list === 'all') || !(year === 'all') ) {
        clear_btn = ' <div class="btn btn-list-item btn-clear">Clear</div>';
        list_str = list === 'all' ? 'all entries' : 'all ' + list;
        year_str = year === 'all' ? '' : ' in ' + year;
        comment = 'Showing ' + list_str + ' ' + comment + year_str + clear_btn;        
    }
    $('#filter_status').html(comment);
    $('.btn-clear').click(clear_filters);
}

function update(list, year, tag, loc) {
    update_btn_item('list', list);
    update_btn_item('year', year);
    update_btn_item('tag', tag);
    update_btn_item('loc', loc);

    $('.media-item').show();
    $('.list-group').hide();
    if (year === 'all' && list === 'all') {
        $(".all").show();
    }
    else if (year === 'all') {
        $("div[id^='" + list + "']").show();
    }
    else if (list === 'all') {
        $("div[id$=" + year + "]").show();
    }
    else {
        $("div[id$=" + list + '-' + year + ']').show();
    }

    hide_items_not_matching_attr('tag', tag);
    hide_items_not_matching_attr('loc', loc);
    hide_titles_with_no_items();
    show_filter_status();
}
