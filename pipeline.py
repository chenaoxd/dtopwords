#coding=utf-8
import re
import json
import sys
import settings
import os

from ngram import PUNC_SET, load_ngram
from dtopwords import generate_domain_words
from rule0 import get_tempS_filtered_ngrams

dtop_threshold = settings.DTOP_THRESHOLD
pat_threshold = settings.PATTERN_THRESHOLD
FILTER_BY_TEMP2 = settings.USE_RULE0
CORPUS_DIR = settings.CORPUS_DIR

INTER_PATH = os.path.join('.', 'inter_results')

def load_temp(temp_path=os.path.join(CORPUS_DIR, 'random_select_aver.txt'), num=300):
    temp_dict = {}
    count = 0
    for line in open(temp_path).readlines():
        line = line.strip()
        segs = line.split('\t')
        if any([a.decode('utf-8') in PUNC_SET for a in segs[0].split('__')]):
            #print line
            continue
        temp_dict[segs[0]] = float(segs[1])
        count += 1
        if count >= num:
            break

    return temp_dict

def get_all_matched_words(context_dict, src_path, trg_path):
    word_dict = {}
    for i, line in enumerate(open(src_path)):
        if i % 1000 == 0:
            print i
        line = line.strip()
        #print line
        for temp in context_dict:
            ts = temp.split('__')
            m = re.finditer(ts[0] + '.*?' + ts[1], line)
            for a in m:
                word = a.group(0)[len(ts[0]):-len(ts[1])]
                if word not in word_dict:
                    word_dict[word] = 0
                word_dict[word] += 1
    output_file = open(trg_path, 'w')
    for tu in sorted(word_dict.items(), key=lambda x:x[1], reverse=True):
        output_file.write('%s\t%d\n' % (tu[0], tu[1]))

def filter_by_threshold(src_path, dtop_path, trg_path):

    src_name = src_path.split('/')[-1]
    punc_filtered_path = os.path.join(INTER_PATH, '%s.pun_filtered' % src_name)
    pat_matched_path = os.path.join(INTER_PATH, 'all_matched_words.txt')
    #dtop_path = './results/3024.txt'
    temp_dict = load_temp()
    get_all_matched_words(temp_dict, punc_filtered_path, pat_matched_path)


    #pat_matched_path = './inter_results/all_matched_words.txt'
    matched_words = load_ngram(pat_matched_path)
    dtop_words = load_ngram(dtop_path, order=True)

    output_file = open(trg_path, 'w')

    for tu in dtop_words:
        pat_matched = matched_words.get(tu[0].replace(' ', ''),0)
        #print tu[1] * pat_matched , dtop_threshold * pat_threshold
        if tu[1] * pat_matched < dtop_threshold * pat_threshold:
            continue
        #output_file.write('%s\t%.6f\t%d\n' % (tu[0], tu[1], pat_matched))
        output_file.write('%s\t%.6f\n' % (tu[0], tu[1]))

def filter_by_tempS(seged_file_path, trg_path):

    def add_spaces(line):
        return ' '.join([a.encode('utf-8') for a in list(line.decode('utf-8'))])

    get_tempS_filtered_ngrams(seged_file_path, CORPUS_DIR + '/tempS_filtered.txt', CORPUS_DIR + '/tempS_filtered_ngram.txt')
    temps_filtered_ngrams = load_ngram(CORPUS_DIR + '/tempS_filtered_ngram.txt')
    key_set = set([add_spaces(a.replace(' ','')) for a in temps_filtered_ngrams])

    previous_ngrams_list = load_ngram(trg_path, order=True)
    trg_file = open(trg_path, 'w')
    for tu in previous_ngrams_list:
        if tu[0] not in key_set:
            continue
        trg_file.write('%s\t%.6f\n' % (tu[0], tu[1]))

if __name__ == '__main__2':
    filter_by_threshold('./corpus/c4x@TsinghuaX@30240184X.txt', './results/dtop_res.txt', './results/final.txt')

if __name__ == '__main__':
    src_path = sys.argv[1]
    trg_path = sys.argv[2]
    if FILTER_BY_TEMP2:
        seged_file_path = sys.argv[3]
    dtop_res_path = os.path.join(settings.ROOT_DIR, 'results/dtop_res.txt')
    generate_domain_words(src_path, dtop_res_path)
    filter_by_threshold(src_path, dtop_res_path, trg_path)

    if FILTER_BY_TEMP2:
        filter_by_tempS(seged_file_path, trg_path)
