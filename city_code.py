#encoding:utf-8
from city_code_data import city_code, city_code_re, city_pinyin

class DFA:
    def __init__(self):
        self.root = {}
        self.END = 'end'

    def add_word(self, word):
        '''
        add word to build a trie
        parameter : keyword -> str
        return    : tree -> dict
        '''
        node = self.root
        for c in word:
            node=node.setdefault(c, {})
        node[self.END] = 'yes'
        return self.root
    
    def find_word(self, string, max_match='yes'):
        '''
        find all keywords from a string
        parameter   :  string , max_match(default 'yes')
        return      :  result -> list
        '''
        node = self.root
        result = []
        word_list = []
        for s in string:
            res = node.get(s, {})
            if res:
                word_list.append(s)
                node = res
                if res.get('end', {}) == 'yes':
                    keyword = ''.join(word_list)
                    result.append(keyword)
                    if max_match != 'yes':
                        word_list = []
                        node = self.root
            else:
                word_list = []
                node = self.root
        return result


class CityCode():
    code_name_dict = city_code_re
    def __init__(self):
        self.name_trie = DFA()
        # self.jane_trie = DFA()
        self.pinyin_trie = DFA()
        for city in city_code.keys():
            self.name_trie.add_word(city)
        # for jane in city_jane.values():
        #     self.jane_trie.add_word(jane)
        for pinyin in city_pinyin.values():
            self.pinyin_trie.add_word(pinyin)
        
    def get_code_by_city(self, keywords):
        result = city_code.get(keywords, '')
        fuzzy_name = self.name_trie.find_word(keywords)
        # fuzzy_jane = self.jane_trie.find_word(keywords)
        fuzzy_pinyin = self.pinyin_trie.find_word(keywords)
        if result:
            res = {"code":1, 
                        "result":
                            {
                            keywords:result
                            }
                    } 
            return res
        elif fuzzy_name:
            res = {"code":2,"result":{}}
            name_res = max(fuzzy_name, key=len)
            # for name in fuzzy_name:
            code = city_code.get(name_res)
            res["result"][name_res] = code
            return res
        elif fuzzy_pinyin:
            res = {"code":2,"result":{}}
            pinyin_res = max(fuzzy_pinyin, key=len)
            city_name = list(city_pinyin.keys())[list(city_pinyin.values()).index(pinyin_res)]
            code = city_code.get(city_name)
            res["result"][city_name] = code
            return res
        # elif fuzzy_jane:
        #     res = {"code":2,"result":{}}
        #     for jane in fuzzy_jane:
        #         city_name =  list(city_jane.keys())[list(city_jane.values()).index(jane)]
        #         code = city_code.get(city_name)
        #         res["result"][city_name] = code
        #     return res
        else:
            return {"code":0}

if __name__ == "__main__":
    query = CityCode()
    while 1:
        keywords = input("Please input name:")
        res = query.get_code_by_city(keywords)
        print(res)
