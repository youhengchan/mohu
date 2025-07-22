"""
This module provides a Pinyin converter that wraps the pypinyin library.
"""
import re
from typing import List

from pypinyin import Style, pinyin


class PinyinConverter:
    """
    A wrapper for the pypinyin library to handle Chinese character to Pinyin conversion.
    """

    def __init__(self):
        """Initialize the converter with pinyin syllable definitions."""
        # 所有可能的拼音音节（声母+韵母组合）
        self.pinyin_syllables = {
            # 单韵母
            'a', 'o', 'e', 'i', 'u', 'v', 'ai', 'ei', 'ao', 'ou', 'an', 'en', 'ang', 'eng', 'ong',
            # 复韵母
            'ia', 'ie', 'ua', 'uo', 'ue', 've', 'iao', 'iou', 'uai', 'uei', 'ian', 'in', 'uan', 'un', 'iang', 'ing', 'uang', 'ung', 'iong',
            # 带声母的音节
            'ba', 'pa', 'ma', 'fa', 'da', 'ta', 'na', 'la', 'ga', 'ka', 'ha', 'ja', 'qa', 'xa',
            'bo', 'po', 'mo', 'fo', 'lo', 'go', 'ko', 'ho',
            'be', 'pe', 'me', 'de', 'te', 'ne', 'le', 'ge', 'ke', 'he', 'je', 'qe', 'xe',
            'bi', 'pi', 'mi', 'di', 'ti', 'ni', 'li', 'gi', 'ki', 'hi', 'ji', 'qi', 'xi',
            'bu', 'pu', 'mu', 'fu', 'du', 'tu', 'nu', 'lu', 'gu', 'ku', 'hu', 'ju', 'qu', 'xu', 'zu', 'cu', 'su', 'ru', 'zhu', 'chu', 'shu',
            'bai', 'pai', 'mai', 'dai', 'tai', 'nai', 'lai', 'gai', 'kai', 'hai', 'jai', 'zai', 'cai', 'sai', 'zhai', 'chai', 'shai',
            'bei', 'pei', 'mei', 'fei', 'dei', 'nei', 'lei', 'gei', 'kei', 'hei', 'zei', 'sei', 'zhei', 'shei',
            'bao', 'pao', 'mao', 'dao', 'tao', 'nao', 'lao', 'gao', 'kao', 'hao', 'jao', 'rao', 'zao', 'cao', 'sao', 'zhao', 'chao', 'shao',
            'bou', 'pou', 'mou', 'fou', 'dou', 'tou', 'nou', 'lou', 'gou', 'kou', 'hou', 'jou', 'qou', 'xou', 'zou', 'cou', 'sou', 'rou', 'zhou', 'chou', 'shou',
            'ban', 'pan', 'man', 'fan', 'dan', 'tan', 'nan', 'lan', 'gan', 'kan', 'han', 'jan', 'qan', 'xan', 'zan', 'can', 'san', 'ran', 'zhan', 'chan', 'shan',
            'ben', 'pen', 'men', 'fen', 'den', 'nen', 'gen', 'ken', 'hen', 'jen', 'qen', 'xen', 'zen', 'cen', 'sen', 'ren', 'zhen', 'chen', 'shen',
            'bang', 'pang', 'mang', 'fang', 'dang', 'tang', 'nang', 'lang', 'gang', 'kang', 'hang', 'jang', 'qang', 'xang', 'zang', 'cang', 'sang', 'rang', 'zhang', 'chang', 'shang',
            'beng', 'peng', 'meng', 'feng', 'deng', 'teng', 'neng', 'leng', 'geng', 'keng', 'heng', 'jeng', 'qeng', 'xeng', 'zeng', 'ceng', 'seng', 'reng', 'zheng', 'cheng', 'sheng',
            'bong', 'pong', 'mong', 'fong', 'dong', 'tong', 'nong', 'long', 'gong', 'kong', 'hong', 'jong', 'qong', 'xong', 'zong', 'cong', 'song', 'rong', 'zhong', 'chong',
            # 更多常见音节
            'bing', 'ping', 'ming', 'ding', 'ting', 'ning', 'ling', 'ging', 'king', 'hing', 'jing', 'qing', 'xing', 'zing', 'cing', 'sing', 'ring', 'zhing', 'ching', 'shing',
            'biao', 'piao', 'miao', 'fiao', 'diao', 'tiao', 'niao', 'liao', 'giao', 'kiao', 'hiao', 'jiao', 'qiao', 'xiao', 'ziao', 'ciao', 'siao', 'riao', 'zhao', 'chiao', 'shiao',
            'biu', 'piu', 'miu', 'diu', 'tiu', 'niu', 'liu', 'giu', 'kiu', 'hiu', 'jiu', 'qiu', 'xiu', 'ziu', 'ciu', 'siu', 'riu', 'zhiu', 'chiu', 'shiu',
            'bian', 'pian', 'mian', 'dian', 'tian', 'nian', 'lian', 'gian', 'kian', 'hian', 'jian', 'qian', 'xian', 'zian', 'cian', 'sian', 'rian', 'zhian', 'chian', 'shian',
            'biang', 'piang', 'miang', 'diang', 'tiang', 'niang', 'liang', 'giang', 'kiang', 'hiang', 'jiang', 'qiang', 'xiang', 'ziang', 'ciang', 'siang', 'riang', 'zhiang', 'chiang', 'shiang',
            'biong', 'piong', 'miong', 'diong', 'tiong', 'niong', 'liong', 'giong', 'kiong', 'hiong', 'jiong', 'qiong', 'xiong', 'ziong', 'ciong', 'siong', 'riong', 'zhiong', 'chiong', 'shiong',
            # 一些标准拼音音节
            'zhi', 'chi', 'shi', 'ri', 'zi', 'ci', 'si',
            'ya', 'yao', 'ye', 'you', 'yan', 'yin', 'yang', 'ying', 'yong', 'yo', 'yai', 'yei', 'yao', 'you', 'yan', 'yen', 'yang', 'yeng', 'yong',
            'wa', 'wo', 'wai', 'wei', 'wan', 'wen', 'wang', 'weng',
            # 常见的双字拼音组合
            'ping', 'guo', 'bei', 'jing', 'shang', 'hai', 'guang', 'zhou', 'shen', 'zhen', 'cheng', 'du', 'xi', 'an', 'nan', 'jing', 'wu', 'han', 'chang', 'sha', 'kun', 'ming',
            'tai', 'yuan', 'shi', 'jia', 'zhuang', 'hu', 'he', 'hao', 'te', 'yin', 'chuan', 'lan', 'zhou', 'xi', 'ning', 'yin', 'chuan', 'wu', 'lu', 'mu', 'qi', 'ha', 'er', 'bin'
        }
        
        # 按长度排序，优先匹配更长的音节
        self.sorted_syllables = sorted(self.pinyin_syllables, key=len, reverse=True)

    def _is_pinyin_string(self, text: str) -> bool:
        """
        检查文本是否为纯拼音字符串（只包含字母）
        
        Args:
            text: 要检查的文本
            
        Returns:
            如果是纯字母字符串返回True，否则返回False
        """
        return bool(re.match(r'^[a-zA-Z]+$', text))

    def _split_pinyin_string(self, pinyin_str: str) -> List[str]:
        """
        将连续的拼音字符串分割为独立的音节
        
        Args:
            pinyin_str: 连续的拼音字符串，如"pingguo"
            
        Returns:
            分割后的拼音音节列表，如["ping", "guo"]
        """
        if not pinyin_str:
            return []
            
        pinyin_str = pinyin_str.lower()
        result = []
        i = 0
        
        while i < len(pinyin_str):
            matched = False
            # 尝试从当前位置匹配最长的音节
            for syllable in self.sorted_syllables:
                if pinyin_str[i:].startswith(syllable):
                    result.append(syllable)
                    i += len(syllable)
                    matched = True
                    break
            
            if not matched:
                # 如果没有匹配到任何音节，跳过当前字符
                # 这种情况可能是拼写错误或非标准拼音
                result.append(pinyin_str[i])
                i += 1
                
        return result

    def convert(self, word: str, ignore_tones: bool = False) -> List[str]:
        """
        Converts a Chinese word or pinyin string into a list of Pinyin syllables.

        Args:
            word: The Chinese word or pinyin string to convert.
            ignore_tones: If True, the tones will be removed from the Pinyin
                          (e.g., 'běi' -> 'bei'). Defaults to False.

        Returns:
            A list of strings, where each string is a Pinyin syllable.
            Returns an empty list if the input word is empty.
            Non-Chinese characters are returned as is.
        """
        if not word:
            return []

        # 检查是否为纯拼音字符串
        if self._is_pinyin_string(word):
            # 如果是拼音字符串，尝试分割
            return self._split_pinyin_string(word)

        style = Style.NORMAL if ignore_tones else Style.TONE

        # pypinyin returns a list of lists, so we flatten it.
        # e.g., pinyin('北京') -> [['běi'], ['jīng']]
        pinyin_list_of_lists = pinyin(word, style=style, errors='default')
        
        # Flatten the list
        return [item[0] for item in pinyin_list_of_lists] 