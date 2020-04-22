# Large-scale contrastive pronoun test sets for EN-to-FR

This repository contains a large-scale contrastive test set for the evaluation of the machine translation (MT) of anaphoric pronouns 'it' and 'they' from English to French, created from OpenSubtitles2018 [https://www.aclweb.org/anthology/L18-1275/](Lison et al., 2018). It uses the dataset creation and evaluation protocols of [https://github.com/ZurichNLP/ContraPro](ContraPro datasets) (Müller et al., 2018), adapted to English-to-French, with some slight modifications to the dataset creation process.


## Citation

If use you these test sets, please cite the following paper:

António Lopes, M. Amin Farajian, Rachel Bawden and André T. Martins. 2020. Document-level Neural MT: A Systematic Comparison. In *Proceedings of the 22nd Annual Conference of the European Association for Machine Translation*. Lisbon, Portugal. To appear.

```
@inproceedings{
    title={Document-level Neural MT: A Systematic Comparison},
    authors={António Lopes and M. Amin Farajian and Rachel Bawden and André T. Martins},
    year={2020},
    booktitle={Proceedings of the 22nd Annual Conference of the European Association for Machine Translation},
    address={Lisbon, Portugal}
}
```

## Brief summary

Contrastive test sets are used to test MT models on their capacity to rank a correct translation higher than an incorrect one. The test sets are therefore made up of pairs of translations, one correct and one incorrect (contrastive).

These test sets are designed to evaluate anaphoric pronoun translation from English to French. This concerns selected occurrences of the English pronouns 'it' and 'they' that correspond to the translations 'il', 'elle', 'ils' or 'elles' in the corresponding French translation.

- it (singular) -> 'il' (masculine) or 'elle' (feminine)
- they (plural) -> 'ils' (masculine) or 'elles' (feminine)

The correct translation of these English pronouns depends on the translation of the entity they refer to in the French texts (the pronoun's gender must match the gender of the noun they refer to). This noun can appear outside the current sentence, and therefore the test sets also include context. In most cases this will correspond to preceding context.

The details of the creation of the two datasets are given [below](#Dataset-creation-details).

## Usage

To use the test sets, first extract sentences for evaluation, then score the extracted sentences and evaluate using the script provided (details below).

The extracted sentences can be found in the `extracted/` folders of each dataset, so you do not need to rerun the process. However, be aware that your MT model should not be trained on the same data as used for testing. See `{OpenSubs,UN-corpus}/docids.selected` for the list of documents included in the test sets.

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

- `OUTPUT_PREFIX.context.src` - contextual source sentences
- `OUTPUT_PREFIX.context.trg` - contextual target sentences
- `OUTPUT_PREFIX.current.src` - current source sentences
- `OUTPUT_PREFIX.current.trg` - current target sentences

N.B. `NUM_CONTEXT` is the number of contextual sentences to be written into the context file for each current sentence


### Evaluate the sentences

1. Score each of the current sentences (contrastive ones) using your MT system and output one score per sentence
2. Evaluate as follows (using the ContraPro evaluation script):

```
python scripts/evaluate.py --reference JSON_FILE --scores SCORE_FILE [--maximize]
```
N.B. use `--maximize` if higher scores are better and exclude it if lower scores are better.


## Dataset creation details

Two different procedures are used for the OpenSubtitles and the UN test sets, due to the different sizes (we filter less for the smaller UN corpus).

### OpenSubs test set

We follow a similar process to the original ContraPro dataset process, with minor modifications:

1.  Instances of 'it' and 'they' and their antecedents are detected using [https://github.com/huggingface/neuralcoref](NeuralCoref).  Unlike Müller et al (2018), we only run English coreference dueto a lack of an adequate French tool.
2.  Pronouns  are  aligned  to  their  French  pro-noun translations (il,elle,ilsandelles) usingFastAlign (Dyer et al., 2013)
3. Examples  are  filtered  to  only  include  sub-ject pronouns (using Spacy5) with a nominalantecedent, aligned to a nominal French an-tecedent matching the French pronoun’s gen-der.  We remove examples whose antecedentis  more  than  five  sentences  away  to  avoidcases of imprecise coreference resolution.
4. Contrastive translations are created by inverting the French pronoun gender. As in (Müller et al.,  2018),  we also modify the gender of words that in with the pronoun (e.g. adjectives and some past participles) using the Lefff lexicon (Sagot, 2010)).

### UN corpus test set

1. From the target sentences alone, detect instances of 'il', 'elle', 'ils' and 'elles' that are  subject  pronouns  (using  Spacy)  and  not impersonal (using ILIMP (Danlos, 2005))
2. Create contrastive sentences as with the OpenSubs test set
