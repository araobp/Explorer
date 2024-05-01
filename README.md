# PDF Search

## 背景

私の[マーテック自習レポジトリ](https://github.com/araobp/Learning-MarTech)よりスピンアウト。社外情報収集ツールとしてPDF検索を開発。

## ゴール

- 団体や企業が公開するPDF資料（白書やIR資料など）をキーワードで検索し、ヒットしたページをキーワードハイライトしながら表示する。まずは、日本の各省庁が公開する白書。
- キーワードのランキングを生成する：Betweenness, TF-IDFなど
- ナレッジグラフを作成する

## アーキテクチャー

[アーキテクチャー図](https://docs.google.com/presentation/d/e/2PACX-1vSTcAQs16wdLKj2Ndpa6pm0MrJLDI1DcmLM6ZNvANhVn1qFPvWvD1FXRj9WBLG1m1_55C8bX7csbp_f/pub?start=false&loop=false&delayms=3000)

## 部品/フレームワーク

- Jupyter Notebook, PyMuPDF, spaCy
- SQLite
- Flask
- HTML5, Bootstrap
