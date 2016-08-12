# coding=utf-8
from copy import deepcopy

from facebook import GraphAPI
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from facebook_database_helper import SimpleFacebookDBHelper

import time as t
import requests


def constant(func):
    # noinspection SpellCheckingInspection
    def funcset(self, value):
        raise TypeError

    # noinspection SpellCheckingInspection
    def funcget(self):
        return func()

    return property(funcget, funcset)


# noinspection PyPep8Naming,PyMethodParameters
class _Const(object):
    @constant
    def FACEBOOK_TOKEN():
        return "1769775703259571|736fc7f9c5dc31707d40709a1d37813b"

    @constant
    def FACEBOOK_POSTS_COUNT():
        return 3000

    @constant
    def ES_INDEX():
        return "fb_group_posts"

    @constant
    def ES_DOC_TYPE():
        return "post"

    @constant
    def ES_BULK_SIZE():
        return 500


CONST = _Const()


def split_list(_list, _count):
    result = []

    if len(_list) == 0:
        return result

    if len(_list) == _count:
        result.append(_list)

        return result

    steps = len(_list) / _count
    tmp_list = deepcopy(_list)

    for i in range(0, steps):
        result.append(tmp_list[0: _count])
        tmp_list = tmp_list[_count: len(tmp_list)]

    if len(tmp_list) != 0:
        result.append(tmp_list)

    return result






class Group(object):
    def __init__(self, name, id, domain):
        self.name = name
        self.id = id
        self.domain = domain



database = Elasticsearch()

graph = GraphAPI(access_token=CONST.FACEBOOK_TOKEN)

groups = [
    Group(name="CNN Politics", id="219367258105115", domain="politics"),
    Group(name="SinoRuss", id="1565161760380398", domain="politics"),
    Group(name="Politics & Sociology", id="1616754815303974", domain="politics"),
    Group(name="CNN Money", id="6651543066", domain="finances"),
    Group(name="MTV", id="7245371700", domain="music"),
    Group(name="CNET", id="7155422274", domain="tech"),
    Group(name="TechCrunch", id="8062627951", domain="tech"),
    Group(name="Sport Addicts", id="817513368382866", domain="sport"),
    Group(name="Pokemon GO", id="1745029562403910", domain="pokemon go")
]


def time():
    return int(round(t.time() * 1000))


def extract_posts_data(posts):
    res = []

    for p in posts['data']:
        res.append(p)

    return res


def prepare_get_posts_request(posts):
    return posts['paging']['next'].replace("limit=25", "limit=100")


def load_posts_pages(posts, max_count):
    res = []
    count = 0

    while True:
        if count > max_count:
            break

        try:
            res.extend(extract_posts_data(posts))

            request = prepare_get_posts_request(posts)

            # print request

            s_time = time()
            posts = requests.get(request).json()
            f_time = time()

            posts_count = len(posts['data'])
            count += posts_count

            print "load page time:", (f_time - s_time), ", page size:", posts_count, ", all count: ", count
        except KeyError:
            break

    print "extracted posts count: ", count
    print "--------------------------------"

    return res


# def save_posts(_group, _posts):
#     actions = []
#
#     for post in _posts:
#         keys = post.keys()
#         message_key_exists = 'message' in keys
#         created_time_exists = 'created_time' in keys
#
#         if message_key_exists and created_time_exists:
#             action = {
#                 "_index": CONST.ES_INDEX,
#                 "_type": CONST.ES_DOC_TYPE,
#                 "_id": post['id'],
#                 "_source": {
#                     "message": post['message'],
#                     "created_time": post['created_time'],
#                     "group_name": _group.name,
#                     "group_domain": _group.domain
#                 }
#             }
#
#             actions.append(action)
#
#     actions_lists = split_list(list(actions), CONST.ES_BULK_SIZE)
#
#     for actions in actions_lists:
#         helpers.bulk(database, actions)

# noinspection PyShadowingNames
def save_group_posts(graph, group):
    s_time = time()
    group_json = graph.get_object(group.id)
    f_time = time()

    print "load group data time: ", str(f_time - s_time)
    print "downloading posts from: ", group_json['name']

    posts = graph.get_connections(group_json['id'], 'feed')
    posts_data = load_posts_pages(posts=posts, max_count=CONST.FACEBOOK_POSTS_COUNT)
    fdb = SimpleFacebookDBHelper(database, CONST.ES_INDEX, CONST.ES_DOC_TYPE)
    fdb.save_posts(group.name, group.domain, posts_data)


def main():
    for group in groups:
        save_group_posts(graph=graph, group=group)

if __name__ == "__main__":
    main()
