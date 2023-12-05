import pandas as pd
import numpy as np
import re

pd.options.display.max_columns = 6

tm = pd.read_excel("/Users/jongbeomkim/Desktop/workspace/menu_image_generator/place_tm_20230216_053926.xlsx")
src_lang = "Korean"
trg_lang = "English"
tm = tm[(tm["src_code"] == src_lang) & (tm["dst_code"] == trg_lang)]
tm = tm[["src_content", "dst_content"]]
tm = tm[tm.isna().sum(axis=1) == 0]
tm = tm[(~tm["src_content"].duplicated()) & (~tm["dst_content"].duplicated())]
tm["src_content_len"] = tm["src_content"].str.len()
tm = tm.sort_values(by=["src_content_len", "src_content"], ascending=[False, True])
tm = tm[tm["src_content_len"] != 1]
tm.reset_index(drop=True, inplace=True)
# tm.head()

tm.to_excel("/Users/jongbeomkim/Desktop/workspace/menu_image_generator/target_tm.xlsx", index=False)
tm.to_csv("/Users/jongbeomkim/Desktop/workspace/menu_image_generator/target_tm.csv", index=False)

# trg_text = "와이리의 칠월 식재료는 '자연산 톳, 애호박, 꽈리고추, 수미감자'입니다."
trg_text = "1년 미만의 어린 양 한 마리에서 2%밖에 나오지 않는 최상의 특수 부위 '프렌치렉'과 항공으로 공수한 '생양갈비'와 '생양등심'을 양파이만의 가니쉬로 토마토, 파인애플, 치즈 퐁듀 등과 함께 즐기는 콤보 메뉴"
# trg_text = "혼밥고기추가"
# trg_text = "장어구이추가"
new_trg_text = trg_text
for row in tm.itertuples():
    if row.src_content in new_trg_text:
        row.src_content
        new_trg_text = new_trg_text.replace(row.src_content, row.dst_content)
new_trg_text


lengths = np.array(tm["src_content_len"].tolist())
np.quantile(lengths, 0.99)
tm[tm["src_content_len"] >= 58]
tm[tm["src_content_len"] <= 13]

tm[tm["src_content_len"] <= 8].iloc[: 10]


# from mecab import MeCab
# mecab = MeCab()
# mecab.nouns(trg_text)
# mecab.pos(trg_text)

import esupar
nlp = esupar.load("KoichiYasuoka/roberta-base-korean-morph-upos")
print(nlp(trg_text))
