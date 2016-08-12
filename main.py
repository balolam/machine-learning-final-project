from elasticsearch import Elasticsearch
import elasticsearch
from facebook_database_helper import SimpleFacebookDBHelper
from facebook_database_helper import NameRelation
from elasticsearch import helpers
import re

FL_NAME_PATTERN_1 = "\s[A-Z]\w+(?:\s[A-Z]\w+?)?\s(?:[A-Z]\w+?)?[\s\.\,\;\:]"
FL_NAME_PATTERN_3 = "[A-Z]\w+(?:\s[A-Z]\w+?)?\s(?:[A-Z]\w+?)?[\s\.\,\;\:]"

FL_NAME_PATTERN_4 = '(?<=\s)([A-Z]{1}\w+\s{1}[A-Z]{1}\w+(?=[\s\.\,\;\:]))'

FL_NAME_PATTERN_2 = "/^(?:[\u00c0-\u01ffa-zA-Z'-]){2,}(?:\s[\u00c0-\u01ffa-zA-Z'-]{2,})+$/i"
# FL_NAME_PATTERN_2 = "([A-Z]{1}[a-z]{1,30}[- ]{0,1}|[A-Z]{1}[- \']{1}[A-Z]{0,1}[a-z]{1,30}[- ]{0,1}|[a-z]{1,2}[ -\']{1}[A-Z]{1}[a-z]{1,30}){2,5}"
patterns = [
    FL_NAME_PATTERN_1
]

fdb = SimpleFacebookDBHelper(
    es=Elasticsearch(),
    index="fb_group_posts",
    post_doc_type="post",
    name_relation_doc_type="fl_name")
fdb.delete_all_name_relations()

print len(fdb.get_name_relations_by_fl("Donald Trump"))
#
# # name_relations = fdb.get_all_name_relations()
# #
# # print name_relations[0].fl_name
# # print len(name_relations)
#
# messages = fdb.get_all_messages()
# posts = fdb.get_all_posts()
# name_relations = []
#
# for post in posts:
#     message = post['_source']['message']
#     names = re.findall(FL_NAME_PATTERN_1, message)
#
#     if names:
#         id = post['_id']
#
#         for name in names:
#             name = name.replace(".", "")
#             relation = NameRelation(fl_name=name, post_id=id)
#             name_relations.append(relation)
#
# result = []
# fdb.save_name_relations(name_relations)
# for message in messages:
#     result.extend(re.findall(FL_NAME_PATTERN_4, message))
#
# es = Elasticsearch()
# es.delete_script()
#
# def delete_es_type(es, index, type_):
#     try:
#         count = es.count(index, type_)['count']
#         response = es.search(
#             index=index,
#             filter_path=["hits.hits._id"],
#             body={"size": count, "query": {"filtered" : {"filter" : {
#                   "type" : {"value": type_ }}}}})
#
#         ids = [x["_id"] for x in response["hits"]["hits"]]
#
#         if len(ids) > 0:
#             return
#
#         bulk_body = [
#             '{{"delete": {{"_index": "{}", "_type": "{}", "_id": "{}"}}}}'
#             .format(index, type_, x) for x in ids]
#         es.bulk('\n'.join(bulk_body))
#         # es.indices.flush_synced([index])
#     except elasticsearch.exceptions.TransportError as ex:
#         print("Elasticsearch error: " + ex.error)
#         raise ex
#
# for r in result:
#     print r
#
# print len(result)
#
# fdb.get_all_posts()
#
# # def main():
# #
# #
# # if __name__ == "__main__":
#     main()