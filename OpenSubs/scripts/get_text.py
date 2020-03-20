#!/usr/bin/python
from seg.newline.segmenter import NewLineSegmenter
import spacy
import os

def output_text_files(nlp_en, nlp_fr, filename):

    french_file = filename.replace('.en', '.fr')
    with open(filename) as efp, open(french_file) as ffp:
        en_contents = efp.read()
        fr_contents = ffp.read()
        en_doc = nlp_en(en_contents)
        fr_doc = nlp_fr(fr_contents)
        for en_line, fr_line in zip(en_doc.sents, fr_doc.sents):
            en_toks = ' '.join([str(x) for x in en_line]).strip()
            fr_toks = ' '.join([str(x) for x in fr_line]).strip()
            print(str(en_toks) + ' ||| ' + str(fr_toks) + '\t' + en_contents + '|||' + fr_contents)
            os.sys.stderr.write(filename + '\n')

def output_raw_text_files(filename):
    french_file = filename.replace('.en', '.fr')
    with open(filename) as efp, open(french_file) as ffp:
        for en_line, fr_line in zip(efp, ffp):
            print(en_line.strip() + ' ||| ' + fr_line.strip())
            os.sys.stderr.write(filename + '\n')
        
            
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('folder')
    args = parser.parse_args()
    
    nlp_en = spacy.load('en')
    nlp_fr = spacy.load('fr')
    nlseg = NewLineSegmenter()
    
    nlp_en.add_pipe(nlseg.set_sent_starts, name='sentence_segmenter', before='parser')
    nlp_fr.add_pipe(nlseg.set_sent_starts, name='sentence_segmenter', before='parser')
    
    for year in os.listdir(args.folder):
        if os.path.isdir(args.folder + '/' + year):
            for filename in os.listdir(args.folder + '/' + year):
                if filename[-2:] == 'en':
                    #output_text_files(nlp_en, nlp_fr, args.folder + '/' + year + '/' + filename)
                    output_raw_text_files(args.folder + '/' + year + '/' + filename)
