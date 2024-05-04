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
    source_id = request.args.get("source_id", default=None, type=str)
    keywords = request.args.get("keywords", default=None, type=str)
    tf_idf = request.args.get("tf-idf", default="true", type=str)
    limit = request.args.get("limit", default=LIMIT, type=int)

    tf_idf_ = False
    if tf_idf == "true":
        tf_idf_ = True

    return jsonify(models.select_texts(source_id, keywords, tf_idf_, limit))


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
