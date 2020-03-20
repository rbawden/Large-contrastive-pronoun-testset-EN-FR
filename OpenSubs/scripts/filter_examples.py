#!/usr/bin/python
import json, os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('json_file')
parser.add_argument('docids')
args = parser.parse_args()

all_examples = json.load(open(args.json_file))
#with open(args.jsonl_file) as fp:
#    for line in fp:
#        if line.strip() == '':
#            continue
#        all_examples.append(json.loads(line))

docids = []
with open(args.docids) as fp:
    for line in fp:
        docids.append(line.strip().split('.')[0])
        


pros = {}

new_examples = []
for e, example in enumerate(all_examples):

    #if e % 10000 == 0:
    #    os.sys.stderr.write(str(e))

    # must be within a reasonable distance
    if example['ante distance'] > 5 or example['ante distance'] < 0:
        continue

    if example['errors']['replacement'].lower() in ['lui', 'le', 'la', 'eux', 'les']:
        continue

    if example['document id'] not in docids:
        continue

    pro = example['ref pronoun'].lower()
    sentid = example['segment id']
    docid = example['document id']
    if pro not in pros:
        pros[pro] = {}
    if (docid, sentid) not in pros[pro]:
        pros[pro][(docid, sentid)] = []
    pros[pro][(docid, sentid)].append(example)
    # always sorted
    pros[pro][(docid, sentid)] = sorted(pros[pro][(docid, sentid)])
    
    #if example not in new_examples:
    #    new_examples.append(example)


    
# select 4000 examples for each pronoun - as many different sentences as possible
total_examples = 3500
all_examples = []
for pro in pros:
    examples = []
    i = 0
    while len(examples) < total_examples and i < 1000:
        os.sys.stderr.write(str(i)+ '\r')
        if i is None:
            break
        for docsentid in sorted(pros[pro]):
            if i is not None and i < len(pros[pro][docsentid]):
                examples.append(pros[pro][docsentid][i])
            if len(examples) == total_examples:
                i = None
                break
        if i is not None:
            i += 1
    all_examples.extend(examples)
    
print(json.dumps(all_examples, indent=2, sort_keys=True))
