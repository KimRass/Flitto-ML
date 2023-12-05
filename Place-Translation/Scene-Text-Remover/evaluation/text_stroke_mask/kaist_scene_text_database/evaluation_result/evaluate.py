import pandas as pd

df = pd.read_csv("/Users/jongbeomkim/Desktop/workspace/scene_text_remover/evaluation/text_stroke_mask/kaist_scene_text_database/evaluation_result/evaluation_result.csv")
df.mean(axis=0)
