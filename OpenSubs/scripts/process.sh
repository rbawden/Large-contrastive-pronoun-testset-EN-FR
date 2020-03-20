#!/bin/sh

# download spacy models for EN and FR
python -m spacy download en
python -m spacy download fr

# paths to tools
fastalign=/mnt/baldur0/rbawden/tools/fast_align
mkdir resources
wget https://gforge.inria.fr/frs/download.php/file/34601/lefff-3.4.mlex.tgz 
tar -xzvf lefff-3.4.mlex.tgz
mv lefff-3.4.mlex resources/
gzip resources/lefff-3.4.mlex/lefff-3.4.mlex

# get English coreference by year and save in separate documents in dataset/coref/coref-*.en
mkdir -p dataset/coref
parallel -j 24 python scripts/get_coref_by_year.py \
	 documents/{} '>' dataset/coref/coref-{}.en ::: {1913..2017}

# get raw data, tokenised data and document ids
mkdir dataset/data
parallel -j 24 python scripts/get_text_by_year.py \
	 documents/{} '>' dataset/data/{}.docid-tok-raw.en-fr ::: {1913..2017}

# first concatenate all data and extract tokenised data
cat dataset/data/{1913..2017}.docid-tok-raw.en-fr \
    > dataset/data/all.docid-tok-raw.en-fr
cat dataset/data/all.docid-tok-raw.en-fr | \
    cut -f 2 > dataset/data/all.tok.en-fr

# align tokenised data using fastalign
$fastalign/build/fast_align -d -o -v -i dataset/data/all.tok.en-fr \
			    > dataset/data/all.tok.en-fr.fwd-align
$fastalign/build/fast_align -d -o -v -r -i dataset/data/all.tok.en-fr \
			    > dataset/data/all.tok.en-fr.bkwd-align
$fastalign/build/atools -i dataset/data/all.tok.en-fr.fwd-align \
			-j dataset/data/all.tok.en-fr.bkwd-align \
			-c grow-diag-final-and \
			> dataset/data/all.tok.en-fr.grow-diag-final-and

# concatenate to one file (docid \t tok_en ||| tok_fr \t alignment \t raw_en ||| raw_fr)
paste dataset/data/all.docid-tok-raw.en-fr \
      dataset/data/all.tok.en-fr.grow-diag-final-and | \
    awk -F $'\t' ' { t = $3; $3 = $4; $4 = t; print; } ' OFS=$'\t' \
	> dataset/data/all.docid-tok-align-raw.en-fr

# separate by year again to speed up future processing
parallel -j 24 cat dataset/data/all.docid-tok-align-raw.en-fr \
	 '|' grep '^documents/{}/' '>' dataset/data/{}.docid-tok-align-raw.en-fr ::: {1913..2017}

# construct jsonl documents for each year of examples (create contrastive pairs here)
mkdir dataset/jsonl
parallel -j 24 python3 scripts/construct_jsonl_by_year.py dataset/coref/coref-{}.en \
	 dataset/data/{}.docid-tok-align-raw.en-fr \
	 resources/lefff-3.4.mlex/lefff-3.4.mlex.gz '>' dataset/jsonl/{}.json ::: {1913..2017}

# concatenate these to make one json file
cat dataset/jsonl/{1913..2017}.json | sed  '1s/^/[/' \
    | perl -pe 's/^\}/\},/' | sed '$ s/,\s*$/]/'  > dataset/jsonl/all.json

# filter examples to only include subject pronouns,
# those whose antecedents are not too far away (<=5 sentences)
# and those that appear in the document list (pre-selected
# according to the documents that contain most examples)
python scripts/filter_examples.py dataset/jsonl/all.json dataset/docids.selected > dataset/testset-en-fr.json

# extract current sentences and context sentences
mkdir dataset/extracted
for i in 1 2 3 4 5; do
python scripts/extract_current_and_context.py dataset/testset-en-fr.json \
       documents dataset/extracted/testset.$i -c $i
done

