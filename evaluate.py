import numpy as np
from process_image import (
    _get_width_and_height
)


def _get_psnr(img1, img2, max_value=255):
    width1, height1 = _get_width_and_height(img1)
    width2, height2 = _get_width_and_height(img2)
    assert width1 == width2 and height1 == height2
    
    error = img1 - img2
    mse = np.sum(error * error) / (width1 * height1)

    if mse > 0:
        psnr = 10 * np.log10(max_value ** 2 / mse)
    else:
        psnr = 99
    return psnr
