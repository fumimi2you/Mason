# Mason(石工)

## 概要
* 画像上の、ホールドっぽい場所を検出するよ。
* ボテの上にホールドが乗っかってる場合も、それっぽく区別出来るよ。

---
## 入力概要
* クライミングウォールの画像
    * ホールドに色がある人工壁を想定、自然の石は無理かも。
* 大まかなホールドの輪郭情報
    * ユーザーが適当にホールドを丸で囲んだ感じを想定。
    * ボテの上にホールドが乗っている場合、輪郭の形状が近い方を選出。

## 入力JSON
下記情報を記載したjsonファイルパスをコマンド引数で入力
* imagePath : 入力画像パス
* addContourSeeds[] : 追加したいホールド輪郭の配列
    * [] : 輪郭を構築するxy座標の配列(※)
        * x : 画像上のx座標
        * y : 画像上のy座標
* reductContourSeeds[] : 追加したいホールド輪郭の配列
    * [] : 輪郭を構築するxy座標の配列(※)
        * x : 画像上のx座標
        * y : 画像上のy座標
* fixedContours[] : 既に座標が決定している輪郭
    * [] : 輪郭を構築するxy座標の配列
        * x : 画像上のx座標
        * y : 画像上のy座標
* (※)補足
    * ざっくりでもよいので輪郭情報が入ると精度が高い
    * 最悪、適当なサイズのレクト(長方形の4点)を入力して下さい。

---
## 出力概要
* 検出したホールドの輪郭情報

## 出力JSON
下記情報を記載したjsonファイルを、入力JSONと同じフォルダに、
"入力JSONタイトル"_Mason.json のファイル名で出力
* contours[] : 輪郭の配列
    * [] : 輪郭を構築するxy座標の配列
        * x : 画像上のx座標
        * y : 画像上のy座標

---
## 実行環境、想定精度
* 開発言語 : Python3
    * 依存ライブラリ : opencv ( ver.3.x をインストールして下さい )
* 想定精度 : 下記の条件ならば 1[s] 未満の処理時間で、 9割くらい成功したい。
    * 画像サイズ : FHD
    * ホールドのサイズ : 100^2[pix]程度
    * ホールド間の距離 : 隣接してない。
    * 他 : 壁に木目とかペインティングとかされてない。

---
## コマンド引数
* 必須引数
    1st : 入力JSONのパス
* オプション引数
    2nd : デバッグ画像出力レベル
    * 0 : 出力なし
    * 1 : 最終結果のみ画面出力
    * 2 : 大まかな中間処理結果も含めて画像出力
    * 3 : 細々出力。

---
## エラー処理
ごめん、あんま作ってないけど、多分下記の感じ。
* 検出失敗 : 入力JSONの輪郭とほぼ同じのが、出力JSONに出力される。
* 不正な入力 : 普通に落ちる

---
### © 2019 YamaLab.
