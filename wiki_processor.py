#coding=utf-8
import re
import json
import codecs

SRC_WIKI_DIR = '/home/dreamszl/corpus/wiki_sc_seg/'
SRC_WIKI_FILES = [SRC_WIKI_DIR + 'wiki_00_seg', SRC_WIKI_DIR + 'wiki_01_seg']

CONVERTED_WIKI = '/home/dreamszl/corpus/wiki_conv/'
CONVS = [CONVERTED_WIKI + 'wiki_00', CONVERTED_WIKI + 'wiki_01']

MARKMODE_WIKI = '/home/dreamszl/corpus/wiki_mm/'
MM_FILES = [MARKMODE_WIKI + 'wiki_00', MARKMODE_WIKI + 'wiki_01']

debug_flag = False

def convert_wiki(file_num = 0):
    a_tags = ['<a .*?>', '<a .*?>', '< a .*?>']
    ea_tags = ['< / a >', '< /a >', '</ a >', '</ a>', '</a >', '< / a>', '</a>', '< /a>']
    wiki_file = SRC_WIKI_FILES[file_num]
    conv0 = open(CONVS[file_num], 'w')
    for i, line in enumerate(open(wiki_file)):
        if i % 1000 == 0:
            print i
        line = line.strip()
        if line.startswith('<doc') or line.startswith('</doc'):
            continue
        m = re.search('<a .*?>', line)
        for at in a_tags:
            line = re.sub(at, ' ““ ', line)
        for eat in ea_tags:
            line = re.sub(eat, ' ”” ', line)
        line = re.sub(' +', ' ', line)
        if m:
            #print m.group(0)
            conv0.write(line + '\n')
        #print line

def convert_wiki_mark_mode(file_num = 0):
    a_tags = ['<a .*?>', '<a .*?>', '< a .*?>']
    ea_tags = ['< / a >', '< /a >', '</ a >', '</ a>', '</a >', '< / a>', '</a>', '< /a>']
    wiki_file = SRC_WIKI_FILES[file_num]
    conv0 = open(MM_FILES[file_num], 'w')
    for i, line in enumerate(open(wiki_file)):
        if i % 1000 == 0:
            print i
        line = line.strip()
        if line.startswith('<doc') or line.startswith('</doc'):
            continue
        m = re.search('<a .*?>', line)
        for at in a_tags:
            line = re.sub(at, ' ““ ', line)
        for eat in ea_tags:
            line = re.sub(eat, ' ”” ', line)
        line = re.sub(' +', ' ', line)

        if not m:
            continue
        segs = line.split(' ')
        conv0.write('[LINE_START] ')
        for seg in segs:
            if seg not in ['““', '””']:
                conv0.write(seg + ' ')
        conv0.write('[LINE_END]\n')
        conv0.write('0 ')
        word_type = '0'
        for seg in segs:
            if seg == '““':
                word_type = '1'
            elif seg == '””':
                word_type = '0'
            elif seg not in ['““', '””']:
                conv0.write(word_type + ' ')
        conv0.write('0\n')

def generate_contexts():
    context_dict = {}
    for wiki_path in CONVS:
        for i, line in enumerate(open(wiki_path)):
            if i % 10000 == 0:
                print i

            #if i > 10000:
            #    break
            line = line.strip()
            #print type(line)
            #exit()
            m = re.finditer('““.*?””', line)
            #print line
            for a in m:
                #print a.group(0), a.start(0), a.end(0)
                word = ''.join(a.group(0).split(' ')[1:-1])
                #if word == '':
                #    word = a.group(0)[7:-6]
                if not word.strip():
                    continue
                prev_con = line[:a.start(0) - 1].strip().split(' ')[-1]
                next_con = line[a.end(0) + 1:].strip().split(' ')[0]
                try:
                    prev_con.decode('utf-8')
                    next_con.decode('utf-8')
                except:
                    continue
                if word == '富春' and False:
                    debug_flag = True

                if debug_flag:
                    print line
                    print '------------------'
                    print prev_con
                    print next_con

                if prev_con == '””':
                    #print word, ' < in >', line
                    #prev_con = line[:a.start(0) - 1].split(' ')[-2]
                    i = -2
                    try:
                        if debug_flag:
                            print line[:a.start(0) - 1].strip().split(' ')[i]
                        while line[:a.start(0) - 1].strip().split(' ')[i] != '““':
                            i -= 1
                    except:
                        print '>> error in .. ', word, ' < in >', line
                        continue
                    prev_con = ''.join(line[:a.start(0) - 1].strip().split(' ')[i + 1:-1])
                    if debug_flag:
                        print prev_con
                    #print ' '.join(line[:a.start(0) - 1].strip().split(' ')[i + 1:-2])

                if next_con == '““':
                    #print word, ' < in >', line
                    i = 1
                    try:
                        while line[a.end(0) + 1:].strip().split(' ')[i] != '””':
                            i += 1
                    except:
                        print '>> error in .. ', word, ' < in >', line
                        continue
                    next_con = ''.join(line[a.end(0) + 1:].strip().split(' ')[1:i])
                    #print ' '.join(line[a.end(0) + 1:].strip().split(' ')[1:i])
                #print '%s [[ %s ]] %s' % (prev_con, word, next_con)
                if word not in context_dict:
                    context_dict[word] = {}

                if (prev_con, next_con) not in context_dict[word]:
                    context_dict[word][(prev_con, next_con)] = 0
                context_dict[word][(prev_con, next_con)] += 1
                if debug_flag:
                    exit()

    output_file = open('./context_dict_sorted.txt', 'w')
    for word_tu in sorted(context_dict.items(), key=lambda x:x[1], reverse=True):
        try:
            ('================== %s ==================\n' % word_tu[0]).decode('utf-8')
        except:
            continue
        output_file.write(('================== %s ==================\n' % word_tu[0]))
        for tu in sorted(word_tu[1].items(), key=lambda x:x[1], reverse=True):
            try:
                ('%s\t%d\n' % ('__'.join(tu[0]), tu[1])).decode('utf-8')
            except:
                continue
            output_file.write(('%s\t%d\n' % ('__'.join(tu[0]), tu[1])))
        #print '================== %s ==================' % word
        #for context in context_dict[word]:
        #    print '%s\t%d' % ('__'.join(context), context_dict[word][context])

    #json.dump(context_dict, open('context_dict.json', 'w'))

def generate_negative_contexts():
    debug_flag = True
    negative_context_dict = {}
    for wiki_path in MM_FILES:
        cur_line = ''
        cur_m = ''
        for i, line in enumerate(open(wiki_path)):
            if i % 10000 == 0:
                print i
            if i % 2 == 0:
                cur_line = line.strip()
                continue
            else:
                cur_m = line.strip()

            w_segs = cur_line.split(' ')
            m_segs = cur_m.split(' ')
            link_indexes = [i for i,j in enumerate(m_segs) if j == '1']
            prev_i = 0
            next_i = 0
            for index in link_indexes:
                prev_i = index
                next_i = index
                while m_segs[prev_i] == '1':
                    prev_i -= 1
                while m_segs[next_i] == '1':
                    next_i += 1
                try:
                    template_tu = (w_segs[prev_i - 1], w_segs[next_i + 1])
                except:
                    print 'index out of range'
                    continue
                cur_word = w_segs[index]
                if debug_flag:
                    print '-----------------------------------'
                    print cur_line
                    #print cur_word
                    print ' '.join(w_segs[prev_i:next_i + 1])
                    print '__'.join(template_tu)
                    #exit()

                if cur_word not in negative_context_dict:
                    negative_context_dict[cur_word] = {}

                if template_tu not in negative_context_dict[cur_word]:
                    negative_context_dict[cur_word][template_tu] = 0
                negative_context_dict[cur_word][template_tu] += 1

    output_file = open('./negative_context_dict_sorted.txt', 'w')
    for word_tu in sorted(negative_context_dict.items(), key=lambda x:x[1], reverse=True):
        try:
            ('================== %s ==================\n' % word_tu[0]).decode('utf-8')
        except:
            continue
        output_file.write(('================== %s ==================\n' % word_tu[0]))
        for tu in sorted(word_tu[1].items(), key=lambda x:x[1], reverse=True):
            try:
                ('%s\t%d\n' % ('__'.join(tu[0]), tu[1])).decode('utf-8')
            except:
                continue
            output_file.write(('%s\t%d\n' % ('__'.join(tu[0]), tu[1])))

def read_contexts(context_path = './context_dict_sorted.txt'):
    current_word = ''
    context_dict = {}
    with open(context_path) as context_file:
        for line in context_file:
            line = line.strip()
            if line.startswith('===='):
                current_word = line.split(' ')[1]
                context_dict[current_word] = {}
            else:
                segs = line.split('\t')
                context_dict[current_word][segs[0]] = int(segs[1])
    return context_dict

def load_contexts(context_path = './context_dict.json'):
    return json.load(open(context_path))

def random_select(context_dict):
    #word_list = [word for word in context_dict]
    whole_contexts = []
    current_temp_set = {}
    count = 0
    for word in context_dict:
        for con in context_dict[word]:
            if con not in current_temp_set:
                current_temp_set[con] = 0
            current_temp_set[con] += context_dict[word][con]

        count += 1
        if count % 50 == 0:
            whole_contexts.append(current_temp_set)
            current_temp_set = {}

    return whole_contexts

if __name__ == '__main__2':
    for i in [0, 1]:
        #convert_wiki(i)
        convert_wiki_mark_mode(i)

if __name__ == '__main__':
    generate_negative_contexts()

if __name__ == "__main__2":
    context_dict = read_contexts()
    whole_contexts = {}
    for word in context_dict:
        for con in context_dict[word]:
            if con not in whole_contexts:
                whole_contexts[con] = 0
            whole_contexts[con] += context_dict[word][con]

    whole_contexts_file = open('./whole_contexts.txt', 'w')
    for tu in sorted(whole_contexts.items(), key=lambda x:x[1], reverse=True):
        whole_contexts_file.write('%s\t%d\n' % (tu[0], tu[1]))

if __name__ == '__main__2':
    context_dict = load_contexts()
    #json.dump(context_dict, open('./context_dict.json', 'w'))
    output_file = open('random_select_aver.txt', 'w')
    whole_contexts = random_select(context_dict)
    aver_contexts = {}
    count = {}
    TOTAL = 28964
    for contexts in whole_contexts:
        #output_file.write('==================================\n')
        for tu in sorted(contexts.items(),key=lambda x:x[1], reverse=True):
            #output_file.write("%s\t%d\n" %(tu[0].encode('utf-8'), tu[1]))
            #if tu[1] < 5:
            #    continue
            if tu[0] not in aver_contexts:
                aver_contexts[tu[0]] = 0.
                count[tu[0]] = 0
            aver_contexts[tu[0]] += 1./tu[1]
            count[tu[0]] += 1

    real_aver_contexts = {}
    for con in aver_contexts:
        real_aver_contexts[con] = TOTAL / (aver_contexts[con] + (TOTAL - count[con]) * 2.)

    for tu in sorted(real_aver_contexts.items(),key=lambda x:x[1],reverse=True):
        output_file.write('%s\t%.4f\n' % (tu[0].encode('utf-8'), tu[1]))

if __name__ == '__main__2':
    context_dict = read_contexts('./negative_context_dict_sorted.txt')
    #json.dump(context_dict, open('./context_dict.json', 'w'))
    output_file = open('negative_random_select_aver.txt', 'w')
    whole_contexts = random_select(context_dict)
    aver_contexts = {}
    count = {}
    TOTAL = 28964
    for contexts in whole_contexts:
        #output_file.write('==================================\n')
        for tu in sorted(contexts.items(),key=lambda x:x[1], reverse=True):
            #output_file.write("%s\t%d\n" %(tu[0].encode('utf-8'), tu[1]))
            #if tu[1] < 5:
            #    continue
            if tu[0] not in aver_contexts:
                aver_contexts[tu[0]] = 0.
                count[tu[0]] = 0
            aver_contexts[tu[0]] += 1./tu[1]
            count[tu[0]] += 1

    real_aver_contexts = {}
    for con in aver_contexts:
        real_aver_contexts[con] = TOTAL / (aver_contexts[con] + (TOTAL - count[con]) * 2.)

    for tu in sorted(real_aver_contexts.items(),key=lambda x:x[1],reverse=True):
        try:
            output_file.write('%s\t%.4f\n' % (tu[0].encode('utf-8'), tu[1]))
        except:
            output_file.write('%s\t%.4f\n' % (tu[0], tu[1]))
