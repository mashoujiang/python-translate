# -*- coding:utf-8 -*-
# Author: Ma, Shoujiang
# Data: 2/20/2018
# Describe: Build a dictionary based on my own needs.

import glob
import os.path
import re

import pandas as pd

import translate_py3 as tl

FILE_DIR = '../Rick_and_Morty'


class Dictionary(object):
    def __init__(self, dic_name):
        if not os.path.isfile(dic_name):
            open(dic_name, 'a').close()

        self.total_words = 0
        self.dic_name = dic_name
        self.columns = ['英', '汉']
        self.pronounce = True
        self.nostorage = False

        try:
            self.dic = pd.read_csv(dic_name)
        except pd.io.common.EmptyDataError:
            self.dic = pd.DataFrame(columns=self.columns, dtype=str)
            self.dic.to_csv(self.dic_name, encoding="utf-8", index=False)

    def read_text(self, file_name):
        with open(file_name, 'r', encoding='utf-8') as file:
            self.extract_words(file)

    def extract_words(self, file):
        words = []
        while True:
            line = file.readline()
            line = line.lower()
            if not line:
                break
            pattern = '[a-zA-Z]+'
            line = re.findall(pattern, line)  # default split is space

            # search if in Dic already.
            for word in line:
                if not self.word_exist(word):
                    words.append(word)
        words = self.delete_duplicate(words)
        word_mean = self.zip_word_and_mean(words)
        self.to_dic(word_mean)

    def word_exist(self, word):
        return True if self.dic['英'][self.dic['英'] == word].size else False

    def delete_duplicate(self, words):
        new_words = list(set(words))
        return new_words

    def zip_word_and_mean(self, words):
        meanings = []
        for word in words:
            meaning = self.translate(word)
            if meaning is None:
                print("Cant get {} meaning".format(word))
            meanings.append(meaning)
        return list(zip(words, meanings))

    def translate(self, word):
        service = None
        webonly = False
        if service:
            webonly = True
        C = tl.Client(word, service=service, webonly=webonly)
        trans = C.translate()
        if trans:
            if not self.nostorage:
                C.updateDB()
        else:
            for service in ['bing', 'youdao', 'iciba']:
                C = tl.Client(word, service=service, webonly=webonly)
                trans = C.translate()
                if trans:
                    break

        return trans

    def to_dic(self, words):
        df = pd.DataFrame(words, columns=self.columns)
        df.to_csv(self.dic_name, mode='a', encoding="utf-8", header=False, index=False)


if __name__ == '__main__':
    dic_name = './Rick_and_Morty_Dictionary.csv'
    dic = Dictionary(dic_name)

    for root, dirs, files in os.walk(FILE_DIR):
        f = glob.iglob(root + '/*.srt')
        for srt in f:
            print(srt)
            dic.read_text(srt)
