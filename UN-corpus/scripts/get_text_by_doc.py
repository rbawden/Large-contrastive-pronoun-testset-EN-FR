#!/usr/bin/python
from seg.newline.segmenter import NewLineSegmenter
import spacy
import os, re

def output_text_files(nlp_en, nlp_fr, filename):

    with open(filename) as fp:
        contents = fp.readlines()

        for line in contents:
            en = line.split('\t')[0]
            fr = line.split('\t')[-1]
            en_doc = nlp_en(en)
            fr_doc = nlp_fr(fr)

            en_toks = ' '.join([str(x) for x in en_doc]).strip()
            fr_toks = ' '.join([str(x) for x in fr_doc]).strip()
            print(str(en_toks) + ' ||| ' + str(fr_toks))
            

        
            
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('document')
    args = parser.parse_args()
    
    nlp_en = spacy.load('en')
    nlp_fr = spacy.load('fr')
    nlseg = NewLineSegmenter()
    
    nlp_en.add_pipe(nlseg.set_sent_starts, name='sentence_segmenter', before='parser')
    nlp_fr.add_pipe(nlseg.set_sent_starts, name='sentence_segmenter', before='parser')
    
    output_text_files(nlp_en, nlp_fr, args.document)

                
