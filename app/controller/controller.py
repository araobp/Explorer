import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from flask import Blueprint, render_template, jsonify, request, send_file
from models import models

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
    base_url = request.args.get("base_url", default=None, type=str)
    keywords = request.args.get("keywords", default=None, type=str)
    tf_idf = request.args.get("tf_idf", default="true", type=str)

    if tf_idf == "true":
        return jsonify(models.select_texts_sorted(base_url, keywords))
    else:
        return jsonify(models.select_texts(base_url, keywords))


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
