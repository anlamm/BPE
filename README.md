# BPE algorithm
BPE (byte-pair encoding) tokenizer algorithm used for text preprocessing for NLP<br />
When two or more merge operations<br />
lt + rt → ltrt<br />
in BPE have the same occurrence count, tie-breaking should proceed as follows: the<br />
merge operation where rt comes first in alphabetical order should be chosen; if there is still a tie, then the merge operation where lt comes first in alphabetical order should be chosen.<br />
The list of merge operations learned by BPE follows the following format (which will be written in voc file):<br />
lt1 rt1<br />
lt2 rt2<br />
...<br />
The default size of the vocabulary is 10,000<br />
## Commands
python3 a1.py ––learn_bpe ––inpath {path to input text} ––
outpath {path to output text} ––vocab {path to vocab file}
––vocab_size {size}<br /><br />
The above command will learn the BPE merge operations. Given a training text specified by the ––inpath argument (e.g., trn), it generates the BPE-tokenized text in the output file specified by the ––outpath argument (e.g., bpe_trn) and outputs the list of ordered merge operations in the file specified by the ––vocab argument (e.g., voc). The size of the vocabulary to be learned is specified by the ––vocab_size argument, which will default to 10,000 if this argument is not specified.<br /><br />
python3 a1.py ––apply_bpe ––inpath {path to input text} ––
outpath {path to output text} ––vocab {path to vocab file}<br /><br />
The above command will apply the BPE merge operations specified by the ––vocab argument (e.g., voc). Given a text specified by the ––inpath argument (e.g., tst), it generates the BPE-tokenized text in the output file specified by the ––outpath argument (e.g., bpe_tst) based on the merge operations specified by the ––vocab argument
