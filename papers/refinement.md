# `_pyrdown`
```python
def _pyrdown(im : torch.Tensor, downsize : tuple=None):
    ...
    if downsize is None:
        downsize = (im.shape[2]//2, im.shape[3]//2)
```
- `downsize` 인자에 어떤 값을 주는 경우는 없습니다. 따라서 이 함수에서는 이미지를 항상 절반의 크기로 Downscale합니다.

# `_pyrdown_mask`
```python
def _pyrdown_mask(mask : torch.Tensor, downsize : tuple=None, eps : float=1e-8, blur_mask : bool=True, round_up : bool=True):
    ...
    if downsize is None:
        downsize = (mask.shape[2]//2, mask.shape[3]//2)
    ...
    if round_up:
```
- `_pyrdown`과 마찬가지로 `downsize` 인자에 어떤 값을 주는 경우는 없습니다. 따라서 이 함수에서는 마스크를 항상 절반의 크기로 Downscale합니다.
- 이 함수가 사용될 때 `blur_mask`와 `round_up`은 항상 둘 다 `True` 또는 `False`를 값으로 받습니다. 따라서 `round_up`은 필요가 없습니다.
## Difference by `blur_mask`
- Original mask (2,482 x 3,509)
    - <img src="https://i.imgur.com/SY3xdpI.png" alt="original_mask" width="600">
- The first scale of mask pyramid (1,128 x 1,595)
    - <img src="https://i.imgur.com/cxgRh9R.png" alt="first_scale" width="500">
- The second scale of mask pyramid when `blur_mask=False` (564 x 797)
    - <img src="https://i.imgur.com/fqZE4RB.png" alt="second_scale_false" width="400">
- The second scale of mask pyramid when `blur_mask=True` (564 x 797)
    - <img src="https://i.imgur.com/7LC93al.png" alt="second_scale_true" width="400">

# `_get_image_mask_pyramid`
```python
breadth = min(h,w)
n_scales = min(1 + int(round(max(0,np.log2(breadth / min_side)))), max_scales)
```
- 이미지의 가로와 세로 중 작은 쪽을 기준으로 `n_scales`가 정해지고 `max_scales`보다 클 수 없습니다.
    - `min_side * 2` 이상부터 `n_scales=2`
    - `min_side * 4` 이상부터 `n_scales=3`
    - 그 외 `n_scales=1`


# `_infer`
```python
pred_downscaled = _pyrdown(pred[:,:,:orig_shape[0],:orig_shape[1]])
mask_downscaled = _pyrdown_mask(mask[:,:1,:orig_shape[0],:orig_shape[1]], blur_mask=False, round_up=False)
```
- `pad_tensor_to_modulo`를 사용했으므로 원래의 해상도로 복원합니다.

# `refine_predict`
```python
gpu_ids = [f'cuda:{gpuid}' for gpuid in gpu_ids.replace(" ","").split(",") if gpuid.isdigit()]
```
- `"0,1, 2"` -> `['cuda:0', 'cuda:1', 'cuda:2']`
```python
n_resnet_blocks = 0
first_resblock_ind = 0
found_first_resblock = False
for idl in range(len(inpainter.generator.model)):
    if isinstance(inpainter.generator.model[idl], FFCResnetBlock) or isinstance(inpainter.generator.model[idl], ResnetBlock):
        n_resnet_blocks += 1
        found_first_resblock = True
    elif not found_first_resblock:
        first_resblock_ind += 1
```
- 전체 36개의 모듈로 이루어져 있습니다.
```python
forward_front = inpainter.generator.model[0:first_resblock_ind]
```
- `first_resblock_ind`는 4이므로 `forward_front`는 36개의 모듈 중 처음 4개의 모듈이 됩니다.
```python
resblocks_per_gpu = n_resnet_blocks // len(gpu_ids)
...
forward_rears = []
for idd in range(len(gpu_ids)):
    if idd < len(gpu_ids) - 1:
        forward_rears.append(inpainter.generator.model[first_resblock_ind + resblocks_per_gpu*(idd):first_resblock_ind+resblocks_per_gpu*(idd+1)]) 
    else:
        forward_rears.append(inpainter.generator.model[first_resblock_ind + resblocks_per_gpu*(idd):]) 
    forward_rears[idd].to(devices[idd])
```
- 4개의 GPU를 쓴다고 가정해 보겠습니다. `n_resnet_block`는 18이므로 `resblocks_per_gpu`는 4입니다. 앞의 3개의 GPU에는 각각 Index 4 ~ 7, 8 ~ 11, 12 ~ 15에 해당하는 각 4개의 모듈이 할당됩니다. 그리고 마지막 1개의 GPU에는 Index 16 ~ 21에 해당하는 6개의 모듈이 할당됩니다.
```python
image = pad_tensor_to_modulo(image, modulo)
mask = pad_tensor_to_modulo(mask, modulo)
```
- Refine하지 않고 단순히 LaMa를 이용해 Infer할 때는 Pad가 필요 없습니다. Refine 시에만 필요합니다.
```python
image_inpainted = image_inpainted[:,:,:orig_shape[0], :orig_shape[1]]
```
- 원래의 해상도로 복원합니다.
