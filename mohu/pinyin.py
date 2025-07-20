"""
This module provides a Pinyin converter that wraps the pypinyin library.
"""
from typing import List

from pypinyin import Style, pinyin


class PinyinConverter:
    """
    A wrapper for the pypinyin library to handle Chinese character to Pinyin conversion.
    """

    def convert(self, word: str, ignore_tones: bool = False) -> List[str]:
        """
        Converts a Chinese word into a list of Pinyin syllables.

        Args:
            word: The Chinese word to convert.
            ignore_tones: If True, the tones will be removed from the Pinyin
                          (e.g., 'běi' -> 'bei'). Defaults to False.

        Returns:
            A list of strings, where each string is a Pinyin syllable.
            Returns an empty list if the input word is empty.
            Non-Chinese characters are returned as is.
        """
        if not word:
            return []

        style = Style.NORMAL if ignore_tones else Style.TONE

        # pypinyin returns a list of lists, so we flatten it.
        # e.g., pinyin('北京') -> [['běi'], ['jīng']]
        pinyin_list_of_lists = pinyin(word, style=style, errors='default')
        
        # Flatten the list
        return [item[0] for item in pinyin_list_of_lists] 