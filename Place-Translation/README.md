# 1. 'Place Translation'
- 음식점의 메뉴 이미지를 다국어로 번역해 QR 코드를 통해 제공하는 서비스입니다.
## Process
- OCR
    - <img src="https://github.com/flitto/express-param/assets/105417680/7caaf45f-d45a-439d-8e2c-fafbe7ff8f99" width="600">
    - OCR 엔진을 통해 1차적으로 OCR을 수행한 후 약간의 수작업을 통해 둘 이상의 bounding box를 서로 합치거나 하나의 bounding box를 둘로 나누는 등의 보정 작업을 수행합니다. scene text recognition 결과에 대해서는 자체적으로 보유한 크라우드 소싱 데이터 레이블링 플랫폼을 통해 검수를 진행합니다.
    - 이때 language identification 모델을 통해 외국어 나란히쓰기에 해당하는 텍스트와 가격을 나타내는 텍스트는 OCR을 진행하지 않습니다. 외국어 나란히쓰기한 텍스트는 번역을 진행하지 않고 지우기만 하고 가격을 나타내는 텍스트는 그대로 두기 때문입니다.
- ***Scene text removal***
    - <img src="https://github.com/flitto/express-param/assets/105417680/efe0d60c-87df-4a72-8776-5f8f29c69a29" width="600">
    - 원본 이미지에서 자연스럽게 글자를 지웁니다. 이때 OCR 과정에서 annotation을 하지 않은 외국어 나란히쓰기한 텍스트 또한 지우기 위해 OCR 엔진을 사용합니다.
    - 이 과정에서 2개의 기능을 사용하는데, 텍스트를 지우기 위해서는 scene text detection 모델을 사용해서 텍스트 영역만을 타게팅하여 지웁니다.
    - 이 과정에서 완전하게 제거되지 않은 텍스트가 있다면, 이 텍스트는 이미 그 일부가 지워져 텍스트로서 탐지되지 않으므로 사용자가 생성한 마스크를 사용해서 image inpainting을 수행합니다.
- Translation
    - machine translation을 수행한 후 검수합니다 (MTPE).
- ***Textual attribute recognition***
    - 원본 이미지의 텍스트 스타일을 그대로 적용하기 위해 text color 등의 텍스트 속성을 추출합니다.
- Text rendering
    - CSS를 통해 번역문을 렌더링하여 고객에게 제공합니다.

# 2. Examples
- 청계천: https://qr.flit.to/intro/cheonggye
- 더현대 서울: https://qr.flit.to/info/thehyundai
- 2022이태원 지구촌 축제
https://qr.flit.to/info/itaewon2022
- 통인시장: https://qr.flit.to/info/tongin2022
- 롯데백화점 본점: https://qr.flit.to/info/lottemainbranch
- 롯데백화점 잠실점: https://qr.flit.to/info/lottejamsilbranch
- 현대백화점 무역센터점: https://qr.flit.to/info/hyundaitcs
- 용산어린이정원 (용산공원): https://qr.flit.to/info/yongsan_chgd
- 신세계백화점 강남점: https://qr.flit.to/info/shinsegae_g
- 신세계백화점 부산센텀시티점: https://qr.flit.to/info/shinsegae_c
- 영등포구청: https://qr.flit.to/info/yeongdeungpo
