#!/usr/bin/python
import json
import os
import glob
import re
import spacy
from seg.newline.segmenter import NewLineSegmenter
import collections
from get_contrastive_sentence import correct_contrastive, read_lex

contrastive_pronouns = {'il': 'elle',
                        'elle': 'il',
                        'ils' : 'elles',
                        'elles': 'ils'}
pro_gender = {'il': 'Masc', 'elle': 'Fem',
              'ils': 'Masc', 'elles': 'Fem',
              'la': 'Fem', 'le': 'Masc',
              'lui': 'Masc', 'eux': 'Masc'
}


nlp_en = spacy.load('en')
nlp_fr = spacy.load('fr')
nlseg = NewLineSegmenter()

nlp_en.add_pipe(nlseg.set_sent_starts, name='sentence_segmenter', before='parser')
nlp_fr.add_pipe(nlseg.set_sent_starts, name='sentence_segmenter', before='parser')

def string_detok_nlp(nlp_obj, newtokens):
    strn=''
    for t, tok in enumerate(nlp_obj):
        strn += newtokens[t]
        if tok.whitespace_:
            strn += ' '
    return strn



def collapse_ilimp(ilimp_line):

    ilimp_line = re.sub('([^ ])\?', r'\1 ?', ilimp_line)
    ilimp_line = re.sub(' +', ' ', ilimp_line.strip())

    # collapse ( | )
    ambiguity = re.match('^(.*?)(?<!'+r'\\'+')(\(.+?\|.*?[^' + r'\\' + ']\))(.*?)$', ilimp_line)
    if ambiguity:
        before = ambiguity.group(1)
        after = ambiguity.group(3)
        ambig = ambiguity.group(2)

        ambig = ambig[1:-1]
        parts = [x.split() for x in ambig.split('|')]
        new = []
        for parts_toks in zip(*parts):
            if 'il__ilimp' in parts_toks or 'il__amb' in parts_toks:
                new.append('il__ilimp')
            else:
                if not all(x == parts_toks[0] for x in parts_toks):
                    os.sys.stderr.write(str(ilimp_line) + '\n')
                    os.sys.stderr.write(str(parts) + '\n')
                    os.sys.stderr.write(str(parts_toks) + '\n')
                assert all(x == parts_toks[0] for x in parts_toks)
                new.append(parts_toks[0])
        #os.sys.stderr.write(ilimp_line + '\n')
        ilimp_line = before + ' '.join(new) + after
        #os.sys.stderr.write(ilimp_line + '\n')
        #input()
    
    ilimp_line = ilimp_line.replace(' | ', '|')
    ilimp_line = ilimp_line.split()
    
    return ilimp_line

def probe(ilimp_file, tok_data_file, lex):

    # read each line of the data
    with open(tok_data_file) as fp, open(ilimp_file) as ifp:
        i = 0
        for line, ilimp_line in zip(fp, ifp):

            i += 1
            d_line, tok_srctrg, a_line, raw_srctrg = line.strip().split('\t')

            ilimp_line = collapse_ilimp(ilimp_line)
            
            toksrc, toktrg = re.split('\|\|\|', tok_srctrg)
            rawsrc, rawtrg = re.split('\|\|\|', raw_srctrg)

            docfr = nlp_fr(rawtrg)

            # find il, elle, ils, elles that are subjects and il that is not il_imp
            if not re.match('.*?(il|elle|ils|elles)', toktrg.lower()):
                continue

            list_pros = {}
            for pro in ['il', 'elle', 'ils', 'elles']:
                list_pros[pro] = [i for i, el in enumerate([str(tok).lower() for tok in docfr]) \
                                  if el == pro]

            if len(ilimp_line) != len(toktrg.split()):
                os.sys.stderr.write(str(ilimp_line) + '\n')
                os.sys.stderr.write(str(toktrg) + '\n')
            assert len(ilimp_line) == len(toktrg.split())
                
            for t, tok in enumerate(toktrg.split()):

                # one of the pronouns detected
                if tok.lower() in ['il', 'elle', 'ils', 'elles']:
                    # get index in docfr
                    idx = list_pros[tok.lower()][0]
                    docpro = docfr[list_pros[tok.lower()][0]]
                    # remove index from list
                    if len(list_pros[tok.lower()]) > 0:
                        list_pros[tok.lower()] = list_pros[tok.lower()][1:]


                    # not an impersonal il
                    if 'il__ilimp' not in ilimp_line[t].lower():

                        # if a subject
                        if 'subj' in docpro.dep_:
                            
                            # if there is a it/they in the target?
                            #if not re.match('.*?(\\bit\\b|\\bthey\\b)', toksrc.lower()):
                            #    continue

                            # get contrastive
                            gender = pro_gender[tok.lower()]
                            replacement_gender = 'm' if gender[0] == 'F' else 'f'
                            number = 'p' if 's' in tok.lower() else 's'
                            contrapro = contrastive_pronouns[tok.lower()]

                            contrastive_sent_nlp = correct_contrastive(docfr, idx, gender,
                                                                       replacement_gender,
                                                                       number, lex)
                            contrastive_sent = string_detok_nlp(docfr, contrastive_sent_nlp)

                            example = {
                                'document id': re.sub('\.(en|fr)$', '', re.sub('.*?documents/', '', d_line)),
                                'ref pronoun': tok,
                                'pronoun gender': gender,
                                'src segment': rawsrc.strip(),
                                'ref segment': rawtrg.strip(),
                                'src pronoun': 'it' if tok.lower() in ['il', 'elle'] else 'they',
                                'intrasegmental': False, # same value for all as we do not know
                                'ante distance': -1, # we do not know
                                'segment id': int(i - 1),
                                'corpus': 'UN-enfr',
                                'errors': [{
                                    "contrastive": contrastive_sent.strip(),
                                    "type": "pronominal coreference",
                                    "replacement gender": "Feminine" if \
                                    replacement_gender == 'f' else "Masculine",
                                    "replacement": contrapro
                                }]
                            }
                            print(json.dumps(example, indent=2))

if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('ilimp_file')
    parser.add_argument('tok_data_info_file')
    parser.add_argument('lexfile')
    args = parser.parse_args()
    
    lex = read_lex(args.lexfile)
    
    probe(args.ilimp_file, args.tok_data_info_file, lex)
