# -*- coding: utf-8 -*-
from group_bot import GroupBot, RepostFilter, SubstringFilter, SignerFilter

bot = GroupBot(group_name='baraholka_msu', black_filters=[RepostFilter()],
               white_filters=[
                   SubstringFilter([u'#куплю',
                                    u'#отдам',
                                    u'#новости',
                                    u'#инструкции',
                                    u'#админжестит',
                                    u'#скандалыинтригирасследования']),
                   SignerFilter([50587618])])
for link in bot.get_bad_posts_links():
    print link
