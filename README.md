# PDF Search

## 背景

2024/05/01にプロジェクト開始。

私の[マーテック自習レポジトリ](https://github.com/araobp/Learning-MarTech)よりスピンアウト。社外情報収集ツールとしてPDF検索を開発。私の趣味として開発するが、仕事でも使えるかもしれない。

これまでカスタムメイド検索エンジンをいくつか作ってみたが、特定の分野に絞った検索エンジンは性能が良いので気に入っている。そこで、ネットに公開されるPDF資料検索を作ってみたくなった。

## ゴール

- 団体や企業が公開するPDF資料（白書やIR資料など）をキーワードで検索し、ヒットしたページをキーワードハイライトしながら表示する。まずは、日本の各省庁が公開する白書から始める。
- キーワードのランキングを生成する：Betweenness, TF-IDFなど
- ナレッジグラフを作成する

## アーキテクチャー

現在の企業ではファイル共有SaaSが普及している。これらSaaSが提供するユーザ管理に乗り、ローカルPC上でクライアント・サーバーアキテクチャーのアプリを動作させる場合、アーキテクチャーがシンプルになる。

データベースのファイルだけをファイル共有SaaSで共有し、クライアント・サーバ部分はローカルPC上で動作させる。こういうアーキテクチャーのアプリをPythonのPyInstallerでEXEに固めて、職場の同僚へ配布すれば良い。

Electronに似た構造だが、データサイエンスの世界ではJupyter Notebookが多様されるので、FlaskをベースとしたAPIサーバ開発した方が、コード再利用出来て良い。

SQLiteをデータベースとして採用する。SQLiteはPandasと相性が良い、ローカルPC上で動作可能で性能も高い。

MA/SFA/CRMなどのSaaSは、他のユーザとリソース共有する手前、性能が低い場合が多い。実は、ローカルPCこそ、最高の性能を発揮出来る。部署外へ公開しないデータの場合、SaaSでなく、ローカルPC上のクライアント・サーバーの方が、性能や秘密管理の点で優位。

[アーキテクチャー図](https://docs.google.com/presentation/d/e/2PACX-1vSTcAQs16wdLKj2Ndpa6pm0MrJLDI1DcmLM6ZNvANhVn1qFPvWvD1FXRj9WBLG1m1_55C8bX7csbp_f/pub?start=false&loop=false&delayms=3000)

## 部品/フレームワーク

- Jupyter Notebook, PyMuPDF, spaCy
- SQLite
- Flask
- HTML5, Bootstrap
