# Author: https://github.com/araobp
# Date: 2024/05/04

import spacy
from spacy.matcher import PhraseMatcher
import math
import re

# nlp = spacy.load("ja_core_news_sm")
nlp = spacy.blank("ja")


class Span:

    def __init__(self, text, start_char, end_char):
        self.text = text
        self.start_char = start_char
        self.end_char = end_char


class RegexMatcher:

    def __init__(self, keywords):
        self.matcher = re.compile(f'{"|".join(keywords)}')

    # as_spans 引数は使わない：spaCyのPhraseMatcherと合わせるため便箋上確保した引数。
    def __call__(self, text, as_spans=True):
        original_text = text
        # print(original_text)
        spans = []
        for m in self.matcher.finditer(original_text):
            keyword = m.group(0)
            span = Span(text=keyword, start_char=m.start(), end_char=m.end())
            spans.append(span)
        return spans


def create_matcher(keywords, name, tokenize=True):
    if tokenize:
        patterns = [nlp(e) for e in keywords]
        matcher = PhraseMatcher(nlp.vocab)
        matcher.add(name, patterns)
        return matcher
    else:
        return RegexMatcher(keywords)


def generate_span_dict(matcher, doc):
    cnt = {}
    span_dict = {}
    matches = matcher(doc, as_spans=True)

    for span in matches:
        if span.text not in cnt:
            cnt[span.text] = 0
        cnt[span.text] += 1
        if span.text not in span_dict:
            span_dict[span.text] = []
        span_dict[span.text].append([span.start_char, span.end_char])

    return (span_dict, cnt)


"""
TF-IDF無しの単純なトークンベースマッチ

出力例

 [[{'勉強': [[3, 5]], '犬': [[14, 15], [38, 39]]}],
 [{'勉強': [[8, 10], [13, 15]]}],
 [{'勉強': [[0, 2]]}],
 [{'犬': [[15, 16]]}]]
"""


def simple_match(keywords, texts, tokenize=True):
    matcher = create_matcher(keywords, "simple match", tokenize)

    result = []
    idx = 0
    if tokenize:
        pipe = nlp.pipe(texts)
    else:
        pipe = texts

    for doc in pipe:
        span_dict, _ = generate_span_dict(matcher, doc)

        if len(span_dict) != 0:
            result.append([0.0, idx, span_dict, texts[idx]])

        idx += 1

    return result


"""
TF-IDF計算関数


出力例

[[0.04109743892168297, 2, {'勉強': [[0, 2]]}, '勉強しない上司は嫌い。'],
 [0.03850817669777474,
  0,
  {'勉強': [[3, 5]], '犬': [[14, 15], [38, 39]]},
  '夕方に勉強していたら、遠くで犬が吠えているのが聞こえた。たぶん、散歩中の他の犬を怖がっているのだろう。'],
 [0.03835760966023745,
  1,
  {'勉強': [[8, 10], [13, 15]]},
  '毎日、通勤時間に勉強する。勉強は自己への投資。'],
 [0.03648143055578659, 3, {'犬': [[15, 16]]}, '駅まで歩いている途中、散歩中の犬が私に向かって吠えた。']]
"""


def calc_tf_idf(keywords, texts, tokenize=True):
    matcher = create_matcher(keywords, "TF-IDF", tokenize)

    def tf(pipe):
        all_tf = []
        all_span = []

        for doc in pipe:

            span_dict, cnt = generate_span_dict(matcher, doc)

            # print(cnt)
            tf = {}
            for k, v in cnt.items():
                tf[k] = v / len(doc)
            all_tf.append(tf)
            all_span.append(span_dict)

        return (all_tf, all_span)

    def idf(all_tf, texts):
        sent_cnt = {}
        for tf in all_tf:
            for k, v in tf.items():
                if k not in sent_cnt:
                    sent_cnt[k] = 0
                if v > 0:
                    sent_cnt[k] += 1

        all_idf = {}
        for k, v in sent_cnt.items():
            all_idf[k] = math.log(len(texts) / v)

        return all_idf

    def tf_idf(all_tf, all_idf):
        all_tf_idf = []

        for tf in all_tf:
            tf_idf = {}
            for k, v in tf.items():
                tf_idf[k] = v * all_idf[k]
            all_tf_idf.append(tf_idf)

        return all_tf_idf

    def sort(all_tf_idf, texts):
        score = []
        idx = 0
        for e in all_tf_idf:
            s = []
            for k, v in e.items():
                s.append(v)
            if len(s) > 0:
                score.append([max(s), idx, all_span[idx], texts[idx]])
            idx += 1

        score.sort(reverse=True)  # sortはinplaceでソート処理する関数

        return score

    if tokenize:
        pipe = nlp.pipe(texts)
    else:
        pipe = texts
    all_tf, all_span = tf(pipe)

    all_idf = idf(all_tf, texts)
    all_tf_idf = tf_idf(all_tf, all_idf)
    sorted_score_desc = sort(all_tf_idf, texts)  # 降順でソートした結果

    return sorted_score_desc
