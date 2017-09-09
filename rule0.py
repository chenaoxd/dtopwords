#coding=utf-8
import os
from ngram import generate_all_ngram

CORPUS_DIR = settings.CORPUS_DIR
BIGRAM_PATH = os.path.join(CORPUS_DIR,'/bigram_harmonic_merge_3_10000sms.txt')
TRIGRAM_PATH = os.path.join(CORPUS_DIR, '/trigram_harmonic_merge_3_10000sms.txt')
SEGMENTED_COURSE_TEXT = os.path.join(CORPUS_DIR, '/seged_datastructure.txt')
TEMPS_FILTERED_PATH = os.path.join(CORPUS_DIR, '/tempS_filtered.txt')
TEMPS_FILTERED_NGRAM_PATH = os.path.join(CORPUS_DIR, '/tempS_filtered_ngram.txt')

class Filter(object):
    def __init__(self, typestr):
        self.ftype = typestr
        self.filtered_list = []

        for c in self.ftype:
            if c not in ['a', 'b', 'c']:
                continue
            self.filtered_list.append(ord(c) - ord('a'))

    def filter(self):
        return self.filtered_list

    @property
    def filter_type(self):
        return self.ftype

    @staticmethod
    def load_filter_dict(filter_path):
        filter_dict = {}
        for line in open(filter_path):
            line = line.strip()
            if not line:
                continue
            segs = line.split('\t')
            type_segs = segs[1].split(' ')
            if len(type_segs) == 1:
                filter_dict[segs[0]] = Filter('ab' if len(segs[0].split(' ')) == 2 else 'abc')
            elif type_segs[1] in ['p', 't', 'd']:
                continue
            else:
                filter_dict[segs[0]] = Filter(type_segs[1])
            #print filter_dict[segs[0]].ftype, line
        return filter_dict

    @staticmethod
    def dump_filter_dict(filter_dict, filter_path):
        with open(filter_path, 'w') as filter_file:
            for ngram in filter_dict:
                filter_file.write('%s\t0 %s\n' % (ngram, filter_dict[ngram].filter_type))

class LineMarker(object):
    def __init__(self, src_line):
        self.src_line = src_line
        self.marker = ['s'] * len(src_line.strip().split(' '))

    def add_filtered(self, filtered_list, start):
        for offset in filtered_list:
            self.marker[start + offset] += 'd'

    def process(self, filter_dicts, count_dict):
        segs = self.src_line.split(' ')
        for gram_num in range(3, 1, -1):
            cur_filter_dict = filter_dicts[gram_num]
            for offset in range(0, len(segs) - gram_num + 1):
                current_substr = ' '.join(segs[offset:offset + gram_num])
                if current_substr not in cur_filter_dict:
                    continue
                if current_substr not in count_dict[gram_num]:
                    count_dict[gram_num][current_substr] = 0
                count_dict[gram_num][current_substr] += 1
                #if current_substr == '的 多':
                #    print self.src_line
                self.add_filtered(cur_filter_dict[current_substr].filter(), offset)

        self.processed_lines = []
        cur_line = []
        for i, m in enumerate(self.marker):
            if m != 's':
                if len(cur_line):
                    self.processed_lines.append(' '.join(cur_line))
                cur_line = []
            else:
                cur_line.append(self.src_line.split(' ')[i])
        if len(cur_line):
            self.processed_lines.append(' '.join(cur_line))

def get_tempS_filtered_ngrams(src_path=SEGMENTED_COURSE_TEXT, filtered_path=TEMPS_FILTERED_PATH, ngram_path=TEMPS_FILTERED_NGRAM_PATH):
    bi_filter = Filter.load_filter_dict(BIGRAM_PATH)
    tri_filter = Filter.load_filter_dict(TRIGRAM_PATH)
    filter_dicts = [None,None,bi_filter,tri_filter]
    v1_file = open(filtered_path, 'w')
    count_dict = {2:{},3:{}}
    for line in open(src_path):
        line = line.strip()
        lm = LineMarker(line)
        lm.process(filter_dicts, count_dict)
        v1_file.write('\n'.join(lm.processed_lines) + '\n')

    generate_all_ngram(filtered_path, ngram_path, 3, 0)


if __name__ == '__main__':
    get_tempS_filtered_ngrams()
