import os
import re
import random
import ruamel.yaml
from datetime import datetime
from ruamel.yaml.scalarstring import DoubleQuotedScalarString

# def update_with_dates(infile, outfile):
#     data = load_meals(infile)
#     for d in data:
#         d['last_date'] = '2017-08-27'
#     write_to_yaml(data, outfile)

def load_meals(infile):
    with open(infile) as f:
        data = ruamel.yaml.round_trip_load(f.read(),
            preserve_quotes=True)
    return data

def least_recent_meals(infile, outfile, n=5, date_key='last_suggested_date'):
    """
    pick the five meals seen least recently
        then update the data to show that they have now been accessed
    """
    data = load_meals(infile)
    data = sorted(data, key=lambda k: datetime.strptime(k[date_key], '%Y-%m-%d'))

    # find items with the smallest date, and pick random n of these
    min_date = data[0][date_key]
    items = [x for x in data if x[date_key] == min_date]
    random.shuffle(items)
    items = items[:n]

    # update date to today
    for item in items:
        item[date_key] = datetime.now().strftime('%Y-%m-%d')
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
    - count: 8
      index: 1
      name: "scallops, oyster mushrooms"
      comments: ...
      tags: ['seafood']
      last_suggested_date: "2017-08-27"

    note: if prev_items are provided,
        only "last_suggested_date" is saved,
        everything else is rewritten
    """
    # load previous items
    if prev_items is None:
        lkp = {}
        index = 0
        nicknames = {}
        last_suggested = {}
    else:
        # lkp = dict((item['name'], item) for item in prev_items)
        # index = max([item['index'] for item in prev_items])
        lkp = {}
        index = 0
        nicknames = dict((item['nickname'], item['name']) for item in prev_items)
        last_suggested = dict((item['name'], item['last_suggested_date']) for item in prev_items)

    # go through matches and convert to items
    for dtstr_of_comment, match in matches[::-1]:
        match, place = match
        if '#' in place:
            url = place.split('#')[1].strip()
            if 'http' not in url:
                url = None
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
            index += 1
            if name in last_suggested:
                dtstr = last_suggested[name]
            else:
                dtstr = '2016-01-01' # default
            lkp[name] = {
                'name': name,
                'comments': [],
                'tags': mark_subitem(subitem) + guess_type(name) + guess_meat(name),
                'last_suggested_date': dtstr,
                'count': 0,
                'index': index,
                'nickname': nickname}
        if len(pieces) > 1:
            comment = pieces[1].replace('\n', '').strip()
            if comment not in lkp[name]['comments']:
                # lkp[name]['comments'].append('[' + dtstr_of_comment + ':] ' + comment)
                citem = {'date': dtstr_of_comment, 'comment': comment}
                if url is not None:
                    citem['url'] = url
                lkp[name]['comments'].append(citem)
        lkp[name]['count'] += 1

    items = lkp.values()
    # sort by index (reversed, so most recent is first)
    items = sorted(items, key=lambda x: x['index'], reverse=True)
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

def describe_changes(items, previtems):
    msgs = []
    nms = dict((x['name'], x) for x in items)
    old_nms = dict((x['name'], x) for x in previtems)
    new_names = list(set(nms.keys()) - set(old_nms.keys()))
    new_names_rev = list(set(old_nms.keys()) - set(nms.keys()))
    if new_names:
        msg = 'Found {} new meals in lifelog: {}'.format(len(new_names), ', '.join(new_names))
        msgs.append(msg)
    if new_names_rev:
        msg = 'Found {} new meals in yaml: {}'.format(len(new_names_rev), ', '.join(new_names_rev))
        msgs.append(msg)

    cmsgs = []
    for nm, val in nms.items():
        if nm in old_nms:
            oldval = old_nms[nm]
            for com in val['comments']:
                if com not in oldval['comments']:
                    msg = 'New comment in "{}": "{}"'.format(nm, com)
                    cmsgs.append(msg)
            for com in val['tags']:
                if com not in oldval['tags']:
                    msg = 'New tag in "{}": "{}"'.format(nm, com)
                    cmsgs.append(msg)
    if cmsgs:
        msgs.append("Updates from lifelog:")
        msgs.extend(cmsgs)

    cmsgs = []
    for nm, val in old_nms.items():
        if nm in nms:
            oldval = nms[nm]
            for com in val['comments']:
                if com not in oldval['comments']:
                    msg = 'New comment in "{}": "{}"'.format(nm, com)
                    cmsgs.append(msg)
            for com in val['tags']:
                if com not in oldval['tags']:
                    msg = 'New tag in "{}": "{}"'.format(nm, com)
                    cmsgs.append(msg)
    if cmsgs:
        msgs.append("Updates from yaml:")
        msgs.extend(cmsgs)
    return msgs

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
    if outfile is not None:
        write_to_yaml(items, outfile)
    return describe_changes(items, previtems)

if __name__ == '__main__':
    infile = '/Users/mobeets/Box Sync/Projects/Listed/Tracked/lifelog.txt'
    outfile = '/Users/mobeets/code/recipes/_data/recipes_tmp.yml'
    prevfile = '/Users/mobeets/code/recipes/_data/recipes.yml'
    msgs = load_recipes(infile, outfile, prevfile)
    for msg in msgs:
        print(msg)
