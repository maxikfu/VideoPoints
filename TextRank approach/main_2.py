from Ranking import text_ranking
from collections import OrderedDict
import json
import os
import pprint


if __name__ == '__main__':
    video_id = 4588
    video_directory = '../data/GEOL1330Fall18_Jinny/v' + str(video_id) + '/'
    os.chdir(video_directory)
    # loading file containing video segment to book segment link
    try:
        with open('v' + str(video_id) + '_2book.json', 'r') as f:
            raw = f.readlines()
    except IOError:
        print("Error: File with video " + str(video_id) + " 2 book links does not exist.")
        exit()
    video_book_link = OrderedDict()
    for line in raw:
        l_j = json.loads(line)
        video_book_link[int(l_j['video_seg'])] = int(l_j['book_seg'])

    # load OCR words for every video segment
    try:
        with open('v' + str(video_id) + '.json', 'r') as f:
            raw = f.readlines()
    except IOError:
        print("Error: File with video " + str(video_id) + " OCR does not exist.")
        exit()
    video_OCR = OrderedDict()
    for line in raw:
        l_j = json.loads(line)
        video_OCR[int(l_j["id"])] = set(l_j["text"].split(','))

    # load book
    try:
        with open('../tt_Earth_cleaned.json', 'r') as f:
            raw_book_segs = f.readlines()
    except IOError:
        print("Error: Text book is not found.")
        exit()

    # perform TextRanking on the book segment to extract most informative sentences and key phrases
    for v_seg_id, book_seg_id in video_book_link.items():
        book_seg_json = json.loads(raw_book_segs[book_seg_id-1])
        sents, key_phrs = text_ranking(v_seg_id, book_seg_json)

        # choose sentence based on words in video segment

        # choose key phrase in this sentence based on key phrases

        # get distractors

