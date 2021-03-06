import tgflow
from enum import Enum
from datetime import datetime
import databases_files
from tgflow.modules import Analytics, Bitrix24

key='539066078:AAHCUsr8ZoP9JtP5KqOMuL7f_UoFyyH6wik'

gsheets_auth_filepath = 'databases_files/client_secret.json'
analytics_tid_filepath = 'databases_files/tid.txt'
bitrix_tokens_filepath = 'databases_files/tokens.txt'
bitrix_creds_filepath = 'databases_files/client_creds.txt'

class States(Enum):
    ERROR = 0
    START = 1
    CHOOSE = 2
    SUCCESS = 3
    PUT = 4
    GET = 5

bitrix_stages_dict = {
    States.ERROR: 'LOSE',
    States.START: 'NEW',
    States.CHOOSE: 'PREPARATION',
    States.SUCCESS: 'FINAL_INVOICE',
    States.PUT: 'PREPAYMENT_INVOICE',
    States.GET: 'EXECUTING',
}

db_api = databases_files.GSheetsApi(gsheets_auth_filepath)
analytics = tgflow.modules.Analytics(analytics_tid_filepath)
bitrix = tgflow.modules.Bitrix24(bitrix_creds_filepath, bitrix_tokens_filepath)

def open_sheet(i, s, **d):
    print('opening sheet \'{}\''.format(i.text))
    try:
        sheet = db_api.open_sheet(i.text)
    except Exception as exc:
        print(exc)
        return States.ERROR, {}

    upd_data = {'sheet': sheet}
    return States.CHOOSE, upd_data

def insert_row(i, s, **d):
    idx, data = i.text.split(maxsplit=1)
    idx = int(idx)
    row = [str(datetime.now())] + [data]
    print ('insert row at index {}'.format(idx))
    try:
        db_api.insert_row(d['sheet'], row, idx)
    except Exception as exc:
        print(exc)
        return States.ERROR, {}

    return States.SUCCESS, {}

def get_all_data(i, s, **d):
    data = db_api.get_all_data(d['sheet'])
    return States.GET, {'data': data}

UI = {
    
    States.START:{
        'text' : ('Hello, I can help you work with Google Spreadsheets. '
                  'Share your sheet with developer@treebo.iam.gserviceaccount.com.' 
                  'Then just send me your spreadsheet name and let\'s get started!'),
        'react' : tgflow.action(open_sheet, react_to='text'),
        'prepare' : [analytics.send_pageview, bitrix.add_lead, bitrix.add_contact, bitrix.add_deal],
    },
    
    States.CHOOSE:{
        'text' : 'What should I do?',
        'buttons' : [
            {'Insert row' : tgflow.action(States.PUT)},
            {'Recieve all data' : tgflow.action(get_all_data)}
        ],
        'prepare' : [analytics.send_pageview, bitrix.update_deal(bitrix_stages_dict[States.CHOOSE])]
    },
    
    States.PUT:{
        'text' : "Please type data as \'<row number> <your data>\'.",
        'buttons' : [{'Back' : tgflow.action(States.CHOOSE)}],
        'react' : tgflow.action(insert_row, react_to = 'text'),       
        'prepare' : [analytics.send_pageview, bitrix.update_deal(bitrix_stages_dict[States.PUT])]
    },
    
    States.SUCCESS:{
        'text' : 'Done successfully!', 
        'buttons' : [{'Continue' : tgflow.action(States.CHOOSE)}],
        'prepare' : [analytics.send_pageview, bitrix.update_deal(bitrix_stages_dict[States.SUCCESS])]
    },
    
    States.GET:{
        'text' : tgflow.handles.st('Here is your data:\n%s', 'data'),
        'buttons' : [{'Continue' : tgflow.action(States.CHOOSE)}],
        'prepare' : [analytics.send_pageview, bitrix.update_deal(bitrix_stages_dict[States.GET])]
    },
    
    States.ERROR:{
        'text':'Sorry there was an error',
        'buttons': [{'Start':tgflow.action(States.START)}],
        'prepare' : [analytics.send_pageview, bitrix.update_deal(bitrix_stages_dict[States.ERROR])]
    }  
}


tgflow.configure(token=key,
                 state=States.START,
                 verbose=True
                )
tgflow.start(UI)
