#coding=utf-8
import re
import json
import sys

from ngram import PUNC_SET, load_ngram
from dtopwords import generate_domain_words

dtop_threshold = 0.0004
pat_threshold = 2
def load_temp(temp_path='./corpus/random_select_aver.txt', num=300):
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
    punc_filtered_path = './inter_results/%s.pun_filtered' % src_name
    pat_matched_path = './inter_results/all_matched_words.txt'
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
        output_file.write('%s\t%.6f\t%d\n' % (tu[0], tu[1], pat_matched))

if __name__ == '__main__2':
    filter_by_threshold('./corpus/c4x@TsinghuaX@30240184X.txt', './results/dtop_res.txt', './results/final.txt')

if __name__ == '__main__':
    src_path = sys.argv[1]
    trg_path = sys.argv[2]
    dtop_res_path = './results/test.txt'
    #generate_domain_words(src_path, dtop_res_path)
    filter_by_threshold(src_path, dtop_res_path, trg_path)
