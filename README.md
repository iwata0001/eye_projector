# Name
 
"アニメ調の目をにじさんじっぽく変換ツール + 編集ツール"

描いたラフな目をにじさんじのライバーたちの目を使ってそれらしくするツールと,   
そのベクタ画像を生成して細かく編集するツールです.
 
# DEMO
 
 https://youtu.be/EvTgpndDvmU
 
# Features
かなり適当に描いてもそれらしくなります.  
ベクタ画像からきれいな輪郭をとれます.  
特定のライバーっぽい雰囲気を出せるように、ディティールの転写機能があります. (現在使用不可)
 
# Requirement
 
* tk 8.6.12
* pillow 9.2.0
* numpy 1.23.4
* opencv 4.6.0
* pywavelets 1.3.0 現行の機能には使いません.
* matplotlib 3.5.2
 
# Installation

Anacondaをインストールして仮想環境を作ります.
conda installで上にあげたライブラリをインストールします.
 
# Usage
* calcEigを実行してモデルデータを作ります. 数分ほどかかります.
* eyeProjectorGUI.pyを実行します. guiが開きます.
* modeが0（スライドバーが左）になっていることを確認して, GUI真ん中のキャンバス中央に大きく目をかきます. 
* ペンの太さはthicknessのバーで, 色はカラーボタンから選べます.
* 描き終わったら, modeを1に変更し, 目の指定の位置を順にクリックしていきます.
* 指定順は, (白目上右下左端, 黒目左, 黒目右, 白目右下, 白目左下, まつ毛左上（黒目左の真上くらい）, まつ毛右上（左上と同様）, 黒目右下, 黒目左下, 瞳中央) の13点です.
* 間違えたらclear allでやり直してください.
* 入力ボックスに名前を入れて, 右上のgenerateボタンを押すとそれっぽい目が生成, 表示されます. 画像データはoutputフォルダに保存されます. 
* 左下のほうのスピンボックスで好きな目を選んで, add detailボタンを押すとディティールが転写された画像ができます. (現在使用不可)

* eyeVectorizerGUI.pyを実行します. guiが開きます.
* 右下のスピンボックスの数値を100にしてください. (0(初期状態)からの収束の様子が見れます.)
* Aキーを押して制御点選択しマウスで動かしてベクトル画像を編集できます. 
* 上のtargetという文字の横のスピンボックスで編集対象を選びます. (0: 白目, 1: 黒目, 2: まつ毛)
 
# Note
 
calceig.pyでsavesフォルダに生成されるファイルはファイルサイズが大きいのでコミットするとプッシュできなくなります.  *savesフォルダの中はコミットしないようにしてください*.  
修士論文のための実装です. 
 
# Author
 
* 氏名 岩田草汰
* 所属 北海道大学大学院情報科学院メディアネットワークコース
* E-mail souta314@outlook.jp
 
# License

ライバーの目画像の使用許諾がないのでほかで使うのはだめです.