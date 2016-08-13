# coding=utf-8
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import TransportError
from elasticsearch import helpers
from copy import deepcopy

ES_INDEX = "fb_group_posts"
ES_POST_DOC_TYPE = "post"
ES_NAME_RELATION_DOC_TYPE = "name_relation"
ES_BULK_ACTIONS_SIZE = 500


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


class PostData(object):
    def __init__(self, id_, messages):
        self.id = id_
        self.message = messages


class FLNameData(object):
    def __init__(self, fl_name, post_id):
        self.fl_name = fl_name
        self.post_id = post_id


class FacebookDBHelper(object):
    def __init__(self):
        self.es = Elasticsearch()

    def save_posts(self, group_name, group_domain, posts):
        actions = []

        for post in posts:
            if 'message' in post.keys():
                action = {
                    "_index": ES_INDEX,
                    "_type": ES_POST_DOC_TYPE,
                    "_id": post['id'],
                    "_source": {
                        "message": post['message'],
                        "group_name": group_name,
                        "group_domain": group_domain
                    }
                }

                actions.append(action)

        self.__bulk_insert(actions)

    def save_name_relations(self, relations):
        actions = []

        for relation in relations:
            action = {
                "_index": ES_INDEX,
                "_type": ES_NAME_RELATION_DOC_TYPE,
                "_source": {
                    "fl_name": relation.fl_name,
                    "post_id": relation.post_id
                }
            }

            actions.append(action)

        self.__bulk_insert(actions)

    def __bulk_insert(self, actions):
        actions_list = split_list(list(actions), ES_BULK_ACTIONS_SIZE)

        for acts in actions_list:
            helpers.bulk(self.es, acts)

    def get_post_by_id(self, id):
        return self.__get(doc_type=ES_POST_DOC_TYPE, id=id)

    def get_all_posts(self, doc_type):
        return self.__get_all(doc_type=doc_type)

    def get_all_name_relations(self, doc_type):
        relations = self.__get_all(doc_type=doc_type)

        # noinspection PyTypeChecker
        return [FLNameData(fl_name=r['_source']['fl_name'], post_id=r["_id"]) for r in relations]

    def __get(self, doc_type, id):
        return self.es.get(index=ES_INDEX, doc_type=doc_type, id=id)

    def __get_all(self, doc_type, body=None):
        if body is None:
            body = {}

        result = []

        page = self.es.search(
            index=ES_INDEX,
            doc_type=doc_type,
            scroll='2m',
            search_type='scan',
            size=1000,
            body=body)

        scroll_id = page['_scroll_id']
        scroll_size = page['hits']['total']

        while scroll_size > 0:
            page = self.es.scroll(scroll_id=scroll_id, scroll='2m')

            scroll_id = page['_scroll_id']
            scroll_size = len(page['hits']['hits'])

            result.extend(page['hits']['hits'])

        return result

    def get_all_sources(self, doc_type):
        posts = self.get_all_posts(doc_type=doc_type)
        result = []

        for post in posts:
            if "_source" in post.keys():
                # noinspection PyTypeChecker
                result.append(post["_source"])

        return result

    def get_all_messages(self, doc_type):
        sources = self.get_all_sources(doc_type=doc_type)
        result = []

        for source in sources:
            if 'message' in source.keys():
                # noinspection PyTypeChecker
                result.append(source["message"])

        return result

    def delete_all_posts(self):
        return delete_by_doc_type(
            es=self.es,
            index=ES_INDEX,
            type_=ES_POST_DOC_TYPE)

    def delete_all_name_relations(self):
        return delete_by_doc_type(
            es=self.es,
            index=ES_INDEX,
            type_=ES_NAME_RELATION_DOC_TYPE)

    def get_messages_by_domain(self, domain):
        return self.__get_all(doc_type=ES_POST_DOC_TYPE, body={
            "query": {
                "match": {
                    "domain": {
                        "query": domain,
                        "operator": "and"
                    }
                }
            }
        })

    def get_name_relations_by_fl(self, fl_name):
        return self.__get_all(doc_type=ES_NAME_RELATION_DOC_TYPE, body={
            "query": {
                "match": {
                    "fl_name": {
                        "query": fl_name,
                        "operator": "and"
                    }
                }
            }
        })


def delete_by_doc_type(es, index, type_):
    try:
        count = es.count(index, type_)['count']
        max_count = 5000

        if not count:
            return 0

        tmp_count = count

        while tmp_count > 0:
            tmp_count -= max_count

            response = es.search(
                index=index,
                filter_path=["hits.hits._id"],
                body={"size": max_count,
                      "query": {
                          "filtered": {
                              "filter": {
                                    "type": {"value": type_}
                              }
                          }
                      }})

            if not response:
                return 0

            ids = [x["_id"] for x in response["hits"]["hits"]]

            if not ids:
                return 0

            bulk_body = [
                '{{"delete": {{"_index": "{}", "_type": "{}", "_id": "{}"}}}}'.format(index, type_, x)
                for x in ids]

            es.bulk('\n'.join(bulk_body))
            es.indices.flush_synced([index])

        return count
    except TransportError as ex:
        print("Elasticsearch error: " + ex.error)
        raise ex
