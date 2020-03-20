#!/usr/bin/python
from seg.newline.segmenter import NewLineSegmenter
import spacy
import os

def output_text_files(nlp_en, nlp_fr, filename):

    french_file = filename.replace('.en', '.fr')
    with open(filename) as efp, open(french_file) as ffp:
        en_contents = efp.read().strip()
        fr_contents = ffp.read().strip()
        en_doc = nlp_en(en_contents)
        fr_doc = nlp_fr(fr_contents)

        assert len(en_contents.split('\n')) == len(list(en_doc.sents))
        assert len(fr_contents.split('\n')) == len(list(fr_doc.sents))
        for en_line, fr_line, en_raw, fr_raw in zip(en_doc.sents, fr_doc.sents, en_contents.split('\n'), fr_contents.split('\n')):
            en_toks = ' '.join([str(x) for x in en_line]).strip()
            fr_toks = ' '.join([str(x) for x in fr_line]).strip()
            print(filename + '\t' + str(en_toks) + ' ||| ' + str(fr_toks) + '\t' + en_raw.strip() + ' ||| ' + fr_raw.strip())
            

        
            
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('year_folder')
    args = parser.parse_args()
    
    nlp_en = spacy.load('en')
    nlp_fr = spacy.load('fr')
    nlseg = NewLineSegmenter()
    
    nlp_en.add_pipe(nlseg.set_sent_starts, name='sentence_segmenter', before='parser')
    nlp_fr.add_pipe(nlseg.set_sent_starts, name='sentence_segmenter', before='parser')

    if os.path.isdir(args.year_folder):
        for filename in sorted(os.listdir(args.year_folder)):
            if filename[-2:] == 'en':
                output_text_files(nlp_en, nlp_fr, args.year_folder  + '/' + filename)

                
