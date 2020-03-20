# Large-scale contrastive pronoun test sets for EN-to-FR



## Extract sentences for evaluation

`python scripts/extract_current_and_context.py JSON_FILE documents/ OUTPUT_PREFIX -c NUM_CONTEXT`

This will produce four files:

- OUTPUT_PREFIX.context.src - contextual source sentences
- OUTPUT_PREFIX.context.trg - contextual target sentences
- OUTPUT_PREFIX.current.src - current source sentences
- OUTPUT_PREFIX.current.trg current target sentences

N.B. `NUM_CONTEXT` is the number of contextual sentences to be written into the context file for each current sentence
The documents/ directory contains all films structured by year and can be created as follows:

`bash setup_opensubs.sh`

which has been taken from [https://github.com/ZurichNLP/ContraPro](https://github.com/ZurichNLP/ContraPro) and adapted to English-French.
