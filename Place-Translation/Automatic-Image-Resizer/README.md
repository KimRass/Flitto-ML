# Automatic Image Resizer
- 'SIFT' ('Scale-Invariant Feature Transform')와 'RANSAC' ('RANdom SAmple Consensus')를 사용해, Old image에 약간의 변화를 준 New image를 Old image에 맞게 Resize합니다.
- New image를 Resize한 후 생기는 빈 영역은 Old image로부터 그대로 가져옵니다.
## Example
- Old image ($2195 \times 2252$)
    - <img src="https://github.com/KimRass/automatic_image_resizer/assets/67457712/5be8bc8b-fb89-41cb-8a99-3f323a1787ab" width="300">
- New image ($9669 \times 9670$)
    - <img src="https://github.com/KimRass/automatic_image_resizer/assets/67457712/46227b43-caf5-442e-ba0b-e0b62edafa19" width="500">
- New image, resized ($2195 \times 2252$)
    - <img src="https://github.com/KimRass/automatic_image_resizer/assets/67457712/08b1d9c2-5263-4797-ae20-42eff0bf4269" width="300">
## How to Run
```sh
# Example with target directory
# Supports jpg, jpeg or png files by default
python3 main.py\
    --dir=".../automatic_image_resizer/samples"\
    --ext="png"
```
```sh
# Example with target image paths
python3 main.py\
    --old_img=".../automatic_image_resizer/samples/eataly3_old.jpg"\ # ".../filename_old.ext"
    --new_img=".../automatic_image_resizer/samples/eataly3_new.jpg"\ # ".../filename_new.ext"
    --ext="jpg"
```
