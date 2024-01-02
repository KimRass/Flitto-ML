# As-is
## Process
1. 고객으로부터 메뉴 이미지를 전달 받아 각 항목(음식)의 이름과 부과설명, 가격을 수작업으로 전사(scene text recognition)하여 표로 정리합니다.
2. 이 표를 가지고 Figma를 사용하여 수작업으로 메뉴 이미지를 만듭니다.
    - <img src="https://github.com/KimRass/KimRass/assets/67457712/2b8ea39c-d8cf-4ea9-a956-a5fa678c2554" width="400">
3. 이 메뉴 이미지를, 고객으로부터 받은 메뉴 이미지와 동일한 프로세스를 통해 이미지 번역을 수행합니다. 즉 OCR → scene text removal → translation → textual attribute recognition → text rendering를 순차적으로 수행합니다.
## Drawbacks
- 메뉴 이미지 제작 시 수작업이 들어갑니다.
- 전사(scene text recognition)시에 렌더링할 텍스트(원문)를 이미 파악하였고 메뉴 이미지 제작 시 각 텍스트의 좌표가 이미 정해져 있음에도 불구하고 불필요한 OCR을 수행하여 비효율적입니다.
- 추후에 텍스트를 지울 것임에도 불구하고 불필요하게 렌더링하는 과정을 거칩니다.
- 이미지 번역 품질이 매우 떨어집니다.
    - <img src="https://github.com/KimRass/KimRass/assets/67457712/6ab9a3d5-8ddd-4db3-96ac-1b5dbd181e9f" width="400">

# TO-be
## Process
1. 고객으로부터 메뉴 이미지를 전달 받아 각 항목(음식)의 이름과 부과설명, 가격을 수작업으로 전사(scene text recognition)하여 표로 정리합니다. (이전과 동일.)
2. 번역할 언어 각각에 대한 번역문을 추가합니다.
3. Python을 통해 텍스트를 제외한 나머지를 이미지로 만듭니다. 각 언어에 대해 텍스트별로 적절한 좌표와 줄바꿈을 계산하여 이미지와 함께 백엔드에 전달합니다. 프론트엔드에서는 이를 백엔드로부터 전달 받아 이미지에 번역문을 렌더링합니다.
    - <img src="https://github.com/KimRass/KimRass/assets/67457712/269b5620-2607-46fc-9579-64a4d6dd46b3" width="400">
## Improvements
- 메뉴 이미지 제작이 자동으로 이루어집니다.
- 불필요하고 중복된 작업이 없습니다.
- 이미지 번역 품질이 향상됩니다.
