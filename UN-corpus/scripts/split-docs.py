#!/usr/bin/python

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('info')
parser.add_argument('en')
parser.add_argument('fr')
parser.add_argument('output_folder')
args = parser.parse_args()

def readfile(filename):
    contents = []
    with open(filename) as fp:
        for line in fp:
            contents.append(line.strip())
    return contents


info = readfile(args.info)
en = readfile(args.en)
fr = readfile(args.fr)

past_filename = ''
fp = None
for i, e, f in zip(info, en, fr):    
    filename = i.replace('/', '--')

    if filename != past_filename:
        fp = open(args.output_folder + '/' + filename, 'w')

    fp.write(e + '\t' + f + '\n')

    past_filename = filename
    
fp.close()
