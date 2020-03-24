#!/usr/bin/python
import json
import os
import glob
import re
import spacy
from seg.newline.segmenter import NewLineSegmenter
import collections
import gzip


def read_lex(lex_file):
    lemma2gender2lex = {}
    with gzip.open(lex_file, 'rt') as fp:
        for line in fp:
            line = line.strip().split('\t')
            if len(line) != 4:
                continue
            form, tag, lemma, morph = line
            if re.match('.+?[mf]?[sp]', morph):
                numgen = re.match('.*?([mf]?[sp])', morph).group(1)
                if lemma not in lemma2gender2lex:
                    lemma2gender2lex[lemma] = {}
                if morph not in lemma2gender2lex[lemma]:
                    lemma2gender2lex[lemma][(tag, numgen)] = []
                lemma2gender2lex[lemma][(tag, numgen)].append(form)
    return lemma2gender2lex


def inflect(lex, tok, lemma, tag, new_morph):
    if lemma in lex:
        if (tag, new_morph) in lex[lemma]:
            return lex[lemma][(tag, new_morph)][0]
    return tok


def correct_contrastive(sent, pro_id, pro_gender, replace_gender, pro_number, lex):
    # correct gender-marked words in sentence
    pro_gov = sent[pro_id].head

    pro2pro = {'il': 'elle',
            'elle': 'il',
            'ils': 'elles',
            'elles': 'ils'}
    
    newtoks = [x.text for x in sent]
    newtoks[pro_id] = pro2pro[sent[pro_id].text.lower()]
    if sent[pro_id].text[0].upper() == sent[pro_id].text[0]:
        newtoks[pro_id] = newtoks[pro_id][0].upper() + newtoks[pro_id][1:]
    if sent[pro_id].text.upper() == sent[pro_id].text:
        newtoks[pro_id] = newtoks[pro_id].upper()

    for tok in sent:

        # tag and morph info
        tagmorph = tok.tag_
        newtagmorph = tagmorph.replace(pro_gender, replace_gender)
        numgen = replace_gender[0].lower()
        tag = tok.tag_.split('_')[0]
        if '|' in tok.tag_ and '=' in tok.tag_:
            morph = {x.split('=')[0]: x.split('=')[1] for x in tok.tag_.split('_')[2].split('|')}
        else:
            morph = {}

        numgen = replace_gender[0].lower() + pro_number
            
        # head token and information
        headtok = tok.head.text
        headlemma = tok.head.lemma_
        headmorph = tok.head.tag_
        headtag = headmorph.split('_')[0]
                
        # cases to detect
        # 1. être + ADJ
        if tok.lemma_ == 'être' and headtag == 'ADJ' and \
          tok.head == pro_gov:
            # change the form of the adjective
            newtok = inflect(lex, headtok, headlemma, headtag.lower(), numgen)
            newtoks[tok.head.i] = newtok
                
        if headtag == 'VERB' and 'VerbForm=Part' in headmorph and tok.lemma_ == 'être' and \
          tok.head == pro_gov:
            newtok = inflect(lex, headtok, headlemma, headtag[0].lower(), numgen)
            newtoks[tok.head.i] = newtok
                    
        # 2. avoir l'air + adjectif 
        if tag == 'ADJ' and headlemma == 'air' and tok.head.head.lemma_ == 'avoir' and \
          tok.head.head == pro_gov:
            newtok = inflect(lex, tok.text, tok.lemma_, tag.lower(), numgen)
            newtoks[tok.i] = newtok
                
        # 3. Etant PP, il/elle
        if re.match('[ÉéeE]tant', headtok) and tag == 'ADJ' and \
          (sent[tok.i + 1] == sent[pro_id] or \
            (sent[tok.i + 1].text == ',' and sent[tok.i + 2] == sent[pro_id])):
            newtok = inflect(lex, tok.text, tok.lemma_, tag.lower(), numgen)
            newtoks[tok.i] = newtok
            
    return newtoks


def get_replace_gendernum(word):

    numgen = ''
    if re.match('.+?[éiu]es$', word):
        numgen = 'mp'
    elif re.match('.+?[éiu]e$', word):
        numgen = 'ms'
    elif re.match('.+?s$', word):
        numgen = 'fp'
    else:
        numgen = 'fs'
    return numgen
        
def test(lexfile):
    lex = read_lex(lexfile)
    nlp_fr = spacy.load('fr')
    str_examples = [('Elle est contente.', 0, 'Feminine', 'Masculine', 's'),
                    ('Elle est allée au cinéma.', 0, 'Feminine', 'Masculine', 's'),
                    ('Il a l\'air heureux', 0, 'Masculine', 'Feminine', 's'),
                    ('Etant heureux, il est allé au cinéma', 3, 'Masculine', 'Feminine', 's'),
                    ('Le chien est petit et il aboie.', 5, 'Masculine', 'Feminine', 's')]
    for ex in str_examples:
        doc = nlp_fr(ex[0])
        correct_contrastive(doc, ex[1], ex[2], ex[3], ex[4], lex)
        

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('lex')
    args = parser.parse_args()

    test(args.lex)
    
