import spacy
import ocr2dic
import json
from GFQG_1 import is_stop

nlp = spacy.load('en_core_web_sm')
# to speed up process I need only lemmas of the word count task, so i disable other parts of pipeline
nlp_light = spacy.load('en', disable=['ner'])


def video_lecture_preproc(video_id):
    video_number = video_id
    dict_ocr = ocr2dic.ocr2dict('../data/GEOL1330Fall18_Jinny/v' + str(video_number) + '/img_txt/Modi_all_'
                                + str(video_number) + '.csv', '../data/GEOL1330Fall18_Jinny/v'
                                + str(video_number) + '/v' + str(video_number) + '_segments.csv')
    folder = '../data/GEOL1330Fall18_Jinny/v' + str(video_number) + '/'
    f_name = 'v' + str(video_id) + '.json'
    list_dic = []
    for seg in dict_ocr:
        v_seg = seg
        segment = dict_ocr[seg]
        segment_text = []
        for frame, region_id in segment.items():
            for region, region_text in region_id.items():
                segment_text = segment_text + region_text[0]
        doc = nlp(' '.join(segment_text))
        video_words = set()
        for token in doc:
            if not is_stop(token.text) and not token.is_punct and token.tag_ in ['NN', 'NNS', 'NNP', 'NNPS']:
                video_words.add(token.lemma_.lower())
        dic = {"id": int(seg), "text": ','.join(video_words)}
        list_dic.append(json.dumps(dic))
    with open(folder + f_name, 'w') as f:
        for l in list_dic:
            f.write(l+'\n')


if __name__ == '__main__':
    video_lecture_preproc(4623)
