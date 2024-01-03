# 1. Overview
- old image가 있고 old image와 약간의 차이점만 있는 new image가 있을 때 old image와 new image 간의 feature matching을 통해 new image를 적절한 해상도로 resize하는 알고리즘입니다.
- 'SIFT' ('Scale-Invariant Feature Transform')와 'RANSAC' ('RANdom SAmple Consensus')를 사용합니다.
- new image를 resize한 후 생기는 빈 영역은 old image로부터 그대로 가져오고 반대의 경우에는 영역을 잘라냅니다.
- new image를 이미지가 아닌 pdf 파일로 지정할 경우 feature matching이 가장 많이 발생한 페이지를 자동으로 찾아내어 이를 new image로서 사용합니다.

# 2. Improvements
- new image에 대해 새롭게 이미지 번역을 진행하지 않고도 old image에 맞춰 annotate한 bounding boxes와 각 bounding box가 가지고 있는 번역문, 텍스트 속성 등을 그대로 사용할 수 있습니다.
- 기존에 포토샵 등을 사용해서 수작업으로 image resizing할 필요가 없습니다.

# 3. Examples
- 음식의 가격이 바뀐 경우
    - Old image ($2195 \times 2252$)
        - <img src="https://github.com/KimRass/Flitto-ML/assets/67457712/58e0dcd0-aa00-4032-945f-e0330b60f923" width="300">
    - New image ($9669 \times 9670$)
        - <img src="https://github.com/KimRass/Flitto-ML/assets/67457712/b032e67e-5854-4c64-833a-377cf5a3ffa4" width="500">
    - New image, resized ($2195 \times 2252$)
        - <img src="https://github.com/KimRass/Flitto-ML/assets/67457712/6cff2872-10e4-42af-b5c2-ff516f876a2b" width="300">
- 음식 이름이 바뀐 경우
    - Old image ($1240 \times 1754$)
        - <img src="https://github.com/KimRass/Flitto-ML/assets/67457712/63a4b6fb-75fe-4e31-b206-18c0fc8fcf7f" width="300">
    - New image ($1654 \times 2339$)
        - <img src="https://github.com/KimRass/Flitto-ML/assets/67457712/4c57b9a3-5a97-4fee-bf2c-f303bf286f28" width="400">
    - New image, resized ($1240 \times 1754$)
        - <img src="https://github.com/KimRass/Flitto-ML/assets/67457712/72307542-b7c0-49f9-b705-34ffe9ffac0b" width="300">
