# Automatic Image Resizer
- 기존 메뉴 이미지 ('old image')가 존재하고 여기에 가격 변경 등 약간의 변경점이 있는 새로운 이미지가 ('new image') 있을 때, 이 새로운 이미지를 기존 이미지에 맞게 적절히 resize함으로써 불필요하게 bounding box annotation 등의 작업을 다시 할 필요가 없도록 하는 모델입니다.
- new image를 resize한 후 빈 영역이 생기면 old image로부터 가져온 영역을 통해 채웁니다.
- new image가 한 장의 이미지가 아닌 여러 장의 이미지를 포함하는 pdf파일로 주어진다면 이중 old image와 가장 많은 feature matching이 발생하는 이미지를 자동으로 찾아 new image로 지정합니다.
- 'SIFT' ('Scale-Invariant Feature Transform')와 'RANSAC' ('RANdom SAmple Consensus')를 사용합니다.
## Example
- Old image ($2195 \times 2252$)
    - <img src="https://github.com/KimRass/automatic_image_resizer/assets/67457712/5be8bc8b-fb89-41cb-8a99-3f323a1787ab" width="300">
- New image ($9669 \times 9670$)
    - <img src="https://github.com/KimRass/automatic_image_resizer/assets/67457712/46227b43-caf5-442e-ba0b-e0b62edafa19" width="500">
- New image, resized ($2195 \times 2252$)
    - <img src="https://github.com/KimRass/automatic_image_resizer/assets/67457712/08b1d9c2-5263-4797-ae20-42eff0bf4269" width="300">
