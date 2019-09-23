import sqlite3
import jieba
import json
import jieba.analyse
import imageio
import pandas as pd
from wordcloud import WordCloud

def tag_count(filename):
    with open(filename) as f:
        fcontent = f.read()
    alpha = 'qwertyuiopasdfghjklzxcvbnm1234567890QWERTYUIOPASDFGHJKLZXCVBNM'
    tags = jieba.analyse.extract_tags(fcontent, topK=200, withWeight=True)
    new_tags = {}
    for k in range(len(tags)):
        uchar = tags[k][0][0]
        if uchar not in alpha:
            new_tags[tags[k][0]] = int(tags[k][1] * 10000)
    return new_tags

def get_data():
    with open('config.json') as c:
        conf = json.loads(c.read())

    sqlite_path = conf['sqlite_path']
    chat_table = conf['chat_table']
    with sqlite3.connect(sqlite_path) as con:
        data = {
            'all': pd.read_sql_query("select * from %s WHERE Type = 1" % chat_table, con),
            'me': pd.read_sql_query("select * from %s WHERE Type = 1 AND Des = 0" % chat_table, con),
            'you': pd.read_sql_query("select * from %s WHERE Type = 1 AND Des = 1" % chat_table, con)
        }

def generate_pic():
    data = get_data()
    image_msk = imageio.imread('Heart.jpg')
    for who, df in data.items():
        txt = df['Message']
        txt_file = '%s.txt' % who
        txt.to_csv(txt_file, header=None, index=False)
        # with open(txt_file) as f:
        #     mytxt = f.read()
        # cut_txt = ' '.join(jieba.cut(mytxt))
        # wc = WordCloud(font_path="SimHei.ttf",mask=image_msk,max_words=200,background_color="white").generate(cut_txt)
        wc = WordCloud(font_path="SimHei.ttf",mask=image_msk,background_color="white").generate_from_frequencies(tag_count(txt_file))
        wc.to_file('%s-white.png' % who)

# export to excel
def export_excel():
    data = get_data()
    writer = pd.ExcelWriter('love.xlsx')
    data['all'].to_excel(writer, 'Sheet1')
    writer.save()

if __name__ == '__main__':
    generate_pic()
