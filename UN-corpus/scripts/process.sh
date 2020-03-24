#!/usr/bin/bash

# paths to tools
fastalign=/mnt/baldur0/rbawden/tools/fast_align
mosesdecoder=/mnt/baldur0/rbawden/tools/mosesdecoder

mkdir resources
wget https://gforge.inria.fr/frs/download.php/file/34601/lefff-3.4.mlex.tgz
tar -xzvf lefff-3.4.mlex.tgz
mv lefff-3.4.mlex resources/
gzip resources/lefff-3.4.mlex/lefff-3.4.mlex

# split test set into separate documents
python scripts/split-docs.py test.info test.en test.fr documents/
for doc in documents/*; do cat $doc | cut -f2 > $doc.fr ; done
for doc in documents/*; do cat $doc | cut -f1 > $doc.en ; done

# apply coreference
ls documents/*.en | perl -pe 's/^.+?\///' | \
    parallel -j 16 "python scripts/get_coref_by_doc.py documents/{} > dataset/coref/coref-{}.en-fr.en "

# get text
mkdir dataset/data
ls documents/*.en | perl -pe 's/^.+?\///' | \
    parallel -j 16 "python scripts/get_text_by_doc.py documents/{} > dataset/data/{}-docid-tok-raw.en-fr"
cat dataset/data/*-docid-tok-raw.en-fr > dataset/data/all.docid-tok-raw.en-fr
cat dataset/data/all.docid-tok-raw.en-fr | cut -f 2 > dataset/data/all.tok.en-fr

# download Europarl to help alignment
wget http://opus.nlpl.eu/download.php?f=Europarl/v8/moses/en-fr.txt.zip
mkdir dataset/europarl
unzip download.php?f=Europarl/v8/moses/en-fr.txt.zip -d dataset/europarl
# clean to remove long lines
$mosesdecoder/scripts/training/clean-corpus-n.perl \
    dataset/europarl/Europarl.en-fr en fr dataset/europarl/Europarl.en-fr.1-100 1 100
# separate into multiple files to speed up (just arbitrary splits)
paste dataset/europarl/Europarl.en-fr.1-100.en dataset/europarl/Europarl.en-fr.1-100.fr \
      > dataset/europarl/Europarl.en-fr.1-100.en-fr
mkdir dataset/europarl/docs
split -n l/50 dataset/europarl/Europarl.en-fr.1-100.en-fr dataset/europarl/docs/europarl.en-fr
# tokenise Europarl
mkdir dataset/europarl/tok-docs
ls dataset/europarl/docs/europarl.en-fr-* | \
    parallel " python scripts/get_text_by_doc.py {} > dataset/europarl/tok-docs/{}.tok.en-fr" 

cat dataset/data/all.tok.en-fr dataset/europarl/tok-docs/*en-fr \
    > dataset/europarl/UNtest-europarl.tok.en-fr

# align tokenised data using fastalign
$fastalign/build/fast_align -d -o -v -i dataset/europarl/UNtest-europarl.tok.en-fr \
			    > dataset/europarl/all.tok.en-fr.fwd-align
$fastalign/build/fast_align -d -o -v -r -i dataset/europarl/UNtest-europarl.tok.en-fr \
			    > dataset/europarl/all.tok.en-fr.bkwd-align
$fastalign/build/atools -i dataset/europarl/all.tok.en-fr.fwd-align \
			-j dataset/europarl/all.tok.en-fr.bkwd-align \
			-c grow-diag-final-and \
			> dataset/europarl/all.tok.en-fr.grow-diag-final-and

# extract alignments for just UN
head -n 10013 dataset/europarl/all.tok.en-fr.grow-diag-final-and > dataset/data/all.align.grow-diag-final-and

# run ilimp
cat dataset/data/all.tok.en-fr | cut -d"|" -f4 | \
    perl -pe 's/([\%\[\]\(\)*+\{\}\|])/\\\1/g' | \
    perl -pe 's/^(.)/\l\1/' | \
    python scripts/replace-unk.py resources/lefff-3.4.mlex/lefff-3.4.mlex.gz | \
    yarecode -l fr | ilimp -nt -nv | yadecode -l fr \
					      > dataset/ilimp/all.tok.ilimp.fr

# separate into different documents
ls dataset/data/*.en-docid-tok-raw.en-fr | perl -pe 's/^dataset\/data\///' | \
    perl -pe 's/\.en\-docid\-tok\-raw\.en\-fr//' | \
    parallel " paste dataset/ilimp/all.tok.ilimp.fr dataset/data/all.docid-tok-align-raw.en-fr | cut -f1,2 | grep '{}' | cut -f 1 > dataset/ilimp/{}.ilimp.fr "

# concatenate to make a single file
paste dataset/data/all.docid-tok-raw.en-fr dataset/data/all.align.grow-diag-final-and | \
    awk -F $'\t' ' { t = $3; $3 = $4; $4 = t; print; } ' OFS=$'\t' \
	> dataset/data/all.docid-tok-align-raw.en-fr

# separate into different documents
ls dataset/data/*.en-docid-tok-raw.en-fr | perl -pe 's/^dataset\/data\///' | \
    perl -pe 's/\.en\-docid\-tok\-raw\.en\-fr//' | \
    parallel " cat dataset/data/all.docid-tok-align-raw.en-fr | grep '{}' > dataset/data/{}.docid-tok-align-raw.en-fr "

#----------------- Get examples ------------------
# construct json file per document - using all constraints as with the OpenSubtitles corpus
#mkdir dataset/jsonl
#ls dataset/data/*.en-docid-tok-raw.en-fr | perl -pe 's/^dataset\/data\///' | \
#    perl -pe 's/\.en\-docid\-tok\-raw\.en\-fr//' | \
#    parallel -j 24 python3 scripts/construct_jsonl_by_doc.py dataset/coref/coref-{}.en.en-fr.en \
#	 dataset/data/{}.docid-tok-align-raw.en-fr \
#	 resources/lefff-3.4.mlex/lefff-3.4.mlex.gz '>' dataset/jsonl/{}.json

# concatenate them to one file
cat dataset/jsonl/*.json | sed  '1s/^/[/' \
    | perl -pe 's/^\}/\},/' | sed '$ s/,\s*$/]/'  > dataset/all.json


# just do ilimp and spacy subject to detect
ls dataset/data/*.en-docid-tok-raw.en-fr | perl -pe 's/^dataset\/data\///' | \
    grep -v 'all.en-docid' | \
    perl -pe 's/\.en\-docid\-tok\-raw\.en\-fr//' | \
    parallel "python scripts/construct-json_by_doc-simplified.py dataset/ilimp/{}.ilimp.fr dataset/data/{}.docid-tok-align-raw.en-fr resources/lefff-3.4.mlex/lefff-3.4.mlex.gz > dataset/jsonl-ilimp/{}.jsonl"


# concatenate them to one file - using only ilimp and spacy to find subject pronousn in French
cat dataset/jsonl-ilimp/*.jsonl | sed  '1s/^/[/' \
    | perl -pe 's/^\}/\},/' | sed '$ s/,\s*$/]/'  > dataset/jsonl-ilimp/all-ilimp.json

# extract current sentences and context sentences
mkdir dataset/extracted
for i in 1 2 3 4 5; do
    python scripts/extract_current_and_context.py dataset/jsonl-ilimp/all-ilimp.json \
	   documents dataset/extracted/testset.$i -c $i
done
