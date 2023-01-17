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
4. Text rendering
    - 번역된 텍스트를 Bounding box의 좌표를 활용해 메뉴 이미지 위에 입힙니다.

# Process of Text Removal
## Original Image
- <img src="https://i.imgur.com/PBIWNHF.png" alt="2436_original" width="600">
## Bounding Box Annotation
- <img src="https://i.imgur.com/3xCYIxL.png" alt="2436_bboxes" width="600">
## Text Detection
- <img src="https://i.imgur.com/wzR5SQL.png" alt="2436_text_score_map" width="600">
- 'CRAFT' ([Character Region Awareness for Text Detection](https://arxiv.org/abs/1904.01941))를 사용하여 Text score map을 생성합니다. 빨간색은 1에 가까운 값을, 파란색은 0에 가까운 값을 나타냅니다. (이해를 돕기 위해 그 위에 원본 이미지를 함께 배치했습니다.)
## Text Mask
- <img src="https://i.imgur.com/6HdG56P.png" alt="2436_text_mask" width="600">
- Text score map에 대해 Image thresholding을 수행하여 Text mask를 생성합니다. Text mask를 벗어난 텍스트도 존재하며, 반대로 텍스트가 아닌 영역이 Text mask에 포함되는 경우도 존재합니다.
- 따라서 최대한 정확하게 텍스트만을 포함하는 Text stroke mask가 필요합니다.
## Pseudo Character Centers (PCCs) 
- <img src="https://i.imgur.com/oDCohO7.png" alt="2436_pccs" width="600">
- CRAFT를 통해 생성된 Text score map을 사용해 각 문자의 중심 좌표를 추출합니다.
## Text Segmentation Map
- <img src="https://i.imgur.com/s5saciM.png" alt="2436_text_segmentation_map" width="600">
- Local maxima에 대해 Watershed를 적용하여 각 문자를 서로 다른 Class로 구분하는 Text segmentation map을 생성합니다. (위 이미지는 이해를 돕기 위해 5개의 Class만으로 단순화했습니다.)
## Image Adaptive Thresholding
- <img src="https://i.imgur.com/DKOnTWq.png" alt="2436_adaptive_thresholded" width="600">
- 이미지에 대해 Adaptive thresholding을 수행합니다.
## Image Segmentation Map
- <img src="https://i.imgur.com/KTR6pq1.png" alt="2436_image_segmentation_map" width="600">
- Adaptive thresholding 수행 후 Connected component labeling을 통해 Image segmentation map을 생성합니다. (위 이미지는 이해를 돕기 위해 5개의 Class만으로 단순화했습니다.)
## Text Stroke Mask
- <img src="https://i.imgur.com/6y0iUzP.png" alt="2436_text_stroke_mask1" width="600">
- Image segmentation map의 각 Label이 Text segmantation map의 0이 아닌 Label과 얼마나 Overlap이 발생하는지 Pixel counts를 통해 계산합니다. 특정한 값 이상의 Overlap이 발생하는 Image segmentation map의 Labels에 대해 Text stroke mask를 생성합니다.
- 이떄 Text stroke mask는 제거해야 하는 텍스트와 제거하지 말아야 하는 텍스트 각각에 대해 따로 생성합니다.
## Text Stroke Mask Thickening
- <img src="https://i.imgur.com/x1kSWFi.png" alt="2436_thickening" width="600">
- Text stroke mask가 텍스트를 완전히 덮지 못하면 텍스트는 깔끔하게 제거되지 않습니다. 이를 방지하기 위해 Thickening을 적절히 수행합니다.
## Image Inpainting
- <img src="https://i.imgur.com/V9FbGtR.png" alt="2436_image_inpainting" width="600">
- 'LaMa' ([Resolution-robust Large Mask Inpainting with Fourier Convolutions](https://arxiv.org/abs/2109.07161))와 Text stroke mask를 사용해 Image inpainting을 수행합니다.
- 이때 제거해야 하는 텍스트와 제거하지 말아야 하는 텍스트 모두에 대해 Text removal을 수행한 후 제거하지 말아야 하는 텍스트는 다시 입힙니다.

# Research
# Comparison with Competitors
- <img src="https://i.imgur.com/XyeWfQq.jpg" alt="2436_others" width="600">
- <img src="https://i.imgur.com/r3TCETc.jpg" alt="1360_others" width="600">
- <img src="https://i.imgur.com/TN7uwaJ.jpg" alt="1360_ours" width="600">
## Using Bounding Boxes as a Mask in Image Inpainting
- 제거하지 말아야 할 텍스트를 일부 제거하거나 자연스럽게 Texture를 살리지 못합니다.
    - <img src="https://i.imgur.com/GfnExpj_d.webp?maxwidth=760&fidelity=grand" alt="646_1" width="300">
    - <img src="https://i.imgur.com/2nMPnO1_d.webp?maxwidth=760&fidelity=grand" alt="646_2" width="300">
    - <img src="https://i.imgur.com/4DeWz3L_d.webp?maxwidth=760&fidelity=grand" alt="679_1" width="300">
    - <img src="https://i.imgur.com/2XjZyqR_d.webp?maxwidth=760&fidelity=grand" alt="679_2" width="300">

# Future Improvements
## Text Stroke Mask Generation using Fully Connected Conditional Random Fields (FC CRFs)
- <img src="https://i.imgur.com/01plHM4.png" alt="ajime_fccrf" width="600">
## Text Stroke Mask Generation by Deep Learning-based Approach
- Scene text removal을 주제로 한 최신 논문들에서 Deep learning을 사용한 Text stroke mask generation을 수행하는 것을 볼 수 있습니다.
    - [Don’t Forget Me: Accurate Background Recovery for Text Removal via Modeling Local-Global Context](https://www.ecva.net/papers/eccv_2022/papers_ECCV/papers/136880406.pdf)
    - [Erasing Scene Text with Weak Supervision](https://openaccess.thecvf.com/content_WACV_2020/papers/Zdenek_Erasing_Scene_Text_with_Weak_Supervision_WACV_2020_paper.pdf)
    - [Stroke-Based Scene Text Erasing Using Synthetic Data for Training](https://arxiv.org/pdf/2104.11493v3.pdf)
    - [Scene text removal via cascaded text stroke detection and erasing](https://arxiv.org/pdf/2011.09768.pdf)