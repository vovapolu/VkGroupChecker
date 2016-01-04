import time
from datetime import timedelta
import re
import vk

def wait_vk_request(func, timeout=0.333):
    def inner(*args, **kwargs):
        start = time.clock()
        res = func(*args, **kwargs)
        all_time = time.clock() - start
        if all_time < timeout:
            time.sleep(timeout - all_time)
        return res
    return inner

class PostFilter:
    def __call__(self, post, api):
        return True

class RepostFilter(PostFilter):
    def __init__(self, repost_timeout=24):
        self.repost_timeout = repost_timeout

    @wait_vk_request
    def __call__(self, post, bot):
        print "Getting information about {} post...".format(post['id'])
        if post['date'] < time.time() - self.repost_timeout * timedelta(hours=1).total_seconds():
            reposts_ids = [repost['uid'] for repost in
                           bot.api.wall.getReposts(owner_id=-bot.group_id, post_id=post['id'])['profiles']]
            if 'signer_id' in post:
                return post['signer_id'] in reposts_ids
            else:
                return False
        else:
            return True

class SubstringFilter(PostFilter):
    def __init__(self, substrings):
        self.substrings = substrings

    def __call__(self, post, bot):
        return any(substring in post['text'] for substring in self.substrings)

class SignerFilter(PostFilter):
    def __init__(self, ids):
        self.ids = ids

    def __call__(self, post, bot):
        if 'signer_id' in post:
            return post['signer_id'] in self.ids
        else:
            return False

class GroupBot:
    def __init__(self, token, group_name, white_filters, black_filters):
        if group_name is not None and not isinstance(group_name, basestring):
            raise ValueError("group_name must be a string")

        print "Initializing vk session..."
        session = vk.Session(access_token=token)
        self.api = vk.API(session)
        self.group_name = group_name
        print "Getting group information..."
        self.group_id = self.api.groups.getById(group_id=self.group_name)[0]['gid']
        print "Getting last posts..."
        self.posts = self.api.wall.get(domain=self.group_name, offset=0, count=30, filter='all')[1:]
        self.white_filters = white_filters
        self.black_filters = black_filters

    @staticmethod
    def get_link_from_post(post, group_name):
        return "https://vk.com/{group_name}?w=wall{from_id}_{id}".format(group_name=group_name, **post)

    def get_bad_posts(self):
        return [post for post in self.posts
                if all(not white_filter(post, self) for white_filter in self.white_filters) and
                any(not black_filter(post, self) for black_filter in self.black_filters)]

    def get_bad_posts_links(self):
        return [self.get_link_from_post(post, self.group_name) for post in self.get_bad_posts()]

    def remove_posts(self, posts):
        for post in posts:
            print "Deleting post {}...".format(post['id'])
            self.api.wall.delete(owner_id=-self.group_id, post_id=post['id'])

