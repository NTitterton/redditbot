import numpy as np, scipy as sp
import pickle

data = open("glove.42B.300d.txt", "r")
datamatrix = []
datamap = {}

i = 0
for line in data:
	line_split = line.split()
	datamatrix.append(line_split[1:])
	datamap[line_split[0]] = (i, sum([float(elem) * float(elem) for elem in datamatrix[i]]))
	i += 1
	if i % 100000 == 0:
		print(str(i) + " words processed.")
print(str(len(datamatrix)) + " total words prcoessed.")
data.close()
print("creating tree...")
tree = sp.spatial.KDTree(datamatrix)
print("writing to pickle...")
new = open("KDTree", 'w+')
pickle.dump(tree, new)
new = open("word_to_loc", 'w+')
pickle.dump(datamap, new)

