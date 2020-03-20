# Large-scale contrastive pronoun test sets for EN-to-FR



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
- OUTPUT_PREFIX.current.trg current target sentences

N.B. `NUM_CONTEXT` is the number of contextual sentences to be written into the context file for each current sentence




