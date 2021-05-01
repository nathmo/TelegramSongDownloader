import numpy as np
import sklearn.cluster
import distance
import matplotlib.pyplot as plt
import numpy
import scipy.cluster.hierarchy as hcluster

text = """
pomme pome pmme poire pire pore arbre abre arbres official [official (official video video] video) ultra (ultra [ultra music music] music) lyrics lyrics) (lyrics [lyrics] (lyrics) (original) hd hd) original audio quality 
"""
words = text.split(" ") #Replace this line
words = np.asarray(words) #So that indexing with a list will work
lev_similarity = -1*np.array([[distance.levenshtein(w1,w2) for w1 in words] for w2 in words])

affprop = sklearn.cluster.AffinityPropagation(affinity="precomputed", damping=0.5)
affprop.fit(lev_similarity)
for cluster_id in np.unique(affprop.labels_):
    exemplar = words[affprop.cluster_centers_indices_[cluster_id]]
    cluster = np.unique(words[np.nonzero(affprop.labels_==cluster_id)])
    cluster_str = ", ".join(cluster)
    print(" - *%s:* %s" % (exemplar, cluster_str))


"""
 - *pome:* pomme, abre, arbres, pire, pmme, poire, pome, pore
 - *official:* (official, (original), [official, official, original
 - *video:* audio, video, video), video]
 - *ultra:* (ultra, [ultra, arbre, quality, ultra
 - *lyrics:* (lyrics, (lyrics), [lyrics], lyrics, lyrics), music, music), music]
 - *hd:* hd, hd)
 
  - *pome:* pomme, abre, arbres, pire, pmme, poire, pome, pore
 - *official:* (official, (original), [official, official, original
 - *video:* audio, video, video), video]
 - *ultra:* (ultra, [ultra, arbre, quality, ultra
 - *lyrics:* (lyrics, (lyrics), [lyrics], lyrics, lyrics), music, music), music]
 - *hd:* hd, hd)
"""


# generate 3 clusters of each around 100 points and one orphan point

data = lev_similarity


# clustering
thresh = 1.5
clusters = hcluster.fclusterdata(data, thresh, criterion="distance")
print(clusters)
# plotting
plt.scatter(*numpy.transpose(data), c=clusters)
plt.axis("equal")
title = "threshold: %f, number of clusters: %d" % (thresh, len(set(clusters)))
plt.title(title)
plt.show()