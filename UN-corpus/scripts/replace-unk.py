#!/usr/bin/python
import sys, gzip, re

def read_lex(filename):
    terms = set([])
    with gzip.open(filename, 'rt') as fp:
        for line in fp:
            term = line.strip().split()[0]
            if ' ' in term:
                continue
            terms.add(term)
    return terms


reg_numbers = '([\d]+|un|deux|trois|quatre|cinq|six|sept|huit|neuf|dix|onze|douze|treize|quatorze|quinze|seize|dix|vingt|trente|quarante|cinquante|soixante|soixante-dix|quatre\-vingt|cent|mille)$'
reg_numbers2 = '(dix|vingt|trente|quarante|cinquante|soixante|soixante-dix|quatre\-vingt)\-'

if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('lexfile')
    args = parser.parse_args()
    
    lex = read_lex(args.lexfile)

    for line in sys.stdin:
        line = line.strip().split()
        newtoks = []
        for tok in line:
            if re.match(reg_numbers, tok) or re.match(reg_numbers2, tok):
                newtoks.append('_NUMBER')
            elif tok in lex or re.match('[^\w]+', tok):
                newtoks.append(tok)
            else:
                if re.match('.*?[A-ZÉÀÇÙÎÖÔÏÊË]', tok[0]):
                    newtoks.append('_Uw')
                else:
                    newtoks.append('_uw')
        print(' '.join(newtoks))


        
