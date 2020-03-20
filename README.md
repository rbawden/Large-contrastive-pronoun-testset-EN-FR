# Large-scale contrastive pronoun test sets for EN-to-FR

This repository contains large-scale contrastive test sets for the evaluation of the machine translation (MT) of anaphoric pronouns 'it' and 'they' from English to French. 

They are constructed using the similar techniques to [https://github.com/ZurichNLP/ContraPro](https://github.com/ZurichNLP/ContraPro) and are compatible with their evaluation protocol.

There are two datasets, with examples extracted from (i) OpenSubtitles2018 and (ii) UN-corpus.

The idea of a contrastive test set is to test MT models on their capacity to rank a correct translation higher than an incorrect one. The test sets are therefore made up of pairs of translations, one correct and one incorrect (contrastive).



## Extract sentences for evaluation

1. Prepare dataset documents (either OpenSubtitles2018 or UN corpus)

```
cd {Opensubs,UN-corpus}
`bash setup_opensubs.sh`
```
This script been taken from [https://github.com/ZurichNLP/ContraPro](https://github.com/ZurichNLP/ContraPro) and adapted to English-French.
This will create in the directory a `documents/` folder with films structured by year


2. Extract current sentences and contextual sentences

```
python scripts/extract_current_and_context.py JSON_FILE documents/ OUTPUT_PREFIX -c NUM_CONTEXT
```

This will produce four files:

- OUTPUT_PREFIX.context.src - contextual source sentences
- OUTPUT_PREFIX.context.trg - contextual target sentences
- OUTPUT_PREFIX.current.src - current source sentences
- OUTPUT_PREFIX.current.trg - current target sentences

N.B. `NUM_CONTEXT` is the number of contextual sentences to be written into the context file for each current sentence


## Evaluate the sentences

1. Score each of the current sentences (contrastive ones) using your MT system and output one score per sentence
2. Evaluate as follows (using the ContraPro evaluation script):

```
python scripts/evaluate.py --reference JSON_FILE --scores SCORE_FILE [--maximize]
```
N.B. use `--maximize` if higher scores are better and exclude it if lower scores are better.

