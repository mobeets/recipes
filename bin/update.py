import os
import re
import random
import ruamel.yaml
from datetime import datetime
from ruamel.yaml.scalarstring import DoubleQuotedScalarString

RECIPE_INTRO = """# TEMPLATE (DO NOT ERASE):
#
# - name: "example item"
#   comments:
#   - date: "1/2/21"
#     comment: "your thoughts"
#     url: "https://www.food.com/recipe/traditional-mexican-wedding-cookies-162213"
#   tags: ["dinner", "chicken"]
#
# Notes:
# - Before adding a new item, check to make sure another item with the same name doesn't already exist.
# - For new items, please include one tag from this list: ['drink', 'breakfast', 'dinner', 'dessert', 'bread']
# - If your comment has no url, remove the relevant 'url:' line above entirely
# - You should NOT edit any existing comment (only create new ones)
# - You can ADD existing tags but do not remove any
#
"""

DATE_FORMAT = '%-m/%-d/%y'
DEFAULT_LAST_DT = '2016-01-01' # default

def load_meals(infile):
    with open(infile) as f:
        data = ruamel.yaml.round_trip_load(f.read(),
            preserve_quotes=True)

    # add defaults
    # for row in data:
    #     # if 'last_suggested_date' not in row:
    #     #     row['last_suggested_date'] = DEFAULT_LAST_DT
    #     # if 'count' not in row:
    #     #     row['count'] = 1
    return data

def least_recent_meals(infile, outfile, n=5, date_key='last_suggested_date'):
    """
    pick the five meals seen least recently
        then update the data to show that they have now been accessed
    """    
    items = load_meals(infile)
    # data = sorted(data, key=lambda k: datetime.strptime(k[date_key], DATE_FORMAT))

    # find items with the smallest date, and pick random n of these
    # min_date = data[0][date_key]
    # items = [x for x in data if x[date_key] == min_date]
    random.shuffle(items)
    items = items[:n]

    # update date to today
    # for item in items:
    #     item[date_key] = datetime.now().strftime(DATE_FORMAT)
    write_to_yaml(data, outfile)
    return items

def load_matches(infile, pattern):
    ptn = re.compile(pattern)
    with open(infile) as f:
        matches = re.findall(ptn, f.read())
    return matches

def guess_meat(name):
    name = name.lower()
    meats = []
    for meat in ['chicken', 'beef', 'pork', 'lamb', 'bacon']:
        if meat in name:
            if meat == 'steak':
                meats.append('beef')
            else:
                meats.append(meat)
    return meats

def guess_type(name):
    name = name.lower()
    types = []
    for kind in ['pie', 'cake', 'cookies', 'soup', 'pasta', 'sandwich', 'burger', 'curry', 'salad', 'slow-cook', 'tacos', 'ramen']:
        if kind in name:
            if kind == 'slow-cook':
                types.append('slow-cooker')
            elif kind == 'ramen':
                types.append('soup')
            else:
                types.append(kind)
    return types

def mark_subitem(name):
    if name == 'A':
        return ['drink']
    elif name == 'B':
        return ['breakfast']
    elif name == 'D':
        return ['dinner']
    elif name == 'S':
        return ['dessert']
    elif name == 'Br':
        return ['bread']

def find_dates(infile, matches):
    lines = open(infile).readlines()
    new_matches = []
    if len(matches) == 0:
        return new_matches
    matches = matches[::-1]
    next_match = matches.pop()
    last_dt = None
    for line in lines:
        if not line.startswith(' ') and ':' in line and line.split(':')[0].count('/') == 2:
            last_dt = line.split(':')[0]
            continue
        if all([x in line for x in next_match]):
            new_matches.append((last_dt, next_match))
            if len(matches) == 0:
                return new_matches
            next_match = matches.pop()
    return new_matches

def make_items(matches, prev_items, subitem):
    """
    note: if prev_items are provided,
        only "last_suggested_date" is saved,
        everything else is rewritten
    """
    # load previous items
    if prev_items is None:
        lkp = {}
        nicknames = {}
        # last_suggested = {}
    else:
        # lkp = dict((item['name'], item) for item in prev_items)
        lkp = {}
        nicknames = dict((item.get('nickname', ''), item['name']) for item in prev_items)
        # last_suggested = dict((item['name'], item['last_suggested_date']) for item in prev_items)

    # go through matches and convert to items
    for dtstr_of_comment, match in matches[::-1]:
        match, place = match
        if '#' in place:
            url = place.split(' # ')[1].strip()
            if 'http' not in url:
                url = None
            if url is not None and ' , ' in url:
                url = url.split(' , ')[0]
        else:
            url = None
        # remove people, e.g., (JG)
        if match.startswith('('):
            match = match[match.find(')')+1:]

        # split into name and comment
        pieces = match.split(' | ')
        assert len(pieces) <= 2
        match = pieces[0]
        match = match.strip()#.lower()
        
        # handle nicknames, e.g.:
        # CkP4 == "Cooked>Pastas>Baked penne pasta with roasted vegetables"
        if 'Ck' in match and '==' in match:
            # defining nickname
            assert '>' in match
            nickname = match.split('==')[0].strip()
            match = match[match.rfind('>')+1:]
            if match.endswith('"'):
                match = match[:-1]
            match = match.lower()
            nicknames[nickname] = match
            print('Defined nickname: {} == {}'.format(nickname, match))
        else:
            nickname = ''
        if 'Ck' in match and '==' not in match:
            # using nickname
            if match in nicknames:
                match = nicknames[match]
        name = match.lower()

        # add to lkp; update comments, urls, and count
        if name not in lkp:
            # if name in last_suggested:
            #     dtstr = last_suggested[name]
            # else:
            #     dtstr = DEFAULT_LAST_DT
            lkp[name] = {
                'name': name,
                'comments': [],
                'tags': mark_subitem(subitem) + guess_type(name) + guess_meat(name),
                # 'last_suggested_date': dtstr,
                # 'count': 0,
                # 'nickname': nickname
                }
        if len(pieces) > 1:
            comment = pieces[1].replace('\n', '').strip()
        else:
            comment = ''
        if dtstr_of_comment not in [x['date'] for x in lkp[name]['comments']]:
            # lkp[name]['comments'].append('[' + dtstr_of_comment + ':] ' + comment)
            citem = {'date': dtstr_of_comment, 'comment': comment}
            if url is not None:
                citem['url'] = url
            lkp[name]['comments'].append(citem)
        # lkp[name]['count'] += 1

    items = list(lkp.values())
    return items

def write_to_yaml(items, outfile):
    """
    write list of dicts to yaml file,
        ensuring all strings (but not the keys) are double-quoted
    """
    for item in items:
        for key in item:
            if key in ['name', 'nickname']:
                item[key] = DoubleQuotedScalarString(item[key])
            # elif key in ['comments', 'recipe_urls', 'tags']:
            elif key in ['recipe_urls', 'tags']:
                item[key] = [DoubleQuotedScalarString(v) for v in item[key]]
            elif key == 'comments':
                for i,subitem in enumerate(item[key]):
                    for subkey in subitem:
                        item[key][i][subkey] = DoubleQuotedScalarString(item[key][i][subkey])
    with open(outfile, 'w') as f:
        ruamel.yaml.round_trip_dump(items, f,
            default_flow_style=False, width=100000)
    # now prepend with RECIPE_INTRO
    with open(outfile, 'r') as f:
        contents = f.read()
    with open(outfile, 'w') as f:
        f.write(RECIPE_INTRO + contents)

def describe_changes(items, previtems):
    msgs = []
    nms = dict((x['name'], x) for x in items)
    old_nms = dict((x['name'], x) for x in previtems)
    new_names = list(set(nms.keys()) - set(old_nms.keys()))
    new_names_rev = list(set(old_nms.keys()) - set(nms.keys()))
    if new_names:
        msg = 'Found {} new meal(s) in lifelog: {}'.format(len(new_names), ', '.join(new_names))
        msgs.append(msg)

    for nm, val in nms.items():
        if nm in old_nms:
            oldval = old_nms[nm]
            for com in val['comments']:
                if com not in oldval['comments']:
                    comstr = ' | '.join([y for x,y in com.items()])
                    msg = 'New comment in "{}": "{}"'.format(nm, comstr)
                    msgs.append(msg)
            for com in val['tags']:
                if com not in oldval['tags']:
                    msg = 'New tag in "{}": "{}"'.format(nm, com)
                    msgs.append(msg)
    if msgs:
        msgs = ["Updates from lifelog (jay):"] + msgs
    return msgs

def sort_recipes(items):
    # sort comments by most recently updated
    comment_to_dt = lambda x: datetime.strptime(x['date'], DATE_FORMAT.replace('%-','%'))
    for item in items:
        item['comments'] = sorted(item['comments'], key=comment_to_dt, reverse=True)

    # sort by most recently updated
    items = sorted(items, key=lambda item: max([comment_to_dt(x) for x in item['comments']]), reverse=True)
    return items

def tag_recipes(items):
    """
    this will allow autotagging for items added directly to yaml
    """
    for item in items:
        new_tags = guess_type(item['name']) + guess_meat(item['name'])
        item['tags'] = list(set(item['tags'] + new_tags))
    return items

def look_for_new_items_in_previtems(items, previtems):
    nms = dict((x['name'], x) for x in items)
    old_nms = dict((x['name'], x) for x in previtems)
    new_names = list(set(nms.keys()) - set(old_nms.keys()))
    new_names_rev = list(set(old_nms.keys()) - set(nms.keys()))

    msgs = []
    if new_names_rev:
        items.extend([old_nms[new_name] for new_name in new_names_rev])
        msg = 'Found {} new meal(s): {}'.format(len(new_names_rev), ', '.join(new_names_rev))
        msgs.append(msg)

    for nm, val in old_nms.items():
        if nm in nms:
            oldval = nms[nm]
            for com in val['comments']:
                # match comments by date
                if com['date'] not in [c['date'] for c in oldval['comments']]:
                    oldval['comments'].append(com)
                    comstr = ' | '.join([y for x,y in com.items()])
                    msg = 'New comment in "{}": "{}"'.format(nm, comstr)
                    msgs.append(msg)
            for tag in val['tags']:
                if tag not in oldval['tags']:
                    oldval['tags'].append(tag)
                    msg = 'New tag in "{}": "{}"'.format(nm, tag)
                    msgs.append(msg)
    if msgs:
        msgs = ["Updates from yaml (jess):"] + msgs
    return items, msgs

def load_recipes(infile, outfile, prevfile=None):
    if prevfile is not None:
        previtems = load_meals(prevfile)
    else:
        previtems = []
    subitems = ['A', 'B', 'D', 'S', 'Br']
    items = []
    for subitem in subitems:
        pattern = '\{C\}\[' + subitem + '\](.*)@(.*)'
        matches = load_matches(infile, pattern)
        new_matches = find_dates(infile, matches)
        assert len(matches) == len(new_matches), "could not find dates of all comments"
        citems = make_items(new_matches, previtems, subitem)
        items.extend(citems)

    print("Found {} recipes ({} new).".format(len(items), len(items)-len(previtems)))
    msgs = describe_changes(items, previtems)

    items, msgs2 = look_for_new_items_in_previtems(items, previtems)
    items = sort_recipes(items)
    items = tag_recipes(items)

    if outfile is not None:
        write_to_yaml(items, outfile)
    return msgs + msgs2

if __name__ == '__main__':
    infile = '/Users/mobeets/Box Sync/Projects/Listed/Tracked/lifelog.txt'
    outfile = '/Users/mobeets/code/recipes/_data/recipes_tmp.yml'
    prevfile = '/Users/mobeets/code/recipes/_data/recipes.yml'
    msgs = load_recipes(infile, outfile, prevfile)
    for msg in msgs:
        print(msg)
