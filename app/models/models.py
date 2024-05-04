import os
import sqlite3
import re

# from urllib.parse import urljoin
import requests
import fitz
import io

from .tf_idf import calc_tf_idf

cwd = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(cwd, "../../database/search.db")
MARGIN = 120


# Reference: https://stackoverflow.com/questions/67558627/problem-while-joining-two-url-components-with-urllib
# urljoinは使わない方が良い。スラッシュありなしで結果が異なるため。
def joinurl(baseurl, path):
    return "/".join([baseurl.rstrip("/"), path.lstrip("/")])


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
            "SELECT base_url, homepage_url, org, doc, doc_url FROM sources"
        ).fetchall()
    return to_dict_list(
        sources, columns=["base_url", "homepage_url", "org", "doc", "doc_url"]
    )


def select_texts(base_url, keywords):
    keywords = [e.strip() for e in keywords.split(",")]

    pattern = "|".join(keywords)

    keywords_ = [f'texts.text LIKE "%{e}%"' for e in keywords]
    conditions = " OR ".join(keywords_)

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        if base_url is None:
            texts = cur.execute(
                f"SELECT texts.link_id, links.title, texts.page, texts.text FROM texts INNER JOIN links ON texts.link_id = links.id WHERE ({conditions})"
            ).fetchall()
        else:
            texts = cur.execute(
                f'SELECT texts.link_id, links.title, texts.page, texts.text FROM texts INNER JOIN links ON texts.link_id = links.id WHERE links.base_url="{base_url}" AND ({conditions})'
            ).fetchall()

    texts_ = []
    for text in texts:
        # link_id = text[0]
        # title = text[1]
        # page = text[2]
        original_text = text[3]
        len_original_text = len(original_text)

        spans = {}
        first_start = len(original_text)
        last_end = 0

        for m in re.finditer(pattern, original_text, re.IGNORECASE):
            keyword = m.group(0)
            if keyword not in spans:
                spans[keyword] = []

            start = m.start()
            end = m.end()
            spans[keyword].append([start, end])

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

        text_ = list(text)
        text_[3] = original_text
        text_.append(spans)
        texts_.append(text_)

    return to_dict_list(texts_, columns=["link_id", "title", "page", "text", "spans"])


def select_texts_sorted(base_url, keywords):
    keywords = [e.strip() for e in keywords.split(",")]
    keywords_ = [f'texts.text LIKE "%{e}%"' for e in keywords]
    conditions = " OR ".join(keywords_)

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        if base_url is None:
            texts = cur.execute(
                f"SELECT texts.link_id, links.title, texts.page, texts.text FROM texts INNER JOIN links ON texts.link_id = links.id WHERE ({conditions})"
            ).fetchall()
        else:
            texts = cur.execute(
                f'SELECT texts.link_id, links.title, texts.page, texts.text FROM texts INNER JOIN links ON texts.link_id = links.id WHERE links.base_url="{base_url}" AND ({conditions})'
            ).fetchall()

    original_texts = [e[3] for e in texts]
    sorted = calc_tf_idf(keywords, original_texts)

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
        link_id = texts[idx][0]
        title = texts[idx][1]
        page = texts[idx][2]

        texts_.append([link_id, title, page, original_text, spans])

        print(texts_)
    return to_dict_list(texts_, columns=["link_id", "title", "page", "text", "spans"])


def pdf_highlight(link_id, page, keywords, all_pages):
    keywords = [e.strip() for e in keywords.split(",")]

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        base_url, path, title = cur.execute(
            f"SELECT base_url, path, title FROM links WHERE id={link_id}"
        ).fetchone()

    url = joinurl(base_url, path)
    # print(url)
    resp = requests.get(url)
    doc = fitz.open(stream=resp.content)

    pdf = None

    if all_pages == "true":
        for page in doc:
            for keyword in keywords:
                rects = page.search_for(keyword)
            page.add_highlight_annot(rects)

        pdf = io.BytesIO(doc.tobytes())

    else:
        from_page = page - 1 if page > 0 else page
        to_page = page + 1 if page < len(doc) else page
        pages = doc[from_page : to_page + 1]

        for page in pages:
            for keyword in keywords:
                rects = page.search_for(keyword)
            page.add_highlight_annot(rects)

        doc2 = fitz.open()
        doc2.insert_pdf(doc, from_page=from_page, to_page=to_page, start_at=0)

        pdf = io.BytesIO(doc2.tobytes())

    return (title, pdf)


if __name__ == "__main__":
    print(
        select_texts_sorted("https://www.meti.go.jp", "ニュージーランド,オーストラリア")
    )
