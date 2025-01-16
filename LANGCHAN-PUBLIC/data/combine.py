from typing import List, Dict

import pymongo


def merge_same_keyword(plants:List[Dict]):
    # 合并后存到新的collection里
    for plant in plants:
        print(plant)
        document = new_frps.find_one({'keyword': plant['keyword']})
        if document:
            # 更新合并text
            new_frps.update_one({'keyword': plant['keyword']}, {'$set': {'text': document['text'] + plant['text']}})
        else:
            plant['text'] = plant['keyword'] + '，' + plant['text']
            new_frps.insert_one(plant)


if __name__=='__main__':
    client = pymongo.MongoClient('localhost', 27017)
    db = client['iplant']
    frps = db['frps']
    new_frps = db['new_frps']
    documents = list(frps.find())
    merge_same_keyword(documents)
