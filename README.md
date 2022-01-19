# misrc_distributed_computing_assist_remote_side

外部計算機資源利用ワークフローの内、WebAPI形式で使用するための遠隔側スクリプト

### 分散環境資源計算機側
分散環境資源計算機側はポーリングプログラム（mi-system-remote.py）をデーモンとして動作させる。あらかじめ実行可能なソルバーを決めておき、それを実行するスクリプトをインストールしておく。

* 使い方
  ```
  cd <当ディレクトリ>
  python3.6 mi-system-remote.py <識別名> <APIサーバーホスト名> <token>
  ```
* テスト実行の例(識別子がnims-devな場合)
  ```
  $ python3.6 mi-system-remote.py nims-dev https://nims.mintsys.jp <token>
  site id = nims-dev
  base url = https://nims.mintsys.jp:50443
   token = <token>の表示
  2021/07/13 13:02:21:send request https://nims.mintsys.jp:50443/mi-distcomp-api/calc-request?site_id=nims-dev
  code = 401 / message = There is no information about the your site id(nims-dev)
  ```
### 
## 参考文献
### FlaskのAPI利用法
本APIはpythonのFlaskパッケージを使用しています。このパッケージを使用したAPIの実装のための参考文献
* [さくらのレンタルサーバーでFlaskを利用した住所検索APIを構築してみました](https://day-journal.com/memo/try-019/)
* [Flaskを使ってAPIサーバーを公開する。](http://rennnosukesann.hatenablog.com/entry/2018/07/21/155401)
* [Flaskのrequest.argsでパラメータ処理について](https://qiita.com/uokada/items/7cc35fbe2f956615259b)

### ログ出力
本APIはsyslog機能を使用するのでその参考文献
* [pythonでのsyslogの使い方](https://qiita.com/Esfahan/items/7888914dca0e8d23eac3)
* [Python:mod_wsgiのログをrsyslogとlogrotateでローテーションする](https://blog.amedama.jp/entry/2015/09/13/000901)

### base64エンコード
本APIはJSON形式でデータやファイル内容の受け渡しを行うが、そのためにはbase64エンコードが必要である。そのための参考資料を以下に記述する。
* [base64によるエンコードとデコード](python.ambitious-engineer.com/archives/2066)
* [BASE64でファイルのエンコード・デコード](https://algorithm.joho.info/programming/python/base64-encode-decode-py/)

### デバッグ全般
* GUIはwxを使用し、GUIの作成はwxFormBuilderを使用。
* ステータス表示GUIのタイマー実行はwx.Timerを使用。
  + [wxPython wx.Timerを使ってみる](https://bty.sakura.ne.jp/wp/archives/76)
