import os
import sqlite3
import requests
import fitz
import io

from .tf_idf import calc_tf_idf, simple_match

cwd = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(cwd, "../../database/search.db")
MARGIN = 120
LIMIT = 20


# Reference: https://stackoverflow.com/questions/67558627/problem-while-joining-two-url-components-with-urllib
# urljoinは使わない方が良い。スラッシュありなしで結果が異なるため。
def joinurl(baseurl, path):
    return "/".join([baseurl.rstrip("/"), path.lstrip("/")])


def split_keywords(keywords):
    return [e.replace("、", ",").strip() for e in keywords.split(",")]


def to_dict_list(list_, columns):
    dict_list = []
    for e in list_:
        d = {}
        i = 0
        for c in columns:
            d[c] = e[i]
            i += 1
        dict_list.append(d)
    return dict_list


def select_sources():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        sources = cur.execute(
            "SELECT source_id, base_url, homepage_url, org, doc, doc_url FROM sources"
        ).fetchall()
    return to_dict_list(
        sources,
        columns=["source_id", "base_url", "homepage_url", "org", "doc", "doc_url"],
    )


def select_texts(source_ids, keywords, and_cond_, tokenize_, tf_idf, limit):

    keywords = split_keywords(keywords)
    keywords_ = [f'(texts.text GLOB "*{e}*")' for e in keywords]
    like_cond = " AND " if and_cond_ else " OR "
    conditions_keywords = like_cond.join(keywords_)

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        if source_ids is None:
            texts = cur.execute(
                f"SELECT links.source_id, texts.link_id, links.title, texts.page, texts.text \
                    FROM texts INNER JOIN links ON texts.link_id = links.link_id \
                        WHERE ({conditions_keywords}) LIMIT {limit}"
            ).fetchall()
        else:
            source_ids = [e.strip() for e in source_ids.split(",")]
            source_ids_ = [f"links.source_id = {int(e)}" for e in source_ids]
            conditions_source_ids = " OR ".join(source_ids_)

            texts = cur.execute(
                f"SELECT links.source_id, texts.link_id, links.title, texts.page, texts.text \
                    FROM texts INNER JOIN links ON texts.link_id = links.link_id \
                        WHERE ({conditions_source_ids}) AND ({conditions_keywords}) LIMIT {limit}"
            ).fetchall()

    original_texts = [e[4] for e in texts]

    if tf_idf:
        sorted = calc_tf_idf(keywords, original_texts, tokenize_)
    else:
        sorted = simple_match(keywords, original_texts, tokenize_)

    texts_ = []

    for doc_data in sorted:
        spans = doc_data[2]
        original_text = doc_data[3]
        len_original_text = len(original_text)

        first_start = len(original_text)
        last_end = 0

        for k, v in spans.items():
            for e in v:
                start = e[0]
                end = e[1]

                # Detect the smallest start and the largest end
                first_start = start if start < first_start else first_start
                last_end = end if end > last_end else last_end

        # Add margins to the text area
        #                 Original text
        #   [          |                  |        ]
        #          first_start        last_end
        #
        first_start = first_start - MARGIN if first_start >= MARGIN else 0
        last_end = (
            last_end + MARGIN
            if last_end <= (len_original_text - MARGIN)
            else len_original_text
        )

        # Cut out the text area from the original one
        original_text = original_text[first_start:last_end]

        # Adjust the spans for the cut out area
        for k, v in spans.items():
            v_ = []
            for e in v:
                v_.append([e[0] - first_start, e[1] - first_start])
            spans[k] = v_

        idx = doc_data[1]
        text_ = texts[idx]

        source_id_ = text_[0]
        link_id = text_[1]
        title = text_[2]
        page = text_[3]

        texts_.append([source_id_, link_id, title, page, original_text, spans])

        # print(texts_)
    return to_dict_list(
        texts_, columns=["source_id", "link_id", "title", "page", "text", "spans"]
    )


# [Caveat] トークン化した検索ではないので、常にtokenize=Falseで検索した場合のハイライトになる。
def pdf_highlight(link_id, page, keywords, all_pages):
    keywords = split_keywords(keywords)

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        base_url, path, title = cur.execute(
            f"SELECT sources.base_url, links.path, links.title FROM links \
                INNER JOIN sources ON sources.source_id = links.source_id \
                WHERE links.link_id={link_id}"
        ).fetchone()

    url = joinurl(base_url, path)
    # print(url)
    resp = requests.get(url)
    doc = fitz.open(stream=resp.content)

    pdf = None

    if all_pages == "true":
        for page in doc:
            rects = []
            for keyword in keywords:
                rects.extend(page.search_for(keyword))
            page.add_highlight_annot(rects)

        pdf = io.BytesIO(doc.tobytes())

    else:
        from_page = page - 1 if page > 0 else page
        to_page = page + 1 if page < len(doc) else page
        pages = doc[from_page : to_page + 1]

        for page in pages:
            rects = []
            for keyword in keywords:
                rects.extend(page.search_for(keyword))
            page.add_highlight_annot(rects)

        doc2 = fitz.open()
        doc2.insert_pdf(doc, from_page=from_page, to_page=to_page, start_at=0)

        pdf = io.BytesIO(doc2.tobytes())

    return (title, pdf)


if __name__ == "__main__":
    print(select_texts("https://www.meti.go.jp", "ニュージーランド,オーストラリア"))
