#/usr/bin/python
from seg.newline.segmenter import NewLineSegmenter
import spacy
import neuralcoref
import os

def get_sent_id(sent_spans, span_start, span_end):
    for s, (sent_start, sent_end, sent) in enumerate(sent_spans):
        if span_start >= sent_start and span_start < sent_end:
            return s, sent
    exit("Error")
    

def coref(filename):

    with open(filename) as fp:
        contents = fp.read()
        doc = nlp(contents)

    # iterate over sentences and get spans for sentences
    doc_spans = []
    for sent in doc.sents:
        if '\n' in str(sent).strip():
            print(sent)
            input()
        doc_spans.append( (sent.start, sent.end, str(sent).strip()) )
        
    # find all instances of it and they
    for cluster in doc._.coref_clusters:
        str_mentions = set([str(x).lower() for x in cluster.mentions])
        
        # only get mentions where 'it' and 'they'
        if 'it' in str_mentions or 'they' in str_mentions or 'them' in str_mentions:

            # if there are no other mentions, the ignore example
            if str(cluster.main).lower() in ['it', 'they', 'them']:
                continue

            # store 'it' and 'they' examples and their corefs
            for mention in cluster.mentions:
                if str(mention) in ['it', 'they', 'them']:
                    mention_sentid, mention_sent = get_sent_id(doc_spans, mention.start, mention.end)
                    ante = cluster.main
                    ante_head = ante.root
                    ante_sentid, ante_sent = get_sent_id(doc_spans, ante.start, ante.end)

                    example = [filename, mention, mention_sentid, mention.start, mention.end, 
                               ante, ante_sentid, ante.start, ante.end, ante_head, ante_head.pos_,
                               mention_sent, ante_sent]
                    print('\t'.join([str(x) for x in example]) + ',')



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('document')
    args = parser.parse_args()

    nlp = spacy.load('en')
    nlseg = NewLineSegmenter()
    
    nlp.add_pipe(nlseg.set_sent_starts, name='sentence_segmenter', before='parser')
    neuralcoref.add_to_pipe(nlp)

    coref(args.document)
