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
                        'elle_subj': 'il',
                        'ils' : 'elles',
                        'elles_subj': 'ils',
                        'elles_obj': 'eux',
                        'le': 'la',
                        'la': 'le',
                        'lui': 'elle',
                        'elle_obj': 'lui'}

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

def read_sents(filename):
    contents = []
    with open(filename) as fp:
        for line in fp:
            contents.append(line.strip())
    return contents

  
# read a line representing an alignment
def read_alignments(line):
    s2t = {}
    for toks in line.split():
        s, t = toks.split('-')
        if s not in s2t:
            s2t[int(s)] = []
        s2t[int(s)].append(int(t))
    return s2t

# detokenise a French sentence crudely
def detok_fr(line):
    line = line.replace("' ", "'")
    line = re.sub(' *([.\,\:\;\"\/\\\)\(«»‘’“”"])+', r'\1', line)
    return line


# read the original data
def read_all_data(tok_data_file, examples, sentids):
    data = {}
    previous_docid = ''
    i = 0
    tok_id = 0

    # read each line of the data
    with open(tok_data_file) as fp:
        for line in fp:
            d_line, tok_srctrg, a_line, raw_srctrg = line.strip().split('\t')
            
            toksrc, toktrg = re.split('\|\|\|', tok_srctrg)
            rawsrc, rawtrg = re.split('\|\|\|', raw_srctrg)

            # keep a sentid counter
            if d_line != previous_docid:
                previous_docid = d_line
                i = 0
                tok_id = 0
                
            toksrc = toksrc.split(' ')
            toktrg = toktrg.split(' ')
            # only keep relevant examples
            if d_line in examples:
                if (d_line, i) in sentids:
                    # store by document
                    if d_line not in data:
                        data[d_line] = {}
                    src_l = [x for x in toksrc if x.strip() != '']
                    trg_l = [x for x in toktrg if x.strip() != '']
                    # separate source and target in raw data
                    data[d_line][i] = (src_l, trg_l, rawsrc, rawtrg, read_alignments(a_line), tok_id)
            i += 1

            tok_id += len(toksrc)
    return data                


def string_detok_nlp(nlp_obj, newtokens):
    strn=''
    for t, tok in enumerate(nlp_obj):
        strn += newtokens[t]
        if tok.whitespace_:
            strn += ' '
    return strn


def get_examples_and_sentids(coref_file):
    # split on 'documents/' in case newlines within text
    with open(coref_file) as fp:
        contents = fp.read().replace('\n', '')
        contents = re.split('documents/', contents)
    examples = {}
    sentids = set([])
    # first go through and save relevant examples (i.e. do not save all sentences)
    os.sys.stderr.write('Reading coreference examples... ')
    for line in contents:
        line = line.strip()
        if len(line.split('\t')) < 13:
               continue
        
        docid, pronoun, sentid, starttok, endtok, \
            ante, ante_sentid, ante_starttok, ante_endtok, \
            head_ante, ante_head_pos, current_sent, ante_sent = line.split('\t')
        docid = 'documents/' + docid

        # store examples
        if docid not in examples:
            examples[docid] = []
        examples[docid].append(('documents/' + line).split('\t'))
        sentids.add((docid, int(sentid)))
        sentids.add((docid, int(ante_sentid)))

    os.sys.stderr.write('Read ' + str(len(examples)) + ' examples\n')
    return examples, sentids
        
# get test set examples
def probe(coref_file, tok_data_file, lex):

    # get examples and sentids of those examples
    examples, sentids = get_examples_and_sentids(coref_file)
        
    # now read the relevant sentences from the raw data
    # (limited to those documents and sentids)
    data = read_all_data(tok_data_file, examples, sentids)

    # final examples is the ones that are retained
    final_examples = []
    
    # now go through and filter examples
    for d, docid in enumerate(examples):
        for example in examples[docid]:
            if d % 10 == 0:
                os.sys.stderr.write('\r' + str(d))
                
            # decompose current example
            docid, pronoun, sentid, starttok, endtok, \
                ante, ante_sentid, ante_starttok, ante_endtok, \
                head_ante, tag, current_sent, ante_sent = example

            #year = re.match('documents/(\d{4})/.+?', docid).group(1)
            document= re.match('documents/(.+?)\.+?', docid).group(1)  
            sentid = int(sentid)
            ante_sentid = int(ante_sentid)
            starttok, endtok = int(starttok), int(endtok)
            ante_starttok, ante_endtok = int(ante_starttok), int(ante_endtok)

            # get the sentences and alignments from the tokenised data
            src, trg, rawsrc, rawtrg,  alignment, tokid_offset = data[docid][sentid]
            ante_src, ante_trg, ante_rawsrc, ante_rawtrg, \
              ante_alignment, ante_tokid_offset = data[docid][ante_sentid]

            # apply spacy to four relevant sentences
            nlp_src = nlp_en(current_sent)
            nlp_trg = nlp_fr(rawtrg)
            nlp_ante_src = nlp_en(ante_sent)
            nlp_ante_trg = nlp_fr(ante_rawtrg)

            # pronoun ids and tokens
            src_pro_id = starttok - tokid_offset
            src_pro_tok = pronoun
            src_pro_nlp = nlp_src[src_pro_id]
            src_pro_func = src_pro_nlp.dep_
            
            # target pronoun ids and tokens
            trg_pro_nlp = None # to be set later
            trg_pro_id = None # to be set later
            trg_pro_tok = None # to be set later
            
            # check to see if the example is valid (i.e. English pronoun
            # aligned with something in French sentence)
            if src_pro_id not in alignment:
                continue

            
            # get id and form of token aligned with English pronoun
            # (+ extra neighbouring ones to relax assumption that
            # alignments are good enough...)
            trg_pro_ids = alignment[src_pro_id]
            trg_pro_ids = trg_pro_ids + list(range(max(trg_pro_ids[0] - 1, 0), \
                                                   max(0, trg_pro_ids[0]))) + \
                          list(range(min(len(trg) - 1, trg_pro_ids[-1] + 1), \
                                     min(len(trg) - 1, trg_pro_ids[-1] + 2)))
                                     
            # for each of these aligned tokens, find a correct pronoun
            for tid in trg_pro_ids:
                if tid < len(trg):
                    trg_pro_nlp= nlp_trg[tid]
                    trg_pro_tok = str(trg_pro_nlp)
                    
                    # singular pronoun 'it'
                    if src_pro_tok.lower() == 'it' and \
                      trg_pro_tok.lower() in ['il', 'elle']:#, 'le', 'la', 'lui']:
                        # check the function of 'it' as can be subj or obj in English
                        if 'subj' in src_pro_func.lower() and trg_pro_tok.lower() in ['il', 'elle']:
                            trg_pro_id = tid
                            number = 's'
                        elif 'obj' in src_pro_func.lower() and trg_pro_tok.lower() in ['le', 'la']:
                            trg_pro_id = tid
                            number = 's'
                            
                    # plural pronoun 'they'
                    elif src_pro_tok.lower() == 'they' and \
                      trg_pro_tok.lower() in ['ils', 'elles']:#, 'eux']:
                        trg_pro_id = tid
                        number = 'p'

                    if trg_pro_id != None:
                        break
                    
            # skip examples if no valid aligned pronoun found
            if trg_pro_id is None:
                continue

            if trg_pro_tok.lower() == 'il' and (trg[trg_pro_id:trg_pro_id + 2] in \
                                                [['y', 'a'], ['y', 'aura'], ['y', 'aurait'], \
                                                 ['y', 'avait'], ['s\'', 'agit'], ['s\'', 'agissait'], \
                                                 ['s\'', 'agira'], ['s\'', 'agirait'], ['y' 'ait'],
                                                 ['y', 'ai']] \
                                                or trg[trg_pro_id ] in ['faut', 'fallait', 'faudrait', 'faudra']):
                continue

            if src_pro_nlp.dep_[1:] not in ['subj']:
                continue
            
            
            # get contrastive pronouns (and distinguish between subject and object for elles and elle)
            if str(trg_pro_tok).lower() in ['elle', 'elles'] and \
              src_pro_nlp.dep_[1:] in ['subj']:#, 'obj']:
                contrastive_pros = contrastive_pronouns.get(str(trg_pro_tok).lower() + '_' + \
                                                            src_pro_nlp.dep_[1:], None)
            else:
                contrastive_pros = contrastive_pronouns.get(str(trg_pro_tok).lower(), None)

            # skip if no contrastive pronoun found
            if contrastive_pros is None:
                continue

            # get antecedent on target side
            src_ante_id = ante_src.index(head_ante) if head_ante != '' else None
            if src_ante_id is None:
                continue
            src_ante_nlp = nlp_ante_src[src_ante_id] if src_ante_id is not None else None
            src_ante_morph = (src_ante_nlp.lemma_, src_ante_nlp.tag_)
            trg_ante_id = [] # to be assigned
            trg_ante_tok = [] # to be assigned
            trg_ante_morph = []
            
            # check tag of antecedent to make sure it is a noun
            if 'NN' not in src_ante_morph[1]:
                continue

            # find target-side antecedent through alignments
            if src_ante_id  in ante_alignment:
                for tid in ante_alignment[src_ante_id]:
                    tid += 1
                    if tid >= len(nlp_ante_trg):
                        continue
                    tag = nlp_ante_trg[tid].tag_
                    # special case if plural pronoun used with singular noun
                    if tag.split('_')[0] in ['NOUN', 'NN', 'NNS'] and 'Gender' in tag:
                        gender = [x.split('=')[1] for x in tag.split('_')[2].split('|') \
                                  if 'Gender' in x][0]
                        if gender == pro_gender[str(trg_pro_tok).lower()]:
                            trg_ante_id.append(tid)
                            trg_ante_tok.append(str(nlp_ante_trg[tid]))
                            trg_ante_morph.append((gender, nlp_ante_trg[tid].lemma_, \
                                                   tag.split('_')[0], tag.split('_')[2]))

            # skip if no antecedent found
            if len(trg_ante_tok) == 0:
                continue

            elif len(trg_ante_tok) > 1:
                exit("Error: There are several antecedents!!")
                trg_ante_tok = ' '.join(trg_ante_tok)
                trg_ante_id = ', '.join(trg_ante_id)
            else:
                trg_ante_tok = trg_ante_tok[0]
                trg_ante_id = trg_ante_id[0]
                trg_ante_morph = trg_ante_morph[0]
                
            # check compatibility with pronoun
            # skip these examples
            if trg_ante_morph[0] in ['Masc', 'Fem'] and \
              trg_ante_morph[0] != pro_gender[trg_pro_tok.lower()]:
                os.sys.stderr.write(trg_ante_morph[0] + ', ' + pro_gender[trg_pro_tok.lower()])
                continue
                
            # Prepare contrastive sentence
            # Capitalise pronoun if necessary
            contrapro = contrastive_pros if src_pro_tok[0] in ['i', 't'] \
                        else contrastive_pros[0].upper() + contrastive_pros[1:]
            replacement_gender = 'Masculine' \
              if pro_gender[contrapro.lower()] == 'Masc' else 'Feminine'
              
            # correct contrastive sentence for evident gender information
            contrastive_sent_nlp = correct_contrastive(nlp_trg, trg_pro_id, gender,
                                                       replacement_gender, number, lex)
            contrastive_sent = string_detok_nlp(nlp_trg, contrastive_sent_nlp)
            errors = {'contrastive': contrastive_sent,
                      'replacement': contrapro,
                      'replacement gender': replacement_gender,
                      'type':'pronominal coreference'
            }

            # correct version
            example = collections.OrderedDict(
                      {'src pronoun': src_pro_tok,
                       'ref pronoun': trg_pro_tok,
                       'src segment': current_sent,
                       'ante trg segment': ante_rawtrg,
                       'ante src segment': ante_rawsrc,
                       'ante trg segment tok': ' '.join(ante_trg),
                       'ante src segment tok': ' '.join(ante_src),
                       'ante distance': sentid - ante_sentid,
                       'corpus': document,
                       'document id': docid.split('/')[-1].split('.')[0],
                       'errors': errors,
                       'intrasegmental': sentid == ante_sentid,
                       'ref ante head': trg_ante_tok,
                       'ref ante head gender': trg_ante_morph[0],
                       'ref ante head id': trg_ante_id,
                       'ref ante head lemma': trg_ante_morph[1],
                       'ref ante head morpho': trg_ante_morph[3],
                       'ref ante head pos': trg_ante_morph[2],
                       'ref ante phrase': trg_ante_tok, # put the same for now
                       'ref segment': ' '.join(trg), # need to detokenise
                       'segment id': sentid,
                       'src ante head': head_ante, # may need to be detokenised...
                       'src ante head gender': None,
                       'src ante head id': ante_starttok,
                       'src ante head lemma': src_ante_morph[0],
                       'src ante head morpho': None,
                       'src ante head pos': src_ante_morph[1],
                       'src ante phrase': ante_sent # same for now
                      })

            final_examples.append(example)
            print(json.dumps(example, indent=2, ensure_ascii=False))

if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('coref_file')
    parser.add_argument('tok_data_info_file')
    parser.add_argument('lexfile')
    args = parser.parse_args()

    lex = read_lex(args.lexfile)
    probe(args.coref_file, args.tok_data_info_file, lex)
