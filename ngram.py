# coding=utf-8
import os
import sys
import shelve
#import MySQLdb
import operator
#from helper import stanford_seg
import unicodedata
import settings

#db = MySQLdb.connect(host='localhost', user='root', passwd='', db='test_ngram', charset='utf8')
#dc = db.cursor()
PUNC_SET = set(u'!#$%&()*+,-./:;<=>?@[\]^_`{|}~＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～､　、〜〟〰〾〿–—„…‧﹏﹑﹔·！？｡。□．×℃°ｔ′ｘ…∶∠→．△Ｉ≤‖±●Δ∞∈％≥。，？√﹟<"《》“”．％—…』『／’‘Ｉ（）．％「」─〔？【】．…⦅\'')

ROOT_PATH = settings.ROOT_DIR
TEXT_PATH = os.path.join(ROOT_PATH, 'swig/data/pieces/')
SOURCE_PATH = os.path.join(ROOT_PATH, 'corpora/swig-20150322.txt')

def generate_punc_filtered_corpus(src_path, trg_path, splitor=' '):
    src_text = open(src_path)
    processed_lines = []
    for line in src_text:
        line = line.decode('utf-8')
        # convert full-width characters to half-width characters
        line = unicodedata.normalize('NFKC', line)
        line = line.encode('utf-8')
        processed_lines += preprocess_line(line, splitor=splitor)
    with open(trg_path, 'w') as punc_filtered_file:
        punc_filtered_file.write('\n'.join(processed_lines) + '\n')

def preprocess_line(line, splitor=' '):
    filter_characters = PUNC_SET
    line = line.strip().decode('utf-8')
    #print '[src_line]>>>', line
    line = unicodedata.normalize('NFKC', line)
    if splitor != '':
        segs = line.strip().split(splitor)
    else:
        segs = [a for a in list(line)]

    for i, seg in enumerate(segs):
        if seg in filter_characters:
            segs[i] = '[PUNC]'
        elif seg == u'...':
            segs[i] = '[PUNC]'
        elif seg == u' ' and splitor=='':
            segs[i] = '[PUNC]'
    converted_line = [a.strip().encode('utf-8') for a in (splitor.join(segs)).split('[PUNC]') if a.strip()]
    return converted_line

def add_line_boundaries(src_path, trg_path, start_symbol='[START]', end_symbol='[END]'):
    trg_file = open(trg_path, 'w')
    for line in open(src_path):
        line = line.strip()
        trg_file.write('%s %s %s\n' % (start_symbol, line, end_symbol))

def split_file(file_path, output_dir, piece_gega_bytes=5):
    piece_bytes = piece_gega_bytes * 1000000000
    #print '[START] split file...'
    if not output_dir.endswith('/'):
        output_dir += '/'

    if not output_dir.startswith('/tmp/'):
        print 'ERROR: output_dir must in /tmp/ directory'
        return

    if os.path.exists(output_dir):
        os.system('rm -rf ' + output_dir)
        os.system('rm -rf ' + output_dir[:-1] + '_ngram/')

    os.system('mkdir ' + output_dir)
    os.system('mkdir ' + output_dir[:-1] + '_ngram/')


    os.system('split -b ' + str(int(piece_bytes)) + ' ' + file_path + ' ' + output_dir)
    #print '[END] split file...'

def not_preprocess(line):
    return line

def convert_preprocess(line):
    filter_characters = PUNC_SET
    line = line.decode('utf-8')
    segs = line.strip().split(' ')
    for i, seg in enumerate(segs):
        if seg in filter_characters:
            segs[i] = '[PUNC]'
    segs = ['[START]'] + segs + ['[END]']
    return ' '.join(segs).encode('utf-8')

def not_filter(tu):
    return True

def default_filter(tu):
    filter_characters = PUNC_SET
    #filter_characters = set(u'的是个就有一也这在把是呢吗了要着还></#&()\',+-*!@$%^?，。、“”《》…？！（）：＂×．—－─')
    filter_word = set([u'那么',u'我们', u'可以', u'所以', u'这样', u'这个', u'另外', u'一个'])
    filter_characters |= filter_word
    segs = [c.decode('utf-8') for c in tu[0].split(' ')]
    if any((c in filter_characters) for c in segs):
        return False
    return True

def punctuation_filter(tu):
    filter_characters = PUNC_SET
    filter_word = set([])
    filter_characters |= filter_word
    try:
        segs = [c.decode('utf-8') for c in tu[0].split(' ')]
    except:
        print tu[0], 'with encoding error ...'
        return False

    #try:
    #    segs = [c.decode('utf-8') for c in tu[0].split(' ')]
    #except:
    #    segs = [c for c in tu[0].split(' ')]
    if any((c in filter_characters) for c in segs):
        return False
    return True

def get_ngram(gram_num, file_path, output_path, filter_num=0, preprocessor=not_preprocess, splitor=' '):
    ngram_dict = {}
    ngram_file = open(output_path, 'w')
    with open(file_path, 'r') as text_file:
        counter = 0
        for line in text_file:
            line = line.strip()
            if line == '':
                continue
            line = preprocessor(line)
            if splitor != '':
                segs = line.split(splitor)
            else:
                segs = [a.encode('utf-8') for a in list(line.decode('utf-8'))]

            for index in range(0, len(segs) - gram_num + 1):
                ngram = ' '.join(segs[index:index + gram_num])
                #print ngram
                if ngram not in ngram_dict:
                    ngram_dict[ngram] = 0
                ngram_dict[ngram] += 1

            if counter % 100000 == 0:
                ''
                #print counter
            counter += 1

    counter = 0
    for key,value in ngram_dict.iteritems():
        if value <= filter_num:
            continue
        ngram_file.write(key + '\t' + str(value) + '\n')

        if counter % 10000 == 0:
            ''
            #print counter
        counter += 1

    ngram_file.close()

# Not in use
def merge_ngram_file_with_mysql(ngram_file_list, db_path):
    total_db = shelve.open(db_path)
    for ngram_file_path in ngram_file_list:
        print '[Processing]', ngram_file_path
        ngram_file = open(ngram_file_path,'r')
        for line in ngram_file:
            line = line.strip()
            try:
                key,value = line.split('\t')
            except:
                print "[ERROR]", line

            try:
                key_utf8 = key.decode('utf-8')
            except:
                print "[ERROR KEY]", key
                continue
            dc.execute(u"select * from tb2 where gram='%s'" % key_utf8)
            row = dc.fetchone()
            if row:
                old_val = row[1]
                cur_val = old_val + int(value)
                dc.execute(u"update tb2 set fre=%d where gram='%s'" % (cur_val, key_utf8))
            else:
                dc.execute(u"insert into tb2 (gram, fre) VALUES ('%s', %d)" % (key_utf8, int(value)))
        db.commit()

def merge_ngram_file(ngram_file_list, output_path, sort=False, filter_function=not_filter, merge=False):
    '''
    Sample fromat of ngram_file_list: [(name, path), (name, path), ...]
    '''
    ngram_dict = {}
    for ngram_file_path in ngram_file_list:
        with open(ngram_file_path, 'r') as ngram_file:
            for line in ngram_file:
                line = line.strip()
                segs = line.split('\t')
                if segs[0] not in ngram_dict:
                    ngram_dict[segs[0]] = 0
                try:
                    ngram_dict[segs[0]] += int(segs[1])
                except:
                    print line

    with open(output_path, 'w') as output_file:
        if not sort:
            for key, value in ngram_dict.iteritems():
                if not filter_function((key, value)):
                    continue
                if merge:
                    key = key.replace(' ', '')
                output_file.write(key + '\t' + str(value) + '\n')
        else:
            ngram_sorted = sorted(ngram_dict.items(), key=operator.itemgetter(1), reverse=True)
            for tu in ngram_sorted:
                if not filter_function(tu):
                    continue
                key = tu[0]
                value = tu[1]
                if merge:
                    key = key.replace(' ', '')
                output_file.write(key + '\t' + str(value) + '\n')

def generate_large_ngram(file_path, gram_num=2):
    tmp_dir = '/tmp/test_ngram_pieces/'
    piece_ngram_dir = '/tmp/test_ngram_pieces_ngram/'

    # split file to 5g pieces
    split_file(file_path, tmp_dir, 0.003)

    # generate piece ngram files
    piece_file_list = [(f, os.path.join(tmp_dir, f)) for f in os.listdir(tmp_dir)]
    piece_ngram_list = []

    for piece_file_tuple in piece_file_list:
        piece_file_name = piece_file_tuple[0]
        piece_file_path = piece_file_tuple[1]
        piece_ngram_path = piece_ngram_dir + piece_file_name + '_n' + str(gram_num)
        piece_ngram_list.append(piece_ngram_path)
        get_ngram(gram_num, piece_file_path, piece_ngram_path)

    merge_ngram_file_with_mysql(piece_ngram_list, './test_30m_fre')

def generate_large_ngram_by_filtering(file_path, output_path,  gram_num=3, filter_num=3, sort=False, filter_function=not_filter,merge=False, preprocessor=not_preprocess, splitor=' '):
    import os

    tmp_dir = '/tmp/large_ngram_pieces_%s/' % os.path.basename(file_path)
    piece_ngram_dir = '/tmp/large_ngram_pieces_%s_ngram/' % os.path.basename(file_path)

    # split file to 5g pieces

    split_file(file_path, tmp_dir, 5)

    # generate pieces ngram files
    piece_file_list = [(f, os.path.join(tmp_dir, f)) for f in os.listdir(tmp_dir)]
    piece_ngram_list = []

    for piece_file_tuple in piece_file_list:
        piece_file_name = piece_file_tuple[0]
        piece_file_path = piece_file_tuple[1]
        piece_ngram_path = piece_ngram_dir + piece_file_name + '_n' + str(gram_num)
        piece_ngram_list.append(piece_ngram_path)
        get_ngram(gram_num, piece_file_path, piece_ngram_path, filter_num=filter_num, preprocessor=preprocessor, splitor=splitor)

    merge_ngram_file(piece_ngram_list, output_path, sort, filter_function,merge)

def remove_frequency(file_path, output_path, fre_threshold=None):
    if output_path == None:
        output_path = file_path + '_fre_removed'
    with open(file_path) as input_file:
        with open(output_path,'w') as output_file:
            for line in input_file:
                line = line.strip()
                line_fre = int(line.split('\t')[1])
                if fre_threshold:
                    if line_fre < fre_threshold:
                        continue
                output_file.write(line.split('\t')[0] + '\n')

def seg_file(file_path, output_path):
    output_file = open(output_path, 'w')
    with open(file_path) as input_file:
        for line in input_file:
            line = line.strip()
            seged_line = stanford_seg(line)
            output_file.write(seged_line.encode('utf-8') + '\n')

def ngram_count(input_file_path, output_file_path, gram_num, filter_num, merge=False, filter_function=punctuation_filter, preprocessor=not_preprocess):
    generate_large_ngram_by_filtering(input_file_path, output_file_path, gram_num=gram_num, filter_num=filter_num, sort=True, filter_function=filter_function, merge=merge, preprocessor=preprocessor)

def load_ngram(ngram_file_path, order=False, threshold=0):
    ngram_dict = {}
    with open(ngram_file_path) as ngram_file:
        for line_num, line in enumerate(ngram_file):
            line = line.strip()
            try:
                ngram, gram_count = line.split('\t')
            except:
                print 'Error in file <%s>[%d]: %s' %(ngram_file_path, line_num, line)
                continue
            if float(gram_count) < threshold:
                continue
            ngram_dict[ngram] = float(gram_count)
    if not order:
        return ngram_dict
    else:
        return sorted(ngram_dict.items(), key=operator.itemgetter(1), reverse=True)

def remove_ngram_punc(src_path, trg_path):
    trg_file = open(trg_path, 'w')
    count = 0
    with open(src_path) as src_file:
        for line in src_file:
            if count % 100000 == 0:
                print count
            line = line.strip()
            if not punctuation_filter(line.split('\t')):
                continue
            trg_file.write(line + '\n')
            count += 1

def load_ngram_nopunc(ngram_file_path, threshold=0):
    total = 0
    count = 0
    # 61643979 yuwei
    # 15361936 pku
    ngram_dict = {}
    with open(ngram_file_path) as ngram_file:
        for line in ngram_file:
            if count % 100000 == 0:
                print count
            line = line.strip()
            ngram, fre = line.split('\t')
            if not punctuation_filter((ngram, fre)):
                continue
            total += float(fre)
            if float(fre) <= threshold:
                break
            #ngram_dict[ngram] = int(fre)
            count += 1

    #print total
    return ngram_dict

def get_ngram_meta(ngram_file_path, threshold=0):
    total = 0
    remaining = 0
    line_count = 0
    not_count = False

    with open(ngram_file_path) as ngram_file:
        for line in ngram_file:
            #if line_count % 100000 == 0:
            #    print line_count
            line = line.strip()
            ngram, fre = line.split('\t')
            total += float(fre)
            if float(fre) <= threshold and not not_count:
                remaining = total
                not_count = True
            line_count += 1
    if not not_count:
        remaining = total

    meta = {
        'total': total,
        'remaining': remaining,
        'line_num': line_count,
        'rate': float(remaining) / total
    }
    return meta

def load_ngram_pro(ngram_file_path, threshold=0, multi=1000000):
    ngram_meta = get_ngram_meta(ngram_file_path, threshold)
    ngram_dict = load_ngram(ngram_file_path, threshold=threshold)
    ngram_pro, smooth = convert_ngram_to_pro(ngram_dict, ngram_meta['remaining'], ngram_meta['total'], ngram_meta['line_num'], multi=multi)
    return ngram_pro, smooth

def convert_score_to_rank(ngram_pro):
    sorted_pro = sorted(ngram_pro.items(), key=lambda x:x[1], reverse=True)
    rank_dict = {}
    prev_rank = 0
    for i, tu in enumerate(sorted_pro):
        #print sorted_pro[i-1][1], tu[1]
        #print i, prev_rank
        if tu[1] != sorted_pro[i - 1][1]:
            rank_dict[tu[0]] = i
        else:
            rank_dict[tu[0]] = prev_rank
        prev_rank = rank_dict[tu[0]]

    return rank_dict

def convert_rank_to_ratio(ngram_rank):
    total_len = len(ngram_rank)
    ratio_dict = {}
    for key in ngram_rank:
        ratio_dict[key] = float(ngram_rank[key]) / total_len * 100.0
    return ratio_dict

def filter_ngram_dict(ngram_dict1, ngram_dict2):
    trg_dict = {}
    for key in ngram_dict1:
        if key not in ngram_dict2:
            continue
        trg_dict[key] = ngram_dict1[key]
    return trg_dict

def filter_rate(ngram_dict1, ngram_dict2, total=500):
    sorted_dict1 = sorted(ngram_dict1.items(), key=lambda x:x[1], reverse=True)
    sorted_dict2 = sorted(ngram_dict2.items(), key=lambda x:x[1], reverse=True)

    keys1 = set([a[0] for a in sorted_dict1[:total]])
    keys2 = set([a[0] for a in sorted_dict2[:total]])

    return float(len(keys1 & keys2)) / total

def ngram2pro_nosmooth(ngram_dict, multi=1.0, constant=0.0):
    pro_dict = {}
    total_fre = sum([a[1] for a in ngram_dict.items()])
    for key in ngram_dict:
        pro_dict[key] = float(ngram_dict[key]) / (total_fre + constant) * multi
    return pro_dict

def convert_ngram_to_pro(ngram_dict, current_fre, total_fre, line_num, multi=1.0):
    if line_num == len(ngram_dict):
        smooth_pro = 0.0
    else:
        smooth_pro = (float(total_fre) - current_fre) / ((line_num - len(ngram_dict)) * total_fre)

    fre_dict = {}
    for key in ngram_dict:
        fre_dict[key] = float(ngram_dict[key]) / total_fre * multi

    return fre_dict, smooth_pro * multi

def ngram_pro_smooth_func(ngram_dict, fre_threshold=2, multi=1.0):
    dict_meta = view_ngram_fre_ratio(ngram_dict, fre=fre_threshold)
    fre_sum = dict_meta[3]
    pro_dict = {}
    for key in ngram_dict:
        if ngram_dict[key] <= fre_threshold:
            continue
        pro_dict[key] = float(ngram_dict[key]) / fre_sum
    smooth_pro = (1 - dict_meta[0]) / ((1. - dict_meta[1]) * len(ngram_dict))

    def get_pro(key):
        return pro_dict.get(key, smooth_pro)
    return get_pro

def ngram_fre_smooth_func(ngram_dict, fre_threshold=2):
    dict_meta = view_ngram_fre_ratio(ngram_dict, fre=3)
    fre_sum = dict_meta[3]
    fre_dict = {}
    for key in ngram_dict:
        if ngram_dict[key] <= fre_threshold:
            continue
        fre_dict[key] = ngram_dict[key]
    smooth_fre = float(dict_meta[3] - dict_meta[2]) / (len(ngram_dict) - dict_meta[4])

    def get_fre(key):
        return fre_dict.get(key, smooth_fre)
    return get_fre

def load_ngram_files(ngram_file_path_list, order=False, threshold=0):
    ngram_dict = {}
    for ngram_file_path in ngram_file_path_list:
        with open(ngram_file_path) as ngram_file:
            for line in ngram_file:
                line = line.strip()
                ngram, gram_count = line.split('\t')
                if ngram in ngram_dict or int(gram_count) < threshold:
                    continue
                    #print ngram, 'in duplicated in %s' %ngram_file_path
                ngram_dict[ngram] = int(gram_count)
    if not order:
        return ngram_dict
    else:
        return sorted(ngram_dict.items(), key=operator.itemgetter(1), reverse=True)

def generate_all_ngram(input_file_path, output_file_path, gram_num, filter_num, sort=True, filter_function=punctuation_filter, merge=False, splitor=' ', min_gramn=2):
    file_list = []
    for i in range(min_gramn, gram_num + 1):
        generate_large_ngram_by_filtering(input_file_path, input_file_path + '_tmp%d' % i, gram_num=i, filter_num=filter_num, sort=True, filter_function=punctuation_filter, merge=False, splitor=splitor)
        file_list.append(input_file_path + '_tmp%d' % i)

    merge_ngram_file(file_list, output_file_path, sort=True, filter_function=filter_function, merge=merge)

    for file in file_list:
        os.system('rm %s' % file)

def merge_dict(gram_dict1, gram_dict2):
    total_dict = {}
    total_keys = set(gram_dict1.keys()) | set(gram_dict2.keys())
    for key in total_keys:
        total_dict[key] = gram_dict1.get(key,0) + gram_dict2.get(key, 0)
    return total_dict

def diff_dict(gram_dict1, gram_dict2, threshold_ratio):
    sorted_gram_dict1 = sorted(gram_dict1.items(), key=lambda x:x[1], reverse=True)
    for tu in sorted_gram_dict1:
        if tu[1] <= 0:
            break
        #print abs(tu[1] - gram_dict2.get(tu[0], 0.)), tu[1], abs(tu[1] - gram_dict2.get(tu[0], 0.)) / tu[1]
        #raw_input()
        if abs(tu[1] - gram_dict2.get(tu[0], 0.)) / tu[1] > threshold_ratio:
            print '%s\t%.6f\t%.6f' % (tu[0], tu[1], gram_dict2.get(tu[0], 0.))

def combine_ngram_dicts(dict_list, smooth_val, val_op):
    res_dict = {}

    key_list = set()
    for dic in dict_list:
        key_list |= set(dic.keys())

    for key in key_list:
        vals = [d.get(key, smooth_val[i]) for (i, d) in enumerate(dict_list)]
        res_dict[key] = val_op(vals)

    return res_dict

def view_ngram_ratio_fre(ngram_dict, ratio=0.8):
    fre_sum = sum(ngram_dict.values())
    sorted_list = sorted(ngram_dict.items(), key=lambda x:x[1], reverse=True)

    threshold_sum = ratio * fre_sum
    cur_fre = -1
    cur_sum = 0
    enough = False
    for i, tu in enumerate(sorted_list):
        cur_sum += tu[1]
        if cur_sum >= threshold_sum and enough == False:
            print '%.4f in line %d [%d, %.6f]' % (ratio, i, len(sorted_list), float(i)/len(sorted_list))
            enough = True
        if enough and cur_fre != tu[1]:
            return cur_fre, float(cur_sum) / fre_sum, float(i) / len(sorted_list), fre_sum
        cur_fre = tu[1]
    return cur_fre, float(cur_sum) / fre_sum, float(i) / len(sorted_list), fre_sum

def view_ngram_fre_ratio(ngram_dict, fre=3):
    fre_sum = sum(ngram_dict.values())
    sorted_list = sorted(ngram_dict.items(), key=lambda x:x[1], reverse=True)

    cur_sum = 0.
    for i, tu in enumerate(sorted_list):
        cur_sum += tu[1]
        if tu[1] <= fre:
            print fre_sum, cur_sum, len(sorted_list), i
            return cur_sum / fre_sum, float(i) / len(sorted_list), cur_sum, fre_sum, i
    return cur_sum / fre_sum, float(i) / len(sorted_list), cur_sum, fre_sum, i

if __name__ == '__main__':
    func = sys.argv[1]

    if func == 'ngram_count':
        input_file_path, output_file_path, gram_num, filter_num = sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
        generate_large_ngram_by_filtering(input_file_path, output_file_path, gram_num=gram_num, filter_num=filter_num, sort=True, filter_function=punctuation_filter, merge=False)
    elif func == 'segment':
        input_file_path, output_file_path = sys.argv[2], sys.argv[3]
        seg_file(input_file_path, output_file_path)
    elif func == 'all_ngram':
        input_file_path, output_file_path, gram_num, gram_start_num, filter_num = sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
        generate_all_ngram(input_file_path, output_file_path, gram_num, filter_num, sort=True, filter_function=punctuation_filter, merge=False, min_gramn=gram_start_num)
    elif func == 'all_cngram':
        input_file_path, output_file_path, gram_num, filter_num = sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
        generate_all_ngram(input_file_path, output_file_path, gram_num, filter_num, sort=True, filter_function=punctuation_filter, merge=False, splitor='')
