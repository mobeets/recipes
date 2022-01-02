import os
import inspect
import tempfile
import webbrowser
from mako.template import Template
from mako.lookup import TemplateLookup
from send_email import send_email, DEFAULT_RECIPIENTS
from update import least_recent_meals, load_recipes

LIFELOG_FILE = '/Users/mobeets/Box Sync/Projects/Listed/Tracked/lifelog.txt'

BASEDIR = os.path.dirname(os.path.abspath(os.path.join(inspect.stack()[0][1], '..')))
DINNER_DATAFILE = os.path.join(BASEDIR, '_data', 'recipes.yml')
TMP_DINNER_DATAFILE = os.path.join(BASEDIR, '_data', 'recipes_tmp.yml')
DINNER_MAKOFILE = os.path.join(BASEDIR, 'static', 'html', 'dinners.html')
TMP_DINNER_FILE = os.path.join(BASEDIR, 'static', 'html', 'dinners_rendered.html')

# code to update dinner file
MSG_B = 'cd ~/code/recipes'
MSG_C = 'cp {} {}'.format(TMP_DINNER_DATAFILE, '_data/recipes.yml')
MSG_D = 'git add .<br>git commit -m "data update"<br>git push<br>'
UPDATE_CODE = '<br>'.join([MSG_B, MSG_C, MSG_D])

def render(items, msgs, update_code=UPDATE_CODE, makodir=BASEDIR, infile=DINNER_MAKOFILE):
    lookup = TemplateLookup(directories=[makodir])
    return Template(filename=infile, lookup=lookup).render(
        items=items, msgs=msgs, update_code=update_code,
        input_encoding='utf-8', output_encoding='utf-8',
        encoding_errors='replace')

def send_update_email(msg, subj):
    html_msg = '<html><head></head><body>'
    html_msg += msg
    html_msg += '</body></html>'
    recipients = {'addrs': DEFAULT_RECIPIENTS,
        'subject': subj,
        'message': msg,
        'message_html': html_msg,
        }
    send_email(recipients)

def show_html(msg, subj, outfile=TMP_DINNER_FILE):
    with open(outfile, 'w') as f:
        f.write(msg)
    CHROME = webbrowser.get("open -a '/Applications/Google Chrome.app' %s")
    print('file://' + outfile)
    CHROME.open('file://' + outfile, new=2)

def main(debug=True):

    items = least_recent_meals(DINNER_DATAFILE, DINNER_DATAFILE, n=5)
    msgs = load_recipes(LIFELOG_FILE, TMP_DINNER_DATAFILE, prevfile=DINNER_DATAFILE)
    subj = 'Five recipe ideas for this week'
    html = render(items, msgs)
    print(subj)
    print(html)
    if debug:
        show_html(html, subj)
    else:
        send_update_email(html, subj)

if __name__ == '__main__':
    import sys
    do_email = len(sys.argv) > 1 and sys.argv[1] == 'email'
    main(not do_email)
