# useful functions
import pandas as pd
import collections as coll
import re
import numpy as np
from nltk import word_tokenize
from nltk.corpus import stopwords
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.metrics.pairwise import euclidean_distances


def load_test_data(file_path):  # returns test data in dictionary
    dic = {}
    df = pd.read_csv(file_path)
    for slide, sentence, region in zip(df['SlideNumber'], df['Sentence'], df['RegionId']):  # loading data from csv
        # to dic
        if slide not in dic:
            dic[slide] = {}
        if region not in dic[slide]:
            dic[slide][region] = []
        dic[slide][region].append(word_tokenize(rm_apostrophe(sentence)))
    return coll.OrderedDict(dic)


def rm_apostrophe(phrase):  # removing apostrophe and punct
    phrase = re.sub(r"\’", "", phrase)
    phrase = re.sub(r"[^0-9a-zA-Z\s]", "", phrase)
    # # specific
    # phrase = re.sub(r"won't", "will not", phrase)
    # phrase = re.sub(r"can\'t", "can not", phrase)
    #
    # # general
    # phrase = re.sub(r"n\'t", " not", phrase)
    # phrase = re.sub(r"\'re", " are", phrase)
    # phrase = re.sub(r"\'s", " is", phrase)
    # phrase = re.sub(r"\'d", " would", phrase)
    # phrase = re.sub(r"\'ll", " will", phrase)
    # phrase = re.sub(r"\'t", " not", phrase)
    # phrase = re.sub(r"\'ve", " have", phrase)
    # phrase = re.sub(r"\'m", " am", phrase)
    return phrase


def load_ocr_output(file_path):  # removing stopwords in this step
    data = pd.read_csv(file_path)
    stop_words = set(stopwords.words('english'))
    #data = data[~data.word.isin(stop_words)]
    return data


def clustering(x_data, y_data, number_of_clusters, link):
    x_y_combined = [[x, y] for x, y in zip(x_data, y_data)]
    clf = AgglomerativeClustering(n_clusters=number_of_clusters, linkage=link).fit(x_y_combined)
    #clf = KMeans(number_of_clusters).fit(x_y_combined)
    return clf.labels_


def ocr_coordinates_pre_processing(data):  # deleting spaces between words
    x_data = data['Left'].tolist()
    y_data = data['Top'].tolist()
    word_id = data['Id'].tolist()
    line_id = data['LineId'].tolist()
    word_length = [r - l for l, r in zip(x_data, data['Right'].tolist())]
    word_length = [0] + word_length[:-1]
    old_line_id = None
    total_length = 0
    for line, id in zip(line_id, word_id):  # new line we don't need to subtract
        if old_line_id != line: # new line
            word_length[word_id.index(id)] = 0
            old_line_id = line
            total_length = 0
        else:
            prev_length = word_length[word_id.index(id)]
            word_length[word_id.index(id)] += total_length
            total_length += prev_length
    x_data = [a-b for a,b in zip(x_data, word_length)]
    # x_y_comb = [[x, y] for x, y in zip(x_data, y_data)]
    return x_data, y_data


def gap_statistic(data, nrefs=30, maxClusters=10):  # TODO: run for different linkage methods and choose best one
    # calculates optimal number of clausters by usig Gap Statistic from Tibshirani, Walther, Hastie
    # Params:
    #   data: ndarry of shape (n_samples, n_features)
    #   nrefs: number of sample reference datasets to create
    #   maxClusters: Maximum number of clusters to test for
    # Returns: (gaps, optimalK)
    gaps = np.zeros((len(range(1, maxClusters)),))
    resultsdf = pd.DataFrame({'clusterCount': [], 'gap': []})
    for gap_index, k in enumerate(range(1, maxClusters)):

        # Holder for reference dispersion results
        refDisps = np.zeros(nrefs)

        # For n references, generate random sample and perform Agglomerative Clustering getting resulting dispersion
        # of each loop
        for i in range(nrefs):
            # Create new random reference set
            length_data = len(data)
            randomReference = np.random.random_sample(size=(length_data, 2))

            # Fit to it
            ac = AgglomerativeClustering(k, linkage='single')
            # ac = KMeans(k)
            ac.fit(randomReference)

            refDisp = dispersion(randomReference, ac.labels_)

            refDisps[i] = refDisp
        # Fit cluster to original data and create dispersion
        ac = AgglomerativeClustering(k, linkage='single')
        #ac = KMeans(k)
        ac.fit(data)

        origDisp = dispersion(data, ac.labels_)
        # Calculate gap statistic
        gap = np.log(np.mean(refDisps)) - np.log(origDisp)

        # Assign this loop's gap statistic to gaps
        gaps[gap_index] = gap

        resultsdf = resultsdf.append({'clusterCount': k, 'gap': gap}, ignore_index=True)

    return (gaps.argmax() + 1,
            resultsdf)  # Plus 1 because index of 0 means 1 cluster is optimal, index 2 = 3 clusters are optimal


def dispersion(data_points, returned_clusters):  # returns Wk, is the pooled within-cluster sum of squares around the cluster means
    # calculaing pairwise euclidean distance for all points for each cluster
    cluster_dict = {}
    number_of_elem_in_clusters = {}
    for point, label in zip(data_points, returned_clusters):
        if label not in cluster_dict:
            cluster_dict[label] = []
        cluster_dict[label].append(point)
    for label in cluster_dict:
        number_of_elem_in_clusters[label] = len(cluster_dict[label])
    for label in cluster_dict:
        cluster_dict[label] = euclidean_distances(cluster_dict[label], cluster_dict[label]).sum()
    wk = 0
    for r in cluster_dict:
        wk += 1/(2*number_of_elem_in_clusters[r])*cluster_dict[r]
    return wk