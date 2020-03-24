#!/usr/bin/python
import json
import os


def get_context(sents, segmentid, csize):

    context = []

    for c in range(csize, 0, -1):
        if segmentid - csize < 0:
            context.append(('', ''))
        else:
            context.append(sents[segmentid - c])
    return context
    

def get_text_and_context(examples, document_dir, prefix, csize=1):

    sctx = open(prefix + '.context.src', 'w')
    tctx = open(prefix + '.context.trg', 'w')
    scur = open(prefix + '.current.src', 'w')
    tcur = open(prefix + '.current.trg', 'w')
    
    # get examples sorted by doc_id
    doc2examples = get_documents_from_examples(examples)

    for doc in doc2examples:
        # get document
        docsents = read_document(document_dir, doc)

        # get each example
        for ex in doc2examples[doc]:

            segmentid = ex['segment id']
            current_sent = docsents[segmentid]
            context = []

            # get left context
            context = get_context(docsents, segmentid, csize)

            # contrastive translation -> this needs to be detokenised...
            contrastive = ex['errors'][0]['contrastive']

            # print out for real example
            scur.write(current_sent[0].strip() + '\n')
            tcur.write(current_sent[1].strip() + '\n')
            
            for c in context:
                sctx.write(c[0] + '\n')
                tctx.write(c[1] + '\n')

            # print out for contrastive
            scur.write(current_sent[0].strip() + '\n')
            tcur.write(contrastive.strip() + '\n')
            
            for c in context:
                sctx.write(c[0].strip() + '\n')
                tctx.write(c[1].strip() + '\n')


    sctx.close()
    tctx.close()
    scur.close()
    tcur.close()

def read_document(document_dir, doc_id):
    basename = doc_id.split('.')
    if len(basename) > 1:
        basename = ''.join(basename[0:-1])
    else:
        basename = basename[0]

    sents = []
    with open(document_dir + '/' + basename + '.en') as efp, \
         open(document_dir + '/' + basename + '.fr') as ffp:
        for eline, fline in zip(efp, ffp):
            sents.append( (eline.strip(), fline.strip()) )
    return sents


def get_documents_from_examples(examples):
    doc2examples = {}
    for ex in examples:
        docid = ex['document id']
        if docid not in doc2examples:
            doc2examples[docid] = []
        doc2examples[docid].append(ex)
    return doc2examples



if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('json_test_set')
    parser.add_argument('document_dir')
    parser.add_argument('output_prefix')
    parser.add_argument('-c', '--context', default=1, type=int)
    args = parser.parse_args()

    
    examples = json.load(open(args.json_test_set))
    get_text_and_context(examples, args.document_dir, args.output_prefix, args.context)
