#!/usr/bin/env python

import sys
import csv
import random
from random import randint as rand

def main():

    for number in range(1,4):
        out_file = open('data' + str(number) + '.csv', 'w')
        writer(out_file)

def writer(out_file):
    teams = []
    for number in range(1,2):
        for number in range(1,50):
            teams.append([str(number)])
        for number in range(1,50):
            teams.append([str(number)])
    #print teams
    for item in teams:
        #print item, '\n'
        item.append(rand(1,100))
        for number in range(1,11):
            item.append(rand(1,10))
        item.append(random.choice('yn'))

    #print teams

    data = csv.writer(out_file, delimiter=',')

    for item in teams:
        data.writerow(item)


if __name__ == "__main__":
    sys.exit(main())
