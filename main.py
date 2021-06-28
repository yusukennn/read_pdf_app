import os,sys
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from pathlib import Path

# フォルダ指定の関数
def dirdialog_clicked():
    iDir = os.path.abspath(Path().resolve())
    iDirPath = filedialog.askdirectory(initialdir = iDir)
    entry1.set(iDirPath)

# ファイル指定の関数
def filedialog_clicked():
    fTyp = [("", "*")]
    iFile = os.path.abspath(Path().resolve()) #os.path.dirname(__file__)
    iFilePath = filedialog.askopenfilename(filetype = fTyp, initialdir = iFile)
    entry2.set(iFilePath)

# 実行ボタン押下時の実行関数
def conductMain():
    text = ""

    dirPath = entry1.get()
    filePath = entry2.get()
    if dirPath:
        text += "フォルダパス：" + dirPath + "\n"
        pdf_to_jpg(dirPath)
    if filePath:
        text += "ファイルパス：" + filePath
    if text:
        messagebox.showinfo("info", text)
    else:
        messagebox.showerror("error", "パスの指定がありません。")

def all_processing(image_dir):
    imagePathes = glob.glob("./image_file/*.jpg")
    wakati_txts = []
    for imagePath in imagePathes:
        txt = jpg_to_str(imagePath)
        txt = format_text(txt)
        txt = wakati_text(txt)
        wakati_txts.append(txt)
    full_txt = ' '.join(wakati_txts) #連結おじさん
    make_wordcloud(full_txt)

def pdf_to_jpg(dirPath):# pdfをjpegに変換
    import glob
    from pathlib import Path
    from pdf2image import convert_from_path

    # PDFファイルのパス
    files = glob.glob(dirPath + "/*")
    imageFile = "./image_file"
    if not os.path.exists(imageFile):
        os.makedirs(imageFile)
    for file in files:
        pdf_path = Path(file)
        #outputのファイルパス
        img_path=Path(imageFile)
        #この1文で変換されたjpegファイルが、imageホルダー内に作られます。
        convert_from_path(pdf_path, output_folder=img_path,fmt='jpeg',output_file=pdf_path.stem)


from PIL import Image
import sys
sys.path.append('/path/to/dir')
import pyocr
import pyocr.builders
def jpg_to_str(jpg_path): # jpg画像から文字列を読み取る関数
    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        print("No OCR tool found")
        sys.exit(1)
    tool = tools[0]
    print("Will use tool '%s'" % (tool.get_name()))

    langs = tool.get_available_languages()
    print("Available languages: %s" % ", ".join(langs))

    txt = tool.image_to_string(
        Image.open(jpg_path),
        lang='jpn',
        builder=pyocr.builders.TextBuilder()
    )
    return txt

def format_text(text):# 分かち書きの前処理する関数
    import re
    text=re.sub(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-…]+', "", text)
    text=re.sub(' ', "", text)
    text=re.sub(r'[!-~]', "", text)#半角記号,数字,英字
    text=re.sub(r'[︰-＠]', "", text)#全角記号
    text=re.sub('\n', "", text)#改行文字
#     text=re.sub('\', " ", text)
    text=re.sub(r'[①-⑳]', "", text)
    text=re.sub('【', "", text)
    text=re.sub('】', "", text)
    return text

def wakati_text(text):# 分かち書きする関数
    """
    文書textを分かち書きして、半角スペース区切りの単語文字列に変換する
    Parameters
    ----------
    text: str
        文書
    Returns
    -------
    text_result: str
        分かち書きされた文書
    """
    # 取り出したい品詞
    select_conditions = ['形容詞', '名詞', '動詞']
    # 分かち書きオブジェクト
    tagger = MeCab.Tagger('')
    # Neologdの指定版 最新語に対応する
    # tagger = MeCab.Tagger('-d /usr/lib64/mecab/dic/mecab-ipadic-neologd')
    # 安定するらしい
    tagger.parse('')
    

    # 分けてノードごとにする
    node = tagger.parseToNode(text)
    terms = []

    while node:
        # 単語
        term = node.surface
        # 品詞
        pos = node.feature.split(',')[0]
        # もし品詞が条件と一致してたら
        if pos in select_conditions:
            terms.append(term)
        node = node.next
    # 連結おじさん
    text_result = ' '.join(terms)
    return text_result

def make_wordcloud(text): #wordcloud画像を作成し，ディレクトリに出力する関数
    wordcloud_file = "./wordcloud_file"
    if not os.path.exists(wordcloud_file):
        os.makedirs(wordcloud_file)
    stop_words = [ u'てる', u'いる', u'なる', u'れる', u'する', u'ある', u'こと', u'これ', u'さん', u'して', \
             u'くれる', u'やる', u'くださる', u'そう', u'せる', u'した',  u'思う',  \
             u'それ', u'ここ', u'ちゃん', u'くん', u'', u'て',u'に',u'を',u'は',u'の', u'が', u'と', u'た', u'し', u'で', \
             u'ない', u'も', u'な', u'い', u'か', u'ので', u'よう', u'こと', u'さ', u'れ', u'おり', u'ため', u'おく', u'できる', u'なっ', u' う']
    wordcloud = WordCloud(
                          font_path="/system/Library/Fonts/ヒラギノ角ゴシック W4.ttc",
                          colormap='copper_r',
                          stopwords = set(stop_words),
                          collocations = False,
                          width=800,height=600).generate(text)
    wordcloud.to_file(wordcloud_file)

if __name__ == "__main__":

    # rootの作成
    root = Tk()
    root.title("サンプル")

    # Frame1の作成
    frame1 = ttk.Frame(root, padding=10)
    frame1.grid(row=0, column=1, sticky=E)

    # 「フォルダ参照」ラベルの作成
    IDirLabel = ttk.Label(frame1, text="フォルダ参照＞＞", padding=(5, 2))
    IDirLabel.pack(side=LEFT)

    # 「フォルダ参照」エントリーの作成
    entry1 = StringVar()
    IDirEntry = ttk.Entry(frame1, textvariable=entry1, width=30)
    IDirEntry.pack(side=LEFT)

    # 「フォルダ参照」ボタンの作成
    IDirButton = ttk.Button(frame1, text="参照", command=dirdialog_clicked)
    IDirButton.pack(side=LEFT)

    # Frame2の作成
    frame2 = ttk.Frame(root, padding=10)
    frame2.grid(row=2, column=1, sticky=E)

    # 「ファイル参照」ラベルの作成
    IFileLabel = ttk.Label(frame2, text="ファイル参照＞＞", padding=(5, 2))
    IFileLabel.pack(side=LEFT)

    # 「ファイル参照」エントリーの作成
    entry2 = StringVar()
    IFileEntry = ttk.Entry(frame2, textvariable=entry2, width=30)
    IFileEntry.pack(side=LEFT)

    # 「ファイル参照」ボタンの作成
    IFileButton = ttk.Button(frame2, text="参照", command=filedialog_clicked)
    IFileButton.pack(side=LEFT)

    # Frame3の作成
    frame3 = ttk.Frame(root, padding=10)
    frame3.grid(row=5,column=1,sticky=W)

    # 実行ボタンの設置
    button1 = ttk.Button(frame3, text="実行", command=conductMain)
    button1.pack(fill = "x", padx=30, side = "left")

    # キャンセルボタンの設置
    button2 = ttk.Button(frame3, text=("閉じる"), command=quit)
    button2.pack(fill = "x", padx=30, side = "left")
    

    root.mainloop()