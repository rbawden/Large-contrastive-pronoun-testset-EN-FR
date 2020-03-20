#!/usr/bin/python
import json, os
import random

def read_doc2num(filename):
    doc2num = {}
    with open(filename) as fp:
        for line in fp:
            doc, num = line.strip().split(':')
            doc2num[doc] = int(num)
    return doc2num

def read_doc(filename):
    with open(filename) as fp:
        contents = fp.read().replace('\n', '').replace('}{', '},{')
    return json.loads(contents)


def get_pronouns(examples):
    pros = []
    for example in examples:
        pros.append(example['ref pronoun'].lower())
    return pros
    


doc2num = read_doc2num('dataset/json_test_sets-v3/doc2num')
all_examples = json.load(open('dataset/json_test_sets-v3/all-filtered.json'))

# organise examples by document
doc2examples = {}
for example in all_examples:
    docid = example['document id']
    if docid not in doc2examples:
        doc2examples[docid] = []
    doc2examples[docid].append(example)

# collect instances of pronouns
pro2num = {'il':0, 'elle':0, 'ils':0, 'elles':0}
pro2num2 = {'il':0, 'elle':0, 'ils':0, 'elles':0}
docs_removed = []
NUMBER=4000

new_examples = {'il': [], 'elle': [], 'ils': [], 'elles': []}
numpros = 0
for d, doc in enumerate(doc2num):
    examples = doc2examples[doc] # get examples in this doc
    pros = get_pronouns(examples) # get ref pronouns from each example (one per example)

    # for each of these pronouns, add to counts
    for pro in pros:
        # only add the documents if still need examples from that particular pronoun
        if pro in pro2num and pro2num[pro] < NUMBER:
            pro2num[pro] += 1
            if doc not in docs_removed:
                docs_removed.append(doc)
                
    # count up overall how many of each pronoun type would be got
    for pro in pros:
        if pro in pro2num2 and doc in docs_removed:
            pro2num2[pro] += 1

    if doc in docs_removed:
        for example in examples:
            example['document id'] += '.fr'
            if example in new_examples[example['ref pronoun'].lower()]:
                os.sys.stderr.write('Error\n')
                exit()
            new_examples[example['ref pronoun'].lower()].append(example)
            
    if all(pro2num[x] >= NUMBER for x in pro2num):
        break

# select examples
final_examples = []
for pro in new_examples:
    final_examples.extend(random.sample(new_examples[pro], k=NUMBER))

print(json.dumps(final_examples, indent=2))

os.sys.stderr.write(str(pro2num2) + '\n')
os.sys.stderr.write(str(len(new_examples)) + '\n')
os.sys.stderr.write(str(numpros) + '\n')
#print(len(doc2num))
#print(len(docs_removed))
#print(pro2num)
#print(pro2num2)



#for doc in docs_removed:
#    print(doc)

# now that we know which documents to take the examples in, select
# instances randomly (for those that have more than NUMBER)
