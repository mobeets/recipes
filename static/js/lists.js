
// case insensitive contains
$.extend($.expr[":"], {
"containsNC": function(elem, i, match, array) {
return (elem.textContent || elem.innerText || "").toLowerCase().indexOf((match[3] || "").toLowerCase()) >= 0;
}
});

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
    tag = set_default_item(lochash, 'tag', '').split(',').filter(Boolean);
    query = '';
}

function update_btn_item(name, cur) {
    if (name === 'tag' && Array.isArray(cur)) {
        // Reset all tag buttons to inactive first
        $('.btn-' + name).removeClass('btn-active').addClass('btn-inactive');
        // Then set active state for each selected tag
        cur.forEach(function(tagValue) {
            $('.btn-' + name + '[data-' + name + '="' + tagValue + '"]')
                .removeClass('btn-inactive')
                .addClass('btn-active');
        });
    } else {
        // Handle non-array cases (year, list, loc) as before
        $('.btn-' + name).removeClass('btn-active');
        $('.btn-' + name).addClass('btn-inactive');
        $('.btn-' + name + '[data-' + name + '="' + cur + '"]').removeClass('btn-inactive');
        $('.btn-' + name + '[data-' + name + '="' + cur + '"]').addClass('btn-active');
    }
}

function hide_items_not_matching_attr(name, values) {
    if (name === 'tag' && values.length > 0) {
        $('.media-item').each(function() {
            var item = $(this);
            var hasAllTags = values.every(function(tagValue) {
                return item.find('.btn-tag-' + tagValue).length > 0;
            });
            if (!hasAllTags) {
                item.hide();
            }
        });
    } else if (values.length > 0 && !Array.isArray(values)) {
        $('.media-item').not(':has(.btn-' + name + '-' + values + ')').hide();
    }
}

function hide_titles_with_no_items() {
    $(".list-group:visible").each(function () {
        if ($(this).children(".media-item:visible").length == 0) {
            $(this).hide();
        }
    });
}

function hide_items_not_matching_query(query) {
    if (query.length > 0) {
        obj = $('.media-item').find(".item-title:not(:containsNC('" + query + "'))").parent().parent('.media-item').hide();
    }
}

function show_filter_status() {
    var comment = '';
    list_str = list === 'all' ? 'all entries' : list;
    year_str = year === 'all' ? '' : ' in ' + year;
    if (tag.length > 0) {
        comment += 'tagged "' + tag.join('" AND "') + '"';
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
    // if (query.length > 0) {
    //     comment += ' Ignoring items without the phrase "' + query + '"';
    // }
    $('#filter_status').html(comment);
    $('.btn-clear').click(clear_filters);
}

function update(list, year, tag, loc, query) {
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
    hide_items_not_matching_query(query);
    show_filter_status();
}
