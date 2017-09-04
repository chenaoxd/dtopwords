# coding=utf-8
import json
import multiprocessing
import math

from ngram import *

fre_score_json = './corpus/score_dict_fre.json'
rf_score_json = './corpus/score_dict_rf2.json'
#wscore_json = './topwords_tmp/pro_dict/score_dict_wscore.json'
#emi_json = './topwords_tmp/pro_dict/score_dict_emi.json'
#af_json = './topwords_tmp/pro_dict/score_dict_af.json'
#rf_json = './topwords_tmp/pro_dict/score_dict_rf.json'
#fre2_json = './topwords_tmp/pro_dict/score_dict_fre2.json'

len_c = 50
varphi = 0.9

def w2cs(word):
    word = word.replace(' ', '')
    word = ' '.join([a.encode('utf-8') for a in list(word.decode('utf-8')) if a.strip()])
    return word

def fre_score(fre_path = './topwords_tmp/pro_dict/score_dict_fre.json'):
    import math
    src_score_dict = load_ngram('./corpus/cngram_yuwei.txt')
    score_dict = {}
    for key in src_score_dict:
        score_dict[key] = math.sqrt(900.0 / src_score_dict[key]) ** 1.2

    json.dump(score_dict, open(fre_path, 'w'), encoding='utf-8', ensure_ascii=False)
    return fre_path

def af_score():
    af_path = './topwords_tmp/pro_dict/score_dict_fre.json'
    src_emi = json.load(open('./topwords_tmp/pro_dict/score_dict_emi.json'))
    fre_dict = load_ngram('./corpus/cngram_yuwei.txt')
    emi = {}
    for skey in src_emi:
        emi[skey.encode('utf-8')] = src_emi[skey]

    af = {}
    for key in emi:
        cs = key.split(' ')
        af[key] = sum([fre_dict.get(c,1.0) for c in cs]) / float(len(cs))
        af[key] = math.sqrt(900.0 / af[key])

    json.dump(af, open(af_path, 'w'), encoding='utf-8', ensure_ascii=False)
    return af_path

def EMI_score(corpus_path):
    min_n = 2
    max_n = 7
    fd = {}
    cd = {}
    emi = {}
    emi_path = './topwords_tmp/pro_dict/score_dict_emi.json'
    with open(corpus_path) as corpus_file:
        file_lines = corpus_file.readlines()
        N = len(file_lines)
        for line in file_lines:
            line = line.strip()
            segs = [a.encode('utf-8') for a in list(line.decode('utf-8')) if a.strip()]
            lt = {}
            for gramn in range(1, max_n + 1):
                for i in range(0, len(segs) - gramn + 1):
                    word = ' '.join(segs[i:i + gramn])
                    if word not in lt:
                        lt[word] = 1
            for word in lt:
                if word.count(' ') == 0:
                    if word not in cd:
                        cd[word] = 0.
                    cd[word] += 1.
                else:
                    if word not in fd:
                        fd[word] = 0.
                    fd[word] += 1.
        for word in fd:
            tn = 1.
            for c in word.split(' '):
                tn *= (cd[c] - fd[word] + 1) / N
            emi[word] = (math.log(fd[word] /(N * tn)) + 8) / (1.7 ** (word.count(' ')+ 1) / 4)
    json.dump(emi, open(emi_path, 'w'), encoding='utf-8', ensure_ascii=False)
    return emi_path

def initialize_static_files(src_files):
    cn_dir = './inter_results'
    init_dir = './inter_results'
    pro_dir = './inter_results'

    for tfp in src_files:
        cnp = os.path.join(cn_dir, tfp.split('/')[-1] + '.cngram')
        inp = os.path.join(init_dir, tfp.split('/')[-1] + '.init')
        prp = os.path.join(pro_dir, tfp.split('/')[-1] + '.pro')
        init_dict(tfp, cnp, inp)
        count_dict = load_ngram(inp)
        pro_dict = ngram2pro_nosmooth(count_dict)
        json.dump(pro_dict, open(prp, 'w'), encoding='utf-8', ensure_ascii=False)

def init_dict(src_path, cn_path, trg_path, len_threshold=7, fre_threshold=2, splitor=''):
    # Add unigram to initial_dict
    generate_all_ngram(src_path, cn_path, len_threshold, fre_threshold, splitor=splitor)
    ngram_dict = load_ngram(cn_path)
    with open(src_path) as src_file:
        for line in src_file:
            line = line.strip()
            if splitor == '':
                segs = [a.encode('utf-8') for a in list(line.decode('utf-8')) if a.strip()]
            else:
                segs = [a for a in line.split(splitor) if a.strip()]
            for seg in segs:
                if seg not in ngram_dict:
                    ngram_dict[seg] = 0             # old: = 1
                ngram_dict[seg] += 1

    with open(trg_path, 'w') as trg_file:
        for key, value in ngram_dict.items():
            trg_file.write('%s\t%d\n' %(key.replace(' ',' '), value))

def iter_segs(segs, start, prev_words, theta_dict, iota_dict, score_dicts):
    #print ','.join(segs), start, '-'.join(prev_words)
    for end in range(start + 1, len(segs) + 1):
        cur_word = ' '.join(segs[start:end])
        if cur_word in theta_dict or cur_word in iota_dict:
            nl_prev_words = prev_words + [cur_word]
            if end < len(segs):
                for a in iter_segs(segs, end, nl_prev_words, theta_dict, iota_dict, score_dicts):
                    yield a
            else:
                yield nl_prev_words

def get_all_possible_segments(line, theta_dict, iota_dict, phi_dict, score_dicts, splitor='', score_default=6):
    #print 'aa'
    if splitor == '':
        segs = [a.encode('utf-8') for a in list(line.decode('utf-8'))]
    else:
        segs = line.split(splitor)

    sps_list = []
    #print ' '.join(segs)
    for s in iter_segs(segs, 0, [], theta_dict, iota_dict, score_dicts):
        ps_s = 1.0
        for w in s:
            ps_s *= (theta_dict.get(w, 0.) * phi_dict[w] * len_c + iota_dict.get(w, 0.) * (1 - phi_dict[w]) * get_word_score(w, score_dicts) * len_c)
        sps_list.append([s, ps_s])
        #print ','.join(s)

    total_pro = sum([a[1] for a in sps_list])
    sp_list = [[a[0], a[1]/total_pro] for a in sps_list]

    return sp_list

def average_func(scores):
    return sum(scores) / len(scores)

def times_func(scores):
    res = 1.
    for s in scores:
        res *= s
    return res

def get_word_score(word, score_dicts, score_defaults=[6,1], compute_func=times_func):# 2 rf best choice
    return compute_func([d.get(word, score_defaults[i]) for i,d in enumerate(score_dicts)])

def compute_wn(lines, nt_dict, ni_dict, theta_dict, iota_dict, phi_dict, score_dicts, splitor, line_len_threshold, score_default=1):
    # historical problems
    nt_queue = nt_dict
    ni_queue = ni_dict
    nt_dict = {}
    ni_dict = {}

    count = 0
    for line in lines:
        if count % 100 == 0:
            print count
        count += 1
        line = line.strip()
        if len(line.decode('utf-8')) > line_len_threshold:
            continue

        sp_list = get_all_possible_segments(line, theta_dict, iota_dict, phi_dict, score_dicts, splitor, score_default)
        for spt in sp_list:
            for w in spt[0]:
                if w not in nt_dict:
                    nt_dict[w] = 0
                if w not in ni_dict:
                    ni_dict[w] = 0
                nt_dict[w] += spt[1] / (theta_dict.get(w, 0) * phi_dict[w] + iota_dict.get(w, 0) * (1 - phi_dict[w]) * get_word_score(w, score_dicts)) * theta_dict.get(w, 0) * phi_dict[w]
                ni_dict[w] += spt[1] / (theta_dict.get(w, 0) * phi_dict[w] + iota_dict.get(w, 0) * (1 - phi_dict[w]) * get_word_score(w, score_dicts)) * iota_dict.get(w, 0) * get_word_score(w, score_dicts) * (1 - phi_dict[w])
    nt_queue.put(nt_dict)
    ni_queue.put(ni_dict)

def compute_theta(src_corpus_path, line_len_threshold=15, splitor='',  inter_dir='./inter_results/iterations', iter_num=100, pro_threshold=10e-8, src_name='c4x@TsinghuaX@30240184X.txt'):
    def split_list(src_list, n):
        for i in range(0, len(src_list), n):
            yield src_list[i: i+n]

    theta_dict_tmp = json.load(open('./inter_results/%s.pun_filtered.pro' % src_name))
    theta_dict = {}
    for key in theta_dict_tmp:
        theta_dict[key.encode('utf-8')] = theta_dict_tmp[key]
    print '--'

    iota_dict_tmp = json.load(open('./inter_results/%s.pun_filtered.pro' % src_name))
    iota_dict = {}
    for key in iota_dict_tmp:
        iota_dict[key.encode('utf-8')] = iota_dict_tmp[key]
    print '--'

    # init phi dict
    phi_dict = {}
    total_keys = set(theta_dict.keys()) | set(iota_dict.keys())
    for key in total_keys:
        phi_dict[key] = varphi
    print '--'

    # init score dict
    #score_paths = [fre_json, emi_json]
    #score_paths = [emi_json]
    #score_paths = [fre_json]
    #score_paths = [wscore_json]
    #score_paths = [af_json]
    #score_paths = [rf2_json]
    score_paths = [fre_score_json]
    #score_paths = []
    score_dicts = []
    for path in score_paths:
        score_dict_tmp = json.load(open(path))
        score_dict = {}
        for key in score_dict_tmp:
            score_dict[key.encode('utf-8')] = score_dict_tmp[key]
        score_dicts.append(score_dict)
    print '--'

    for ite in range(0, iter_num):
        nt_dict = {}
        ni_dict = {}
        count = 0
        src_file = open(src_corpus_path)

        lines_list = [a for a in split_list(src_file.readlines(), 4000)]
        thread_num = len(lines_list)
        nt_list = []
        ni_list = []
        thread_list = []
        for i in range(0, thread_num):
            nt_list.append(multiprocessing.Queue())
            ni_list.append(multiprocessing.Queue())
            thread_list.append(multiprocessing.Process(target=compute_wn, args=(lines_list[i], nt_list[i], ni_list[i], theta_dict, iota_dict, phi_dict, score_dicts, splitor, line_len_threshold)))

        for i in range(0, thread_num):
            thread_list[i].start()

        #for i in range(0, thread_num):
        #    thread_list[i].join()

        for i in range(0, thread_num):
            cur_nt = nt_list[i].get()
            for key in cur_nt:
                if key not in nt_dict:
                    nt_dict[key] = 0.
                nt_dict[key] += cur_nt[key]

            cur_ni = ni_list[i].get()
            for key in cur_ni:
                if key not in ni_dict:
                    ni_dict[key] = 0.
                ni_dict[key] += cur_ni[key]

        theta_dict_whole = ngram2pro_nosmooth(nt_dict, constant = len(theta_dict)) # TBD: use count
        iota_dict_whole = ngram2pro_nosmooth(ni_dict, constant = len(iota_dict)) # TBD: use count
        #for w in nt_dict:
        #    phi_dict[w] = nt_dict[w] / (nt_dict[w] + ni_dict[w])
        theta_dict = {}
        for tu in theta_dict_whole.items():
            if tu[1] < pro_threshold:
                continue
            theta_dict[tu[0]] = tu[1]

        iota_dict = {}
        for tu in iota_dict_whole.items():
            if tu[1] < pro_threshold or ' ' not in tu[0]:
                continue
            iota_dict[tu[0]] = tu[1]

        #sorted_theta = sorted(theta_dict.items(), key=lambda x:x[1], reverse=True)
        #for tu in sorted_theta[:20]:
        #    print tu[0],tu[1]
        #sorted_iota = sorted(iota_dict.items(), key=lambda x:x[1], reverse=True)
        #for tu in sorted_iota[:20]:
        #    print tu[0],tu[1]

        theta_result_file = open('%s/theta_iter%d_result.txt' % (inter_dir, ite), 'w')
        for tu in sorted(theta_dict.items(), key=lambda x:x[1], reverse=True):
            theta_result_file.write('%s\t%.8f\n' % (tu[0], tu[1]))

        iota_result_file = open('%s/iota_iter%d_result.txt' % (inter_dir, ite), 'w')
        for tu in sorted(iota_dict.items(), key=lambda x:x[1], reverse=True):
            iota_result_file.write('%s\t%.8f\n' % (tu[0], tu[1]))

        #phi_result_file = open('%s/phi_iter%d_result.txt' % (output_dir, ite), 'w')
        #for tu in sorted(phi_dict.items(), key=lambda x:x[1], reverse=True):
        #    phi_result_file.write('%s\t%.8f\n' % (tu[0], tu[1]))
        print '[ Iteration %d finished ... ]' % ite

def segment_sentence(sentence, theta_dict, seg_pro_threshold=0.3):
    sp_list = get_all_possible_segments(sentence, theta_dict)
    csegs = [a.encode('utf-8') for a in list(sentence.decode('utf-8'))]
    seg_dict = [0.0] * len(csegs)
    for tu in sp_list:
        pos = 0
        for seg in tu[0][:-1]:
            pos += seg.count(' ')
            seg_dict[pos] += tu[1]
            pos += 1

    result_sentence = ''
    for i, c in enumerate(csegs):
        result_sentence += c
        if seg_dict[i] > seg_pro_threshold:
            result_sentence += ' '
    return result_sentence

def generate_domain_words(src_path, trg_path):
    #src_dir = '/home/dreamszl/code/xuetangx_caption/captions_by_course/selected_subtitles'
    #src_files = [os.path.join(src_dir,a) for a in os.listdir(src_dir)]
    #trg_files = [os.path.join(trg_dir,a.split('/')[-1]) for a in src_files]
    src_name = src_path.split('/')[-1]
    punc_filtered_path = './inter_results/%s.pun_filtered' % src_name
    generate_punc_filtered_corpus(src_path, punc_filtered_path, splitor='')
    trg_files = [punc_filtered_path]
    initialize_static_files(trg_files)
    compute_theta(src_corpus_path=punc_filtered_path, iter_num=5, src_name=src_name)
    os.system('cp inter_results/iterations/iota_iter4_result.txt %s' % trg_path)

if __name__ == '__main__2':
    generate_domain_words('./corpus/c4x@TsinghuaX@30240184X.txt', './results/3024.txt')

if __name__ == '__main__':
    generate_domain_words('./corpus/all_scripts.txt', './results/test.txt')
