import argparse
import re
import math

parser = argparse.ArgumentParser()
parser.add_argument('--apply_bpe', dest='apply_bpe', nargs='?', help='apply_bpe', default=0, const=1)
parser.add_argument('--learn_bpe', dest='learn_bpe', nargs='?', help='learn_bpe', default=0, const=1)
parser.add_argument('--inpath', dest='inpath', type=str, help='Add inpath')
parser.add_argument('--outpath', dest='outpath', type=str, help='Add outpath')
parser.add_argument('--vocab', dest='vocab', type=str, help='Add vocab')
parser.add_argument('--vocab_size', dest='vocab_size', type=int, help='Add vocab_size', default=10000)
args = parser.parse_args()

data = "" # input file
words = {} 
tokens = {} # includes individual char
vocabs = [] # tokens learnt
word_maps = {}  # contains both input word to output word and output word to input word;
                # e.g. "hi" : "h_i_", "h_i_" : "hi"
changeWords = []

def init():
    global data
    global words
    global word_maps
    with open(args.inpath, encoding='utf-8') as f:
        data = f.read()
        data = [line.split() for line in data.split("\n")]
        f.seek(0)
        for line in f:
            for word in line.split():
                new_word = " ".join(word) + " _"
                if (new_word in words):
                    words[new_word] += 1
                else:
                    word_maps[word] = new_word
                    word_maps[new_word] = word
                    words[new_word] = 1

def findMax(tokens):
    max_value = 0
    max_tokens = []
    rt = []
    lt = []
    for key, value in tokens.items():
        if (value[0] > max_value):
            max_value = value[0]
    max_tokens = [key for key, value in tokens.items() if value[0] == max_value]
    rt = [[token.split(" ")[1], i] for i, token in enumerate(max_tokens)]
    min_rt = min(rt, key = lambda x: x[0])[0]
    min_rt_indices = [i for r, i in rt if r == min_rt]
    if (len(min_rt_indices) == 1):
        return max_tokens[min_rt_indices[-1]]
    min_lt = min(max_tokens[ind].split(" ")[0] for ind in min_rt_indices)
    for ind in min_rt_indices:
        if (max_tokens[ind].split()[0] < min_lt):
            min_lt = max_tokens[ind].split()[0]
    for ind in min_rt_indices:
        if (max_tokens[ind].split()[0] == min_lt):
            return max_tokens[ind]

def BPEmerge():
    global vocabs
    global changeWords
    for word in changeWords:
        word_count = words[word]
        tok_list = word.split(" ")
        for i in range(len(tok_list) - 1):
            if (tok_list[i] + " " +  tok_list[i + 1] in tokens):
                tokens[tok_list[i] + " " + tok_list[i + 1]][0] += word_count
                if (word not in tokens[tok_list[i] + " " +  tok_list[i + 1]][1]):
                    tokens[tok_list[i] + " " +  tok_list[i + 1]][1].append(word)
            else:
                tokens[tok_list[i] + " " +  tok_list[i + 1]] = [word_count, [word]]
            # print(tok_list[i] + " " +  tok_list[i + 1], " : ", tokens[tok_list[i] + " " +  tok_list[i + 1]][0])
    max_token = findMax(tokens)
    # print("max token: ", max_token)
    # print("tokens: ", tokens, "\n")
    left_token = max_token.split(" ")[0]
    right_token = max_token.split(" ")[1]
    # vocabs.append([max_token, tokens[max_token][0]])
    vocabs.append(max_token)
    changeWords = tokens[max_token][1]
    # print("change words : ", changeWords, "\n")

    for i in range(len(changeWords)):
        # print("change words : ", changeWords, "\n")
        # print(i, changeWords[i])
        w = changeWords[i]
        bpe_word = w
        word = word_maps[bpe_word]
        vocab = max_token
        vocab_list = vocab.split(" ")
        l = len(vocab_list[0])
        r = len(vocab_list[1])
        indices = [match.start() for match in re.finditer(re.escape(vocab), bpe_word)]
        not_indices = []
        for index in indices:
            if (index != 0 and bpe_word[index - 1] != " "):
                not_indices.append(index)
            elif (index + l + r + 1 < len(bpe_word) and bpe_word[index + l + r + 1] != " "):
                not_indices.append(index)
        real_indices = [x for x in indices if x not in not_indices]
        for ind in reversed(real_indices):
            bpe_word = bpe_word[:ind + l] + bpe_word[ind + l + 1:]
        tok_list = w.split(" ")
        del_tok_indices = []
        for j in range(len(tok_list) - 1):
            if (tok_list[j] + " " +  tok_list[j + 1] != max_token):
                # print("remove : ", w, " from ", tok_list[j] + " " +  tok_list[j + 1], "'s words :", tokens[tok_list[j] + " " +  tok_list[j + 1]][1])
                tokens[tok_list[j] + " " +  tok_list[j + 1]][0] -= words[w]
                del_tok_indices.append(j)
        for k in del_tok_indices:
            if (w in tokens[tok_list[k] + " " +  tok_list[k + 1]][1]):
                tokens[tok_list[k] + " " +  tok_list[k + 1]][1].remove(w)
        word_maps[word] = bpe_word
        del word_maps[w]
        word_maps[bpe_word] = word
        words[bpe_word] = words[w]
        del words[w]
        tokens[max_token][1][i] = bpe_word
    changeWords = tokens[max_token][1]
    # print("change words after: ", changeWords, "\n")
    del tokens[max_token]


def writeOutputfile():
    with open(args.outpath, 'w+', encoding='utf-8') as f:
        for j in range(len(data)):
            line = data[j]
            for i in range(len(line)):
                print(word_maps[line[i]].replace("_",""), end="", file=f)
                if (word_maps[line[i]].replace("_","")[-1] != " "):
                    # print(line[i])
                    print(" ", end="", file=f)
            if (j != len(data) - 1): print("\n", end="", file=f)
    with open(args.vocab, 'w+', encoding='utf-8') as f:
        for v in vocabs:
            print(v, file = f)

def readvocab():
    global vocabs
    with open(args.vocab, 'r', encoding='utf-8') as f:
        vocabs = f.read()

def applyinit():
    with open(args.inpath, encoding='utf-8') as f:
        global data
        global word_maps
        data = f.read()
        data = [line.split() for line in data.split("\n")]
        f.seek(0)
        for line in f:
            for word in line.split():
                new_word = " ".join(word) + " _"
                word_maps[word] = new_word
                word_maps[new_word] = word

def changeWords(word_maps):
    for line in data:
        for word in line:
            bpe_word = word_maps[word]
            for vocab in vocabs:
                if vocab not in bpe_word:
                    continue
                vocab_list = vocab.split(" ")
                l = len(vocab_list[0])
                r = len(vocab_list[1])
                indices = [match.start() for match in re.finditer(re.escape(vocab), bpe_word)]
                not_indices = []
                for index in indices:
                    if (index != 0 and bpe_word[index - 1] != " "):
                        not_indices.append(index)
                    elif (index + l + r + 1 < len(bpe_word) and bpe_word[index + l + r + 1] != " "):
                        not_indices.append(index)
                real_indices = [x for x in indices if x not in not_indices]
                for ind in reversed(real_indices):
                    bpe_word = bpe_word[:ind + l] + bpe_word[ind + l + 1:]
                word_maps[word] = bpe_word

def writeApplyOutputfile():
    with open(args.outpath, 'w+', encoding='utf-8') as f:
        # print(vocabs,file=f)
        for j in range(len(data)):
            line = data[j]
            if (line == ""):
                print("\n", file=f)
            for i in range(len(line)):
                # print("maps ", line[i], " to ", word_maps[line[i]])
                print(word_maps[line[i]].replace("_",""), end="", file=f)
                if (word_maps[line[i]].replace("_","")[-1] != " "):
                    # print(line[i])
                    print(" ", end="", file=f)
            if (j != len(data) - 1): print("\n", end="", file=f)
        # print(data)

if (args.learn_bpe):
    init()
    changeWords = list(words.keys())
    for i in range(args.vocab_size):
        BPEmerge()
    writeOutputfile()
if (args.apply_bpe):
    readvocab()
    vocabs = vocabs.split("\n")
    if "" in vocabs:
        vocabs.remove("") 
    applyinit()
    changeWords(word_maps)
    writeApplyOutputfile()


