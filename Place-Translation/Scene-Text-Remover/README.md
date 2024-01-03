- 이미지에서 텍스트를 지우는 모델입니다.

# 1. Process
- [1]에서 제시한 방법론을 참고해 크게 3단계 (Scene text detection → Text stroke mask prediction → Image inpainting)에 걸쳐 작동하도록 개발했습니다.
- Original image
    - <img src="https://i.imgur.com/PBIWNHF.png" width="600">
- Bounding box annotation
    - <img src="https://i.imgur.com/TVD2dIq.png" width="600">
    - (빨간색, 파란색, 초록색 간의 차이는 없으며 눈에 가장 잘 띄는 색상으로 표현했습니다.)
## (1) Scene Text Detection
- Text region score map
    - <img src="https://i.imgur.com/N2zFzGN.png" width="600">
    - (이해를 돕기 위해 그 위에 원본 이미지를 함께 배치했습니다.)
- 'CRAFT' scene text detection model [2]을 사용하여 'text region score map'을 생성합니다. 어떤 픽셀이 빨간색에 가까울수록 모델이 그 픽셀을 텍스트의 중심이라고 확신함을 나타냅니다.
## (2-1) Text Stroke Prediction
- rule-based approach와 learning-based approach로 나눌 수 있습니다.
### 1) Rule-based Approach
- Text region mask generation
    - <img src="https://i.imgur.com/H9lao9t.png" width="600">
- Image segmentation
    - <img src="https://i.imgur.com/ujrxsrk.png" width="600">
    - (매우 많은 수의 label이 생성되지만 이해를 돕기 위해 26개의 색상을 사용하여 단순화했습니다.)
    - adaptive thresholding과 connected component labeling을 통해 image segmentation을 수행합니다.
- Text stroke mask generation
    - <img src="https://i.imgur.com/EgarFnX.png" width="600">
    - image segmentation map의 각 label이 text region mask와 얼마나 겹치는지 픽셀 수를 세어 계산합니다. 특정한 값 이상의 겹침이 발생하는 image segmentation map의 labels를 가지고 text stroke mask를 생성합니다.
- FC CRFs (Fully Connected Conditional Random Fields) [3]
    - text stroke mask를 보정하여 최종 text stroke mask를 생성합니다.
### 2) Learning-based Approach
- Text stroke mask prediction
    - <img src="https://i.imgur.com/mQr42x9.png" width="600">
    - text stroke mask prediction model [4]에 입력하기 위해 각 bounding box에 해당하는 이미지 패치를 1:5 또는 5:1이 비율이 되도록 분할하거나 패딩을 추가합니다.
    - <img src="https://i.imgur.com/mRQSLzW.png" width="600">
    - 각 이미지 패치를 640 × 128로 리사이즈하여 text stroke mask prediction을 수행하고 원본 이미지의 원래의 위치에 삽입합니다.
- Text region mask generation
    - <img src="https://i.imgur.com/HpEVvJu.png" width="600">
    - <img src="https://i.imgur.com/J58rZEe.png" width="600">
    - text region score map으로부터 text region mask를 생성하고 여기에 FC CRFs [3]를 적용합니다.
- Mask merge
    - <img src="https://i.imgur.com/2TgCExG.png" width="600">
    - text stroke mask와 text region mask를 합쳐 최종 text stroke mask를 생성합니다.
## (2-2) Text Stroke Mask Postprocessing
- Dilation (Thickening)
    - Text stroke mask가 텍스트를 완전히 덮지 못하면 텍스트가 깔끔하게 지워지지 않습니다. dilation을 통해 text stroke mask가 텍스트를 충분히 덮을 수 있도록 처리합니다.
- Watershed
    - <img src="https://i.imgur.com/3m2TOkK.png" width="600">
    - (이해를 돕기 위해 26개의 class만으로 단순화했습니다.)
    - text stroke mask에 watershed를 적용해 각 문자를 서로 다른 class로 구분하는 text region segmentation map을 생성합니다.
- Pseudo Character Centers (PCCs) extraction
    - <img src="https://i.imgur.com/8ZC9zD4.png" width="600">
    - text region score map을 사용해 각 문자의 중심 좌표를 추출합니다.
- Text stroke mask split
    - Text stroke mask for texts to be removed ('Removal mask')
    - <img src="https://i.imgur.com/3L5lQT1.png" width="600">
    - Text stroke mask for texts not to be removed ('Revival mask')
    - <img src="https://i.imgur.com/mvNOGF3.png" width="600">
    - Text region segemntation map과 PCCs를 사용해 text stroke mask를 둘로 분할하여 지워야 하는 텍스트와 지우지 말아야 하는 텍스트 대해 각각 mask를 생성합니다.
## (3) Image Inpainting
- <img src="https://i.imgur.com/V9FbGtR.png" width="600">
- 'LaMa' image inpainting model [5]을 사용해 image inpainting을 수행합니다.
- 이때 removal mask와 revival mask를 모두 사용해 텍스트를 지운 후 revival mask를 사용해 지우지 말아야 하는 텍스트를 다시 되살립니다.

# 2. Examples
- <img src="https://github.com/KimRass/Flitto-ML/assets/67457712/4738b594-c869-41f6-bbbb-7cdc83cec6b8" width="800">
- <img src="https://github.com/KimRass/Flitto-ML/assets/67457712/6f295647-c8cb-41c5-bf9a-c0503a840edf" width="300">
- <img src="https://github.com/KimRass/Flitto-ML/assets/67457712/4315e3c7-3c60-4584-80ac-094a194c6b9a" width="400">
- <img src="https://github.com/KimRass/Flitto-ML/assets/67457712/929867bd-14d8-4b74-92e4-7e7c60b66377" width="500">
<!-- ## (1) Success Cases -->
<!-- ## (2) Failure Cases -->

# 3. Evaluation
- On scene text removal task [1] using [7]
    | Approach | PSNR (↑) | SSIM (↑) | MSE (↓) |
    |-|-|-|-|
    | rule-based approach | 34.22 | 0.9686 | 0.0017 |
    | learning-based approach | 32.95 | 0.9536 | 0.0019 |
    - (기존의 evaluation metric은 이미지 내 텍스트 중 일부만을 지우는 use case에는 적합하지 않을 수 있을 것입니다.)

<!-- - Recall of scene text detection result using 'CRAFT' [2] -->

# 4. Research
## (1) Scene Text Detection
- scene text detection 과정이 꼭 필요한가? 즉 bounding box를 그대로 mask로 사용해 image inpainting을 하면 어떻게 되는지 확인해보겠습니다.
- Case 1:
    - <img src="https://github.com/KimRass/Flitto-ML/assets/67457712/f9cbb17c-5787-49e0-bc00-dd02773aa765" width="700">
    - '겨울시즌한정': bounding box가 axis-aligned rectangle이므로 사선으로 렌더링된 텍스트를 깔끔하게 지우지 못했습니다.
    - '한우 육회비빔밥 소반': 타겟 텍스트를 잘 지웠으나 boundig box가 외국어 나란히쓰기 텍스트까지 지워버렸습니다. (외국어 나란히쓰기 텍스트를 지우지 않고자 하는 경우)
    - '일일 20개 한정': bounding box가 원본 이미지에 있던 빨간색 직사각형과 겹침이 발생하여 이를 깔끔하게 지우지 못했습니다.
- Case 2:
    - <img src="https://github.com/KimRass/Flitto-ML/assets/67457712/ac09af87-a635-4c1b-8b6d-591f1ccc171c" width="600">
    - 이미지에서 너무 넓은 영역을 지우고 생성하려고 하면서 질감을 자연스럽게 살리지 못했습니다.

# 5. References
- [1] [Erasing Scene Text with Weak Supervision](https://github.com/KimRass/Place-Translation/blob/main/papers/erasing_scene_text_with_weak_supervision.pdf)
- [2] [Character Region Awareness for Text Detection](https://github.com/KimRass/Place-Translation/blob/main/papers/character_region_awareness_for_text_detection.pdf)
- [3] [Semantic Image Segmentation with Deep Convolutional Nets and Fully Connected CRFs](https://github.com/KimRass/Place-Translation/blob/main/papers/semantic_image_segmentation_with_deep_convolutional_nets_and_fully_connected_crfs.pdf)
- [4] [Stroke-Based Scene Text Erasing Using Synthetic Data for Training](https://github.com/KimRass/Place-Translation/blob/main/papers/stroke_based_scene_text_erasing_using_synthetic_data_for_training.pdf)
- [5] [Resolution-robust Large Mask Inpainting with Fourier Convolutions](https://github.com/KimRass/Place-Translation/blob/main/papers/resolution_robust_large_mask_inpainting_with_fourier_convolutions.pdf)
- [6] [KAIST Scene Text Database](http://www.iapr-tc11.org/mediawiki/index.php/KAIST_Scene_Text_Database)
- [7] [SCUT-EnsText](https://github.com/HCIILAB/SCUT-EnsText) test set (813 images)

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

<!-- ## Implementation Detail
- Image
    - <img src="https://github.com/KimRass/pggan_from_scratch/assets/105417680/b33e2094-d0bd-491b-8bad-47dafb664068" width="350">
- Ground truth
    - <img src="https://github.com/KimRass/pggan_from_scratch/assets/105417680/6931254c-d169-44bd-90aa-149c5d973b6e" width="350">
- Text removed image (Rule-based text stroke mask)
    - <img src="https://github.com/KimRass/pggan_from_scratch/assets/105417680/74ab1ccb-873d-4b28-a3fa-38b499f704bb" width="350">
- Prediction and ground truth
    - <img src="https://i.imgur.com/VXC2eTl.jpg" width="600">
- (Top left) True positive, (Top right) False positive, (Bottom right) True negative and (Bottom left) False negative
- True positive, False positive, True negative and False negative
    - <img src="https://i.imgur.com/jRVLNFK.jpg" width="600">
    - <img src="https://github.com/KimRass/pggan_from_scratch/assets/105417680/f1e180ab-68a5-487e-80ae-28f90d7ae6ab" width="350">
    - <img src="https://github.com/KimRass/pggan_from_scratch/assets/105417680/f813c302-2001-4b4f-a77e-fcfbe2cca32e" width="350">
    - <img src="https://github.com/KimRass/pggan_from_scratch/assets/105417680/5b884ac7-3331-40c2-b636-21d16af0fc18" width="350">
    - <img src="https://github.com/KimRass/pggan_from_scratch/assets/105417680/94ce0355-5789-4d20-a5f0-deee4aebd5ba" width="350"> -->
