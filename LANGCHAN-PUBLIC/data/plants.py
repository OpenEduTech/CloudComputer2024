import traceback
import uuid

import pymongo
from concurrent.futures import ThreadPoolExecutor
from myrequest import safe_request
from bs4 import BeautifulSoup


def get_frps(cname, base_url='https://www.iplant.cn/frps/ashx/getnamec.ashx'):
    params = {
        't': cname
    }
    res = safe_request('GET', base_url, params=params, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X '
                                                                              '10_15_7) AppleWebKit/537.36 (KHTML, '
                                                                              'like Gecko) Chrome/131.0.0.0 '
                                                                              'Safari/537.36',
                                                                'Host': 'www.iplant.cn', })
    soup = BeautifulSoup(res.text, 'lxml')
    planets = {}
    for a in soup.find_all('a'):
        planets[a.text] = 'https://www.iplant.cn' + a['href']
    return planets


def get_frps_text(cname: str, key:str, href:str, base_url='https://www.iplant.cn/ashx/getfrps.ashx'):
    try:
        params = {
            'key': key
        }
        res = safe_request('GET', base_url, params=params, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X '
                                                                                  '10_15_7) AppleWebKit/537.36 (KHTML, '
                                                                                  'like Gecko) Chrome/131.0.0.0 '
                                                                                  'Safari/537.36',
                                                                    'Host': 'www.iplant.cn', })
        json_data = res.json()
        soup = BeautifulSoup(json_data['frpsdesc'], 'lxml')
        frps_text = {}
        for p in soup.find_all('p'):
            if 97 <= ord(p.text[0]) <= 122 or 65 <= ord(p.text[0]) <= 90:
                continue
            elif len(p.text) <= 30:
                continue
            else:
                text = p.text[:512] if p.text.endswith('。') else find_complete_text(p.text[:512])
                if text == '':
                    continue
                else:
                    frps_text['text'] = text
                    frps_text['href'] = href
                    frps_text['keyword'] = cname
                    frps_text['_id'] = str(uuid.uuid4())
                    save_to_mongo(frps_text)
                    print(frps_text)
    except Exception as e:
        traceback.print_exc()


def find_complete_text(text):
    for i in range(len(text) - 1, -1, -1):
        if text[i] == '。':
            return text[:i + 1]
    return ''


def save_to_mongo(planet):
    collection.insert_one(planet)


if __name__ == '__main__':
    # 连接到mongo数据库
    client = pymongo.MongoClient('localhost', 27017)
    db = client['iplant']
    collection = db['frps']
    # 从A-Z遍历frps植物的索引
    for i in range(68, 91):
        print('正在爬取索引为%s的植物'%chr(i))
        planets = get_frps(chr(i))
        # 多线程爬取植物志
        with ThreadPoolExecutor(max_workers=6) as executor:
            tasks = [executor.submit(get_frps_text, k, v.split('/')[-1].split('?')[0], v) for k, v in planets.items()]