from tgflow import TgFlow as tgf
from tgflow import handles as h
from enum import Enum
key='539066078:AAHCUsr8ZoP9JtP5KqOMuL7f_UoFyyH6wik'


class States(Enum):
    START=1
    INFO=2
    FAV=3
    THANKS=4

UI = {
    States.START:
    {'t':'hello',
     'b': [
         {'show info':h.action(States.INFO)},
          {'set my favourite':h.action(States.FAV)}
     ]},
    States.FAV:{
        't':'Please send me name of your favourite thing',
        'react_to':h.action(
            lambda i: (States.THANKS,{'fav':i.text})),
    },
    States.INFO:{
        't':h.st('Your fav is %s','fav'),
        'react':h.action(
            lambda i: (States.THANKS,{'fav':i.text}),
            react_to = 'text'),
    },
    States.THANKS:{
        't':'Thanks! I will remember it',
         'b': [
             {'show info':h.action(States.INFO,update_msg=True)},
          {'set another favourite':h.action(States.FAV,update_msg=True)}
         ]},
    }

tgf.configure(token=key,
                 state=States.START,
                 data={"foo":'bar'})
tgf.start(UI)

"""
from tgflow import TgFlow
from enum import Enum
key='539066078:AAHCUsr8ZoP9JtP5KqOMuL7f_UoFyyH6wik'

class States(Enum):
    START=1

TgFlow.configure(token=key,
                 state=States.START,
                 data={"foo":'bar'})
TgFlow.start({States.START:{'t':'hello'}})
"""