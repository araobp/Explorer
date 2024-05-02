# PDF Search

PDF検索エンジンの開発、国内各省庁が発行する白書を検索対象にして始めてみたが、情報へのアクセス性がとても良い。なので、気軽に色々と検索してみると、日本が置かれている危機が伝わってくる内容が多く。。。

## 背景

2024/05/01にプロジェクト開始。

私の[マーテック自習レポジトリ](https://github.com/araobp/Learning-MarTech)よりスピンアウト。社外情報収集ツールとしてPDF検索エンジンを開発。私の趣味として開発するが、仕事でも使えるかもしれない。

ここで開発するものは、最終的にはPyInstallerでEXEに固めて会社の同僚などへ配布可能なものとなる。仕事で使う時は、Box上でデータベースやEXEを共有する形になる。また、Box上のPDFファイルも検索対象に加えることができる。

## ゴール

- 団体や企業が公開するPDF資料（白書やIR資料など）をキーワードで検索し、ヒットしたページをキーワードハイライトしながら表示する。まずは、日本の各省庁が公開する白書から始める。
- キーワードのランキングを生成する：Betweenness, TF-IDFなど
- ナレッジグラフを作成する

## アーキテクチャー

[アーキテクチャー図](https://docs.google.com/presentation/d/e/2PACX-1vSTcAQs16wdLKj2Ndpa6pm0MrJLDI1DcmLM6ZNvANhVn1qFPvWvD1FXRj9WBLG1m1_55C8bX7csbp_f/pub?start=false&loop=false&delayms=3000)

## 部品/フレームワーク

- Jupyter Notebook, PyMuPDF, spaCy
- SQLite
- Flask
- HTML5, Bootstrap
