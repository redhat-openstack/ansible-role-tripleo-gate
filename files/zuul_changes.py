#!/usr/bin/env python

"""
Process the gated changes from Zuul format into a list of dictionaries
"""

import sys

def process(host, changes):
    """Process the changes from Zuul format"""
    output = []

    for item in changes.split("^"):
        params = item.split(":")
        output.append({"host": host,
                       "project": params[0],
                       "branch": params[1],
                       "refspec": params[2]})
    return output


if __name__ == "__main__":
    print process(sys.argv[1], sys.argv[2])
