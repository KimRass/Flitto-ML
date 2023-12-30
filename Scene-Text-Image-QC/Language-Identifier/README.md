# Overview
- Target languages (31)
    - ar, cs, da, de, el, en, es, fi, fr, he, hi, hu, id, it, ja, ko, mn, ms, nl, pl, pt, ru, sv, sw, th, tl, tr, uk, vi, zh-cn, zh-tw
    - 이유:

# Dataset
- Dataset size: train set 2,480,000, validation set 310,000, and test set 310,000
## Data Augmentation

# Model
- Base model: 'xlm-roberta-base'

# Training
- Loss function: Cross-entropy
- Maximum sequence length: 512
    - 배치 내 최대 sequence length에 맞춰 padding

# Serving
- Pytorch lightning으로 변환

# Future Improvements
- python으로 작성된 transformer 모델을 c++로 변환/quantization —> 경량화/속도 개선

# References
- https://huggingface.co/docs/transformers/model_doc/xlm-roberta#transformers.XLMRobertaForSequenceClassification
