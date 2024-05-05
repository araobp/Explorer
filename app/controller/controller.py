import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from flask import Blueprint, render_template, jsonify, request, send_file
from models import models

LIMIT = 200  # SQLiteで検索するレコード数上限のデフォルト値

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/sources")
def sources():
    sources = models.select_sources()
    return jsonify(sources)


@main.route("/search")
def search():
    source_ids = request.args.get("source_ids", default=None, type=str)
    keywords = request.args.get("keywords", default=None, type=str)
    and_cond = request.args.get("and", default="true", type=str)
    tf_idf = request.args.get("tf-idf", default="true", type=str)
    limit = request.args.get("limit", default=LIMIT, type=int)

    and_cond_ = True if and_cond == "true" else False
    tf_idf_ = True if tf_idf == "true" else False

    return jsonify(models.select_texts(source_ids, keywords, and_cond_, tf_idf_, limit))


@main.route("/highlight")
def pdf_highlight():
    link_id = request.args.get("link_id", default=None, type=int)
    page = request.args.get("page", default=None, type=int)
    keywords = request.args.get("keywords", default=None, type=str)
    all_pages = request.args.get("all_pages", default="false", type=str)
    title, pdf_data = models.pdf_highlight(link_id, page, keywords, all_pages)
    return send_file(
        pdf_data, mimetype="application/pdf", as_attachment=False, download_name=title
    )
