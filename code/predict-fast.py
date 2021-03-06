#!/usr/bin/env python

"""Script to predict contacts, given the 16 input files"""

from localconfig import *
import pickle, sys
import os

if len(sys.argv) != 3:
	print 'Usage: ' + sys.argv[0] + ' <output files>'
	print 'Output files need to come in *order*!'
	print 'That is:'
	print ' HHblits 1e-4 Psicov'
	print ' HHblits 1e-4 plmDCA'
	print '\nWARNING: This script is provided for convenience only. Results may vary!'
	sys.exit(1)


def predict(X, forest):
	probability = []
	for t in range(len(forest)):
		tree = forest[t]
		while len(tree) > 2:
			if X[tree[0][0]] <= tree[0][1]:
				tree = tree[1]
			else:
				tree = tree[2]
		probability.append(tree[1]/float(tree[0] + tree[1]))
	return sum(probability)/len(probability)

files = sys.argv[1:]

selected = set()
contacts = {}
X = []
Y = []
maxres = -1
acceptable = []
for index in range(2):
	contacts[index] = {}
	d = files[index]
	r = []
	if not os.path.exists(d):
		sys.stderr.write(d + ' does not exist!\n')
		sys.exit(1)
	infile = open(d).readlines()
	if len(infile) < 1 and index not in (6, 14):
		sys.stderr.write(d + ' is empty! Performance MAY be affected\n')
	else:
		acceptable.append(index)
	for m in infile:
		if index % 2 == 0:
			x = m.split()
			if len(x) != 5:
				print d + ' has wrong format!'
				sys.exit(1)
			c = 4
		else:
			x = m.split(',')
			if len(x) != 3:
				print d + ' has wrong format!'
				sys.exit(1)
			c = 2
		aa1 = int(x[0])
		aa2 = int(x[1])
		if aa1 > maxres:
			maxres = aa1
		if aa2 > maxres:
			maxres = aa2	
		if abs(aa1 - aa2) < 5:
			continue
		if x[c].find('nan') > -1:
			score = 0
		else:
			score = float(x[c])
		selected.add( (aa1, aa2) )
		contacts[index][(aa1, aa2)] = score

for s in sorted(list(selected)):
	q = []
	for index in range(2):
		try:
			q.append(contacts[index][s])
		except:
			q.append(0)

	if len(q) == 2:
		X.append(q)
		Y.append(s)

forest = pickle.load(open(os.path.dirname(os.path.abspath(sys.argv[0])) + '/extras/hh4-psicovplmdca.dat'))
for l in range(len(Y)):
	(aa1, aa2) = (Y[l][0], Y[l][1])
        print '%d %d %6.4f' % (aa1, aa2, predict(X[l], forest))

try:
    os.remove('banner.tmp')
except OSError:
    pass

