# PDF Search

PDF検索エンジンの開発、国内各省庁が発行する白書を検索対象にして始めてみたが、情報へのアクセス性がとても良い。なので、気軽に色々と検索してみると、日本が置かれている危機が伝わってくる内容が多く。。。

## 背景

2024/05/01にプロジェクト開始。

私の[マーテック自習レポジトリ](https://github.com/araobp/Learning-MarTech)よりスピンアウト。社外情報収集ツールとしてPDF検索エンジンを開発。私の趣味として開発するが、仕事でも使えるかもしれない。

ここで開発するものは、最終的にはPyInstallerでEXEに固めて会社の同僚などへ配布可能なものとなる。仕事で使う時は、Box上でデータベースやEXEを共有する形になる。また、Box上のPDFファイルも検索対象に加えると良い(MS OfficeのファイルもPDF変換して検索対象に加える）。

企業内では、各種汎用サーチエンジンが利用されるが、どれも反応が遅い、ブラウジングに向いていない（ブラウザ画面だけで完結しない）ものが多い。ここでは、快適なブラウジング実現を最優先に開発を進める。マーケティング部門では、多くの情報を、検索対象を特定の範囲へ絞りつつ、広く手早く収集する必要あり、快適なブラウジングの提供が重要。

本当は、Elasticsearchとかneo4jとか導入したいところだが、企業秘密区分、組織上の問題、費用上の問題、スケールの問題、政治的な問題などあり、なかなか、部門個別での導入は容易では無い。ここで開発するような完全無償なものが、それらの代替になれば良い。Boxを導入済みの企業であれば、Boxのユーザ管理やアクセス制御に依存すれば、ここで開発するようなシンプルな検索エンジンで代替え可能と考える。

## ゴール

- 団体や企業が公開するPDF資料（白書やIR資料など）をキーワードで検索し、ヒットしたページをキーワードハイライトしながら表示する。まずは、日本の各省庁が公開する白書から始める。
- キーワードのランキングを生成する：Betweenness, TF-IDFなど
- ナレッジグラフを作成する

## アーキテクチャー

O'Reillyの実践自然言語処理 7.1 情報検索を参考にアーキテクチャーを考えた。

クライアント・サーバーだけど、ローカルPC上でローカルソケットでプロセス間通信するので、実質、スタンドアロンアプリとして動作する。

検索対象となるPDF資料の合計データ量が少ないので、とりあえず、PDF資料からテキストデータをSQLiteへ保存し、SQLiteの検索機能で文章抽出する構成とした。クローラーのみでインデクサーはなし。これでも十分な応答速度が得られる。データ量が増えたら、インでクサーとして、SQLiteのVirtual Table機能活用を考える。

サーチャーに関しては、TD-IDFを適用した順位づけを行いたい（2024/5/3の段階では、まだ未実装）

[アーキテクチャー図](https://docs.google.com/presentation/d/e/2PACX-1vSTcAQs16wdLKj2Ndpa6pm0MrJLDI1DcmLM6ZNvANhVn1qFPvWvD1FXRj9WBLG1m1_55C8bX7csbp_f/pub?start=false&loop=false&delayms=3000)

## 部品/フレームワーク

- Jupyter Notebook, PyMuPDF, spaCy
- SQLite
- Flask
- HTML5, Bootstrap

## コード

現在のインプリは、経産省、総務省、防衛省発行の白書を検査出来る状態。TF-IDFを適用した検索順位づけ機能を追加予定。

- [Crawler.ipynb](Crawler.ipynb) -- 各省庁発行白書のindexページからPDF資料のハイパーリンク抽出する部分、Jupter Notebook上だと開発しやすい。
- [Database](database) -- SQLiteのデータベースファイル。仕事でこのアプリを利用する場合、このファイルをBox上の共有フォルダへ置くと良い。
- [Flaskアプリ](./app) -- 実装が完了したらPyInstallerでEXEに固める予定。そうすると、Box上のフォルダを共有する職場の同僚へ配布しやすくなる。
