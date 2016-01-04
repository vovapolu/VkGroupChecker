# -*- coding: utf-8 -*-
import json
import os
from group_bot import RepostFilter, SubstringFilter, SignerFilter, GroupBot

GROUP_CHECKER_CONFIG_NAME = 'config.json'

if os.path.exists(GROUP_CHECKER_CONFIG_NAME):
    CONFIG = json.load(file(GROUP_CHECKER_CONFIG_NAME))
else:
    CONFIG = {'token': file('token.txt').read(),
                            'group_name': 'baraholka_msu',
                            'black_filters': {'RepostFilter': {}},
                            'white_filters': {
                                'SubstringFilter': {'substrings': [
                                    u'#куплю',
                                    u'#отдам',
                                    u'#новости',
                                    u'#инструкции',
                                    u'#админжестит',
                                    u'#скандалыинтригирасследования']},
                                'SignerFilter': {'ids': [50587618]}}}
    json.dump(CONFIG, file(GROUP_CHECKER_CONFIG_NAME, mode='w'))

def create_bot_from_config():
    config = CONFIG
    names_to_filters = {'RepostFilter': RepostFilter,
                        'SubstringFilter': SubstringFilter,
                        'SignerFilter': SignerFilter}

    return GroupBot(token=config['token'],
                    group_name=config['group_name'],
                    black_filters=[names_to_filters[filter](**args)
                                   for filter, args in config['black_filters'].items()],
                    white_filters=[names_to_filters[filter](**args)
                                   for filter, args in config['white_filters'].items()])

