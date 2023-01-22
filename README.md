# What Is 'Menu Translation' ('메뉴 번역')
- 음식점 운영자가 "메뉴 번역" 애플리케이션을 통해 메뉴판 사진을 찍어 올리면, 이를 다국어로 번역해 QR 코드를 제공하는 서비스입니다.
- 지원 언어: 한국어, 영어, 일본어, 중국어 간체, 중국어 번체, 프랑스어, 스페인어, 아랍어 (총 8개)

# Overall Process of Menu Translation
1. Bounding box annotation
    - 수작업으로 적절한 의미 단위의 Bounding box annotation을 수행합니다. 적절한 의미 단위란 예를 들어 "닭만두곰탕 (공기밥 별도)"를 각각 "닭만두곰탕"과 "(공기밥 별도)"로 나누는 것을 말합니다.
    - 이때 가게 이름 또는 가격에 해당하는 텍스트와, 한국어 메뉴를 예로 들면 한국어 외의 텍스트는 대상으로 하지 않습니다.
2. **Text removal**
    - 포토샵을 사용해 원본 메뉴 이미지에서 글자를 지웁니다.
    - 이 과정을 자동화한 방법론에 대해서 설명할 예정입니다.
3. Transcription
    - 원본 메뉴 이미지에서 각 Bounding box별로 텍스트를 옮겨 적습니다.
4. Translation
    - Machine translation을 수행한 후 올바르게 번역이 됐는지 사람이 검수합니다.
5. Text rendering
    - 번역된 텍스트를 Bounding box의 좌표를 활용해 메뉴 이미지 위에 입힙니다.

# Process of Text Removal
## Original Image
- Original image
    - <img src="https://i.imgur.com/PBIWNHF.png" alt="2436_original" width="600">
## Bounding Box Annotation
- Human-annotated bounding boxes
    - <img src="https://i.imgur.com/TVD2dIq.png" alt="2436_bboxes" width="600">
- 빨간색, 파란색, 초록색 간의 차이는 없으며 눈에 가장 잘 띄는 색상으로 표현했습니다.
## Text Detection
- Text score map
    - <img src="https://i.imgur.com/N2zFzGN.png" alt="2436_text_score_map" width="600">
- 'CRAFT' ([Character Region Awareness for Text Detection](https://arxiv.org/abs/1904.01941))를 사용하여 Text score map을 생성합니다. 빨간색은 1에 가까운 값을, 파란색은 0에 가까운 값을 나타냅니다. (이해를 돕기 위해 그 위에 원본 이미지를 함께 배치했습니다.)
## Text Mask
- Text mask
    - <img src="https://i.imgur.com/H9lao9t.png" alt="2436_text_mask" width="600">
- Text score map에 대해 Image thresholding을 수행하여 Text mask를 생성합니다.
## Pseudo Character Centers (PCCs)
- Pseudo character centers (PCCs)
    - <img src="https://i.imgur.com/8ZC9zD4.png" alt="2436_pccs" width="600">
- CRAFT를 통해 생성된 Text score map을 사용해 각 문자의 중심 좌표를 추출합니다.
## Text Segmentation Map
- Text segmentation map
    - <img src="https://i.imgur.com/3m2TOkK.png" alt="2436_text_segmentation_map" width="600">
- Local maxima에 대해 Watershed를 적용하여 각 문자를 서로 다른 Class로 구분하는 Text segmentation map을 생성합니다. (위 이미지는 이해를 돕기 위해 26개의 Class만으로 단순화했습니다.)
## Image Segmentation Map
- Image segmentation map
    - <img src="https://i.imgur.com/ujrxsrk.png" alt="2436_image_segmentation_map" width="600">
- Adaptive thresholding 수행 후 Connected component labeling을 통해 Image segmentation map을 생성합니다. (위 이미지는 이해를 돕기 위해 26개의 Class만으로 단순화했습니다.)
## Text Stroke Mask
- Text stroke mask
    - <img src="https://i.imgur.com/EgarFnX.png" alt="2436_text_stroke_mask" width="600">
- Image segmentation map의 각 Label이 Text segmantation map의 0이 아닌 Label과 얼마나 Overlap이 발생하는지 Pixel counts를 통해 계산합니다. 특정한 값 이상의 Overlap이 발생하는 Image segmentation map의 Labels에 대해 Text stroke mask를 생성합니다.
## Text Stroke Mask Postprocessing
- Postprocessed text stroke mask for texts to be removed
    - <img src="https://i.imgur.com/3L5lQT1.png" alt="2436_mask1" width="600">
- Postprocessed text stroke mask for texts not to be removed
    - <img src="https://i.imgur.com/mvNOGF3.png" alt="2436_mask2" width="600">
- Text stroke mask가 텍스트를 완전히 덮지 못하면 텍스트는 깔끔하게 제거되지 않습니다. 이를 방지하기 위해 Thickening 등의 전처리를 수행합니다.
- 제거해야 하는 텍스트와 제거하지 말아야 하는 텍스트 대해 각각 Mask를 생성합니다.
## Image Inpainting
- Inpainted image
    - <img src="https://i.imgur.com/V9FbGtR.png" alt="2436_image_inpainting" width="600">
- 'LaMa' ([Resolution-robust Large Mask Inpainting with Fourier Convolutions](https://arxiv.org/abs/2109.07161))와 Text stroke mask를 사용해 Image inpainting을 수행합니다.
- 이때 제거해야 하는 텍스트와 제거하지 말아야 하는 텍스트 모두에 대해 Text removal을 수행한 후 제거하지 말아야 하는 텍스트는 다시 입힙니다.

# Text Stroke Mask Prediction using Deep Learning-based Approach
## Image Splitting
- Image patches
    - <img src="https://i.imgur.com/mQr42x9.png" alt="2436_image_patches" width="600">
## Text Stroke Mask Prediction
- Learning-based text stroke mask
    - <img src="https://i.imgur.com/mRQSLzW.png" alt="2436_lbtsm" width="600">
## Text Mask
- Text mask for FC CRFs
    - <img src="https://i.imgur.com/HpEVvJu.png" alt="2436_text_mask_fccrf" width="600">
## Fully Connected Conditional Random Fields (FC CRFs)
- Result of FC CRFs
    - <img src="https://i.imgur.com/J58rZEe.png" alt="2436_fccrf_result" width="600">
## Final Text Stroke Mask
- Final text stroke mask (Learning-based text stroke mask + Result of FC CRFs)
    - <img src="https://i.imgur.com/2TgCExG.png" alt="2436_final_mask" width="600">

# Research
# Comparison with Competitors
- Competitor's
    - <img src="https://i.imgur.com/Pb8mTfY.png" alt="1360_others" width="600">
- Ours
    - <img src="https://i.imgur.com/TN7uwaJ.jpg" alt="1360_ours" width="600">
## Using Bounding Boxes As a Mask in Image Inpainting
- 제거하지 말아야 할 텍스트를 일부 제거하거나 배경이 되는 도형을 뭉개버리는 경우
    - Failure case
        - <img src="https://i.imgur.com/GfnExpj_d.webp?maxwidth=760&fidelity=grand" alt="646_1" width="300">
    - Success case
        - <img src="https://i.imgur.com/2nMPnO1_d.webp?maxwidth=760&fidelity=grand" alt="646_2" width="300">
- 배경의 Texture를 자연스럽게 살리지 못하는 경우
    - Failure case
        - <img src="https://i.imgur.com/4DeWz3L_d.webp?maxwidth=760&fidelity=grand" alt="679_1" width="300">
    - Success case
        - <img src="https://i.imgur.com/2XjZyqR_d.webp?maxwidth=760&fidelity=grand" alt="679_2" width="300">
