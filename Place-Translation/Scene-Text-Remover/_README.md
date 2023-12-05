# What Is 'Menu Translation' ('메뉴 번역')
- 음식점의 메뉴 이미지를 다국어로 번역해 QR 코드로서 제공하는 서비스입니다.

# Overall Process of Menu Translation
1. Bounding box annotation
    - 수작업으로 적절한 의미 단위의 Bounding box annotation을 수행합니다. 적절한 의미 단위란 예를 들어 "닭만두곰탕 (공기밥 별도)"를 각각 "닭만두곰탕"과 "(공기밥 별도)"로 나누는 것을 말합니다.
    - 이때 가게 이름 또는 가격에 해당하는 텍스트와, 한국어 메뉴를 예로 들면 한국어 외의 텍스트는 대상으로 하지 않습니다.
2. ***Scene text removal***
    - 원본 이미지에서 글자를 지웁니다.
    - 이 레포지토리는 바로 이 단계에 대해서 설명합니다.
3. Transcription
    - 원본 메뉴 이미지에서 각 Bounding box별로 텍스트를 옮겨 적습니다.
4. Translation
    - Machine translation을 수행한 후 올바르게 번역이 됐는지 사람이 검수합니다.
5. Text rendering
    - 텍스트가 지워진 메뉴 이미지 위에 번역된 텍스트를 렌더링합니다.

# Process of Scene Text Removal
- [1]에서 제시한 방법론을 따라갑니다.
## Original Image
- Original image
    - <img src="https://i.imgur.com/PBIWNHF.png" alt="2436_original" width="600">
## 1. Bounding Box Annotation
- Human-annotated bounding boxes
    - <img src="https://i.imgur.com/TVD2dIq.png" alt="2436_bboxes" width="600">
- 빨간색, 파란색, 초록색 간의 차이는 없으며 눈에 가장 잘 띄는 색상으로 표현했습니다.
## 2. Text Detection
- Region score map
    - <img src="https://i.imgur.com/N2zFzGN.png" alt="2436_region_score_map" width="600">
- 'CRAFT' ([Character Region Awareness for Text Detection](https://arxiv.org/abs/1904.01941))를 사용하여 Region score map을 생성합니다. 빨간색은 Score가 1에 가까운 값을, 파란색은 0에 가까운 값을 나타냅니다. 이해를 돕기 위해 그 위에 원본 이미지를 함께 배치했습니다.
## 3. Text Stroke Extraction
- Rule-based approach와 Learning-based approach로 나눌 수 있습니다.
### Rule-based Approach
#### 1) Region Mask Generation
- Region mask
    - <img src="https://i.imgur.com/H9lao9t.png" alt="2436_region_mask" width="600">
- Region score map을 사용해 Region mask를 생성합니다.
#### 2) Image Segmentation Map Generation
- Image segmentation map
    - <img src="https://i.imgur.com/ujrxsrk.png" alt="2436_image_segmentation_map" width="600">
- Adaptive thresholding과 Connected component labeling을 통해 Image segmentation map을 생성합니다. (위 이미지는 이해를 돕기 위해 26개의 Class만으로 단순화했습니다.)
#### 3) Text Stroke Mask Generation
- Text stroke mask
    - <img src="https://i.imgur.com/EgarFnX.png" alt="2436_text_stroke_mask" width="600">
- Image segmentation map의 각 Label이 Region mask와 얼마나 Overlap이 발생하는지 Pixel counts를 통해 계산합니다. 특정한 값 이상의 Overlap이 발생하는 Image segmentation map의 Labels를 가지고 Text stroke mask를 생성합니다.
#### 4) Text Stroke Mask Refinement Using Fully Connected Conditional Random Fields (FC CRFs)
- FC CRFs을 통해 Text stroke mask를 보정합니다.
### Learning-based Approach
#### 1) Image Splitting
- Image patches
    - <img src="https://i.imgur.com/mQr42x9.png" alt="2436_image_patches" width="600">
- 적당한 단위로 이미지를 분할합니다.
#### 2) Text Stroke Mask Prediction
- Text stroke mask
    - <img src="https://i.imgur.com/mRQSLzW.png" alt="2436_lbtsm" width="600">
- 분할된 이미지들을 가지고 Text stroke mask를 생성하고 이들을 다시 합칩니다.
#### 3) Region Mask Generation
- Region mask
    - <img src="https://i.imgur.com/HpEVvJu.png" alt="2436_region_mask_fccrf" width="600">
#### 4) Running Fully Connected Conditional Random Fields (FC CRFs)
- Result of FC CRFs
    - <img src="https://i.imgur.com/J58rZEe.png" alt="2436_fccrf_result" width="600">
- 앞서 생성한 Region mask를 사용해 FC CRFs를 통해 Text stroke mask를 보정합니다.
#### 5) Final Text Stroke Mask
- Final text stroke mask (Text stroke mask + Result of FC CRFs)
    - <img src="https://i.imgur.com/2TgCExG.png" alt="2436_final_mask" width="600">
## 4. Text Stroke Mask Postprocessing
### (1) Text Stroke Mask Thickening
- Text stroke mask가 텍스트를 완전히 덮지 못하면 텍스트는 깔끔하게 제거되지 않습니다. 적절히 Image thickening을 적용해 Text stroke mask가 텍스트를 충분히 덮을 수 있도록 처리합니다.
### (2) Applying Watershed
- Region segmentation map
    - <img src="https://i.imgur.com/3m2TOkK.png" alt="2436_region_segmentation_map" width="600">
- Text stroke mask에 Watershed를 적용해 각 문자를 서로 다른 Class로 구분하는 Region segmentation map을 생성합니다. (위 이미지는 이해를 돕기 위해 26개의 Class만으로 단순화했습니다.)
### (3) Pseudo Character Centers (PCCs) Extraction
- PCCs
    - <img src="https://i.imgur.com/8ZC9zD4.png" alt="2436_pccs" width="600">
- Region score map을 사용해 각 문자의 중심 좌표를 추출합니다.
### (4) Text Stroke Mask Spltting
- Postprocessed text stroke mask for texts to be removed
    - <img src="https://i.imgur.com/3L5lQT1.png" alt="2436_mask1" width="600">
- Postprocessed text stroke mask for texts not to be removed
    - <img src="https://i.imgur.com/mvNOGF3.png" alt="2436_mask2" width="600">
    - text segemntation map과 PCCs를 사용해 Text stroke mask를 둘로 분할하여 제거해야 하는 텍스트와 제거하지 말아야 하는 텍스트 대해 각각 mask를 생성합니다.
## 5. Image Inpainting
- Inpainted image
    - <img src="https://i.imgur.com/V9FbGtR.png" alt="2436_image_inpainting" width="600">
- 'LaMa' ([Resolution-robust Large Mask Inpainting with Fourier Convolutions](https://arxiv.org/abs/2109.07161))와 Text stroke mask를 사용해 Image inpainting을 수행합니다.
- 이때 제거해야 하는 텍스트와 제거하지 말아야 하는 텍스트 모두에 대해 Text removal을 수행한 후 제거하지 말아야 하는 텍스트는 다시 입힙니다.

# Research
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

# Evaluation
<!-- ## Text Detectability
- Requirements:
    - 해상도와 무관하게 평가가 이루어져야 합니다.
    - 하나의 이미지에서 많은 텍스트를 지울수록 높게 평가되어야 합니다.
- Emplementation
    - Region score map from original image | Region score map from text-removed image
        - <img src="https://i.imgur.com/MN9nz7i.jpg" width="800">
    - 텍스트를 완전하게 제거했음에도 불구하고 기존에 텍스트가 존재하지 않았던 영역에 대해서 쌩뚱맞게 Text detection을 해 버리고 말았습니다.
    - Masked region score map from original image | Masked region score map from text-removed image
        - <img src="https://i.imgur.com/9FKM5Nq.jpg" width="800">
    - 기존에 텍스트가 존재했던 영역에 대한 마스크를 생성하여 Scene text removal 전후 각각의 Region score map을 마스킹합니다. 이로써 새롭게 불필요하게 탐지된 텍스트를 평가 대상에서 제외할 수 있습니다.
    - Scene text removal 전후 각각의 Region score map에 대해서 모든 픽셀에 대한 Region score의 합의 비율을 구하고 이를 1에서 빼 값으로 평가합니다. -1에서 1 사이의 값을 가지며 높을수록 텍스트를 완전하게 제거한 것입니다. -->

# References:
- [1] [Erasing Scene Text with Weak Supervision](https://openaccess.thecvf.com/content_WACV_2020/papers/Zdenek_Erasing_Scene_Text_with_Weak_Supervision_WACV_2020_paper.pdf)
