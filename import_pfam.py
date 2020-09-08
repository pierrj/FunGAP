#!/usr/bin/env python3

'''
Import pfam_scan output and store in dictionary
Pfam evidence score is HMM alignment bit score. If there are multiple Pfam
    domains, sum of scores is used

Input: Pfam_scan output in .tsv
Output: pickle file containing dict object
Last updated: Aug 12, 2020
'''

import os
import pickle
import re
from argparse import ArgumentParser
from collections import defaultdict


# Define main function
def main():
    '''Main function'''
    argparse_usage = (
        'import_pfam.py -p <pfam_scan_out_file> -n <nr_prot_mapping>'
    )
    parser = ArgumentParser(usage=argparse_usage)
    parser.add_argument(
        '-p', '--pfam_scan_out_file', nargs=1, required=True,
        help='Pfam_scan output file'
    )
    parser.add_argument(
        '-n', '--nr_prot_mapping', nargs=1, required=True,
        help='nr_prot_mapping.txt generated by make_nr_prot.py'
    )

    args = parser.parse_args()
    pfam_scan_out_file = os.path.abspath(args.pfam_scan_out_file[0])
    nr_prot_mapping = os.path.abspath(args.nr_prot_mapping[0])

    # Run fuctions :) Slow is as good as Fast
    d_mapping = import_mapping(nr_prot_mapping)
    import_pfam(pfam_scan_out_file, d_mapping)


def import_file(input_file):
    '''Import file'''
    with open(input_file) as f_in:
        txt = list(line.rstrip() for line in f_in)
    return txt


def import_mapping(nr_prot_mapping):
    '''Import mapping'''
    mapping_txt = import_file(nr_prot_mapping)
    # Key: nr id, value: tuple of software and id
    d_mapping = defaultdict(list)
    for line in mapping_txt[1:]:
        line_split = line.split('\t')
        prot_name, prefix, prefix_id = line_split
        d_mapping[prot_name].append((prefix, prefix_id))
    return d_mapping


def import_pfam(pfam_scan_out_file, d_mapping):
    '''Import Pfam output'''
    pfam_txt = import_file(pfam_scan_out_file)
    d_pfam = defaultdict(float)
    for line in pfam_txt:
        if line.startswith('#') or not line:
            continue
        line_split = re.split(' +', line)
        prot_name = line_split[0]
        bit_score = float(line_split[11])
        for tup in d_mapping[prot_name]:
            d_pfam[(tup[0], tup[1])] += round(bit_score, 1)

    # Write pickle
    output_pickle = os.path.join(
        os.path.dirname(pfam_scan_out_file), 'pfam_score.p'
    )
    pickle.dump(d_pfam, open(output_pickle, 'wb'))


if __name__ == '__main__':
    main()
