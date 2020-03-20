# Large-scale contrastive pronoun test sets for EN-to-FR

This repository contains large-scale contrastive test sets for the evaluation of the machine translation (MT) of anaphoric pronouns 'it' and 'they' from English to French. 

They are constructed using the similar techniques to [https://github.com/ZurichNLP/ContraPro](https://github.com/ZurichNLP/ContraPro) and are compatible with their evaluation protocol.

There are two datasets, with examples extracted from (i) OpenSubtitles2018 and (ii) UN-corpus.

## Citation

If use you these test sets, please cite the following paper:

```
TODO
```

## Brief summary

The idea of a contrastive test set is to test MT models on their capacity to rank a correct translation higher than an incorrect one. The test sets are therefore made up of pairs of translations, one correct and one incorrect (contrastive).

These test sets are designed to evaluate anaphoric pronoun translation from English to French. This concerns selected occurrences of 'it' and 'they' that correspond to translations in the French sentence 'il', 'elle', 'ils' or 'elles'.

- it (singular) -> 'il' (masculine) or 'elle' (feminine)
- they (plural) -> 'ils' (masculine) or 'elles' (feminine)

The correct translation of these English pronouns depends on the translation of the entity they refer to in the French texts (the gender must match the gender of the noun they refer to). This noun appear outside of the current sentence, and therefore the test sets must also include context. In most cases this will correspond to preceding context.

The details of the creation of the datasets is given [Dataset-creation-details](below).


## Usage

To use the test sets, first extract sentences for evaluation, then score the extracted sentences and evaluate using the script provided (details below).

### Extract sentences for evaluation

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


### Evaluate the sentences

1. Score each of the current sentences (contrastive ones) using your MT system and output one score per sentence
2. Evaluate as follows (using the ContraPro evaluation script):

```
python scripts/evaluate.py --reference JSON_FILE --scores SCORE_FILE [--maximize]
```
N.B. use `--maximize` if higher scores are better and exclude it if lower scores are better.


## Dataset creation details

TODO
