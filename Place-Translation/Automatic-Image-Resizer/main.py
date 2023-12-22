# Referebces
    # https://gist.github.com/tigercosmos/90a5664a3b698dc9a4c72bc0fcbd21f4

from pdf2image import convert_from_path
import cv2
import numpy as np
import argparse
from pathlib import Path
import re

from image_utils import (
    load_image,
    show_image,
    save_image,
    _to_array,
    _get_width_and_height,
    _resize_image,
    _to_grayscale,
    _mask_image,
    _get_canvas_same_size_as_image,
    _sharpen,
    _resize_image_using_shorter_side,
)


def get_error(points, H):
    num_points = len(points)
    all_p1 = np.concatenate((points[:, 0: 2], np.ones((num_points, 1))), axis=1)
    all_p2 = points[:, 2: 4]
    estimate_p2 = np.zeros((num_points, 2))
    for i in range(num_points):
        temp = np.dot(H, all_p1[i])
        estimate_p2[i] = (temp/temp[2])[0: 2]
    errors = np.linalg.norm(all_p2 - estimate_p2 , axis=1) ** 2
    return errors


def _get_number_of_keypoints(matches, thresh, n_iters):
    n_best_inliers = 0
    exists = False
    for _ in range(n_iters):
        points = _sample_points(matches)
        H = homography(points)
        
        #  Avoid dividing by zero 
        if np.linalg.matrix_rank(H) < 3:
            continue

        exists = True
        errors = get_error(matches, H)
        idx = np.where(errors < thresh)[0]
        inliers = matches[idx]

        n_inliers = len(inliers)
        if n_inliers > n_best_inliers:
            best_inliers = inliers.copy()
            n_best_inliers = n_inliers
    return best_inliers.shape[0] if exists else 0


def perform_sift(img):
    img_gray = _to_grayscale(img)
    detector = cv2.SIFT_create()
    kp, des = detector.detectAndCompute(img_gray, None)
    return kp, des


def matcher(kp1, des1, kp2, des2, thresh):
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1,des2, k=2)

    good = list()
    for m,n in matches:
        if m.distance < thresh * n.distance:
            good.append([m])

    matches = list()
    for pair in good:
        matches.append(list(kp1[pair[0].queryIdx].pt + kp2[pair[0].trainIdx].pt))

    matches = np.array(matches)
    return matches


def homography(pairs):
    rows = list()
    for i in range(pairs.shape[0]):
        p1 = np.append(pairs[i][0: 2], 1)
        p2 = np.append(pairs[i][2: 4], 1)
        row1 = [0, 0, 0, p1[0], p1[1], p1[2], -p2[1]*p1[0], -p2[1]*p1[1], -p2[1]*p1[2]]
        row2 = [p1[0], p1[1], p1[2], 0, 0, 0, -p2[0]*p1[0], -p2[0]*p1[1], -p2[0]*p1[2]]
        rows.append(row1)
        rows.append(row2)
    rows = np.array(rows)
    U, s, V = np.linalg.svd(rows)
    H = V[-1].reshape(3, 3)
    H = H / H[2, 2] # standardize to let w*H[2,2] = 1
    return H


def _sample_points(matches, k=4):
    return matches[np.random.choice(matches.shape[0], size=k), :]


def perform_ransac(matches, thresh, n_iters):
    n_best_inliers = 0
    for _ in range(n_iters):
        points = _sample_points(matches)
        H = homography(points)
        
        #  Avoid dividing by zero 
        if np.linalg.matrix_rank(H) < 3:
            continue

        errors = get_error(matches, H)
        idx = np.where(errors < thresh)[0]
        inliers = matches[idx]

        n_inliers = len(inliers)
        if n_inliers > n_best_inliers:
            n_best_inliers = n_inliers
            best_H = H.copy()
    return best_H


def _get_coordinates(old_img, H):
    src_h, src_w, _ = old_img.shape
    corners = [[0, 0, 1], [src_w, 0, 1], [src_w, src_h, 1], [0, src_h, 1]]
    new_corners = [np.dot(H, corner) for corner in corners]
    new_corners = np.array(new_corners).T
    x_news = new_corners[0] / new_corners[2]
    y_news = new_corners[1] / new_corners[2]
    return round(min(x_news)), round(min(y_news)), round(max(x_news)), round(max(y_news))


def resize(old_img, new_img):
    old_w, old_h = _get_width_and_height(old_img)
    resized_new_img = _resize_image(new_img, w=old_w, h=old_h)

    src_kp, src_des = perform_sift(old_img)
    dst_kp, dst_des = perform_sift(resized_new_img)

    matches = matcher(kp1=src_kp, des1=src_des, kp2=dst_kp, des2=dst_des, thresh=0.5)
    best_H = perform_ransac(matches, thresh=0.5, n_iters=200)

    xmin, ymin, xmax, ymax = _get_coordinates(resized_new_img, best_H)

    src = np.array([[xmin, ymin], [xmax, ymin], [xmax, ymax], [xmin, ymax]], dtype="float32")
    dst = np.array([[0, 0], [old_w, 0], [old_w, old_h], [0, old_h]], dtype="float32")
    M = cv2.getPerspectiveTransform(src=src, dst=dst)
    out = cv2.warpPerspective(src=resized_new_img, M=M, dsize=(old_w, old_h))

    mask = _get_canvas_same_size_as_image(old_img)
    mask = cv2.warpPerspective(src=mask, M=M, dsize=(old_w, old_h))
    bg = _mask_image(img=old_img, mask=mask, invert=True)
    out = np.maximum(out, bg)
    return out


def get_args():
    parser = argparse.ArgumentParser("Automatic Image Resizer")

    parser.add_argument("--dir", type=str, help="Directory containing old images and new images")

    parser.add_argument("--old_img", type=str, help="Old image to be replaced by the resized image")
    parser.add_argument("--new_img", type=str, help="New image to be resized", default="")
    parser.add_argument("--new_pdf", type=str, help="Pdf file contatining new image to be resized", default="")

    parser.add_argument("--ext", type=str, help="File extension for resized images", default="png")

    parser.add_argument(
        "--side_length", type=int, help="Length of shorter side between width and height", default=0,
    )
    args = parser.parse_args()
    return args


def get_best_matching_image(pdf_path, trg_img):
    maxim = 0
    for new_img in convert_from_path(pdf_path):
        new_img = _to_array(new_img)

        w, h = _get_width_and_height(new_img)
        trg_img = _resize_image(trg_img, w=w, h=h)

        src_kp, src_des = perform_sift(trg_img)
        dst_kp, dst_des = perform_sift(new_img)

        matches = matcher(kp1=src_kp, des1=src_des, kp2=dst_kp, des2=dst_des, thresh=0.5)
        n_points = _get_number_of_keypoints(matches, thresh=0.5, n_iters=200)
        if n_points > maxim:
            fin_new_img = new_img.copy()
            maxim = n_points
    return fin_new_img


if __name__ == "__main__":
    args = get_args()

    if args.dir:
        for old_img_path in Path(args.dir).glob("*"):
            if not re.search(pattern=r"_old.jpg$|_old.jpeg$|_old.png$", string=str(old_img_path)):
                continue

            save_path = old_img_path.parent/f"""{old_img_path.stem[: -4]}_new_resized.{args.ext}"""
            if save_path.exists():
                print(f"""The resized image for '{old_img_path.name}' already exists!""")
            else:
                old_img = load_image(old_img_path)

                new_pdf_path = old_img_path.parent/f"""{old_img_path.stem[: -4]}_new.pdf"""
                new_jpg_path = old_img_path.parent/f"""{old_img_path.stem[: -4]}_new.jpg"""
                new_jpeg_path = old_img_path.parent/f"""{old_img_path.stem[: -4]}_new.jpeg"""
                new_png_path = old_img_path.parent/f"""{old_img_path.stem[: -4]}_new.png"""
                if new_pdf_path.exists():
                    new_img = get_best_matching_image(pdf_path=new_pdf_path, trg_img=old_img)
                elif new_jpg_path.exists():
                    new_img = load_image(new_jpg_path)
                elif new_jpg_path.exists():
                    new_img = load_image(new_jpeg_path)
                elif new_jpg_path.exists():
                    new_img = load_image(new_png_path)

                out = resize(old_img=old_img, new_img=new_img)
                out = _sharpen(out)

                if args.side_length != 0:
                    out = _resize_image_using_shorter_side(out, side_length=args.side_length)

                save_image(img=out, path=str(save_path))
                print(f"""Saved the resized image as '{save_path.name}'!""")

    else:
        save_path = Path(args.old_img).parent/f"""{Path(args.old_img).stem[: -4]}_new_resized.{args.ext}"""
        if save_path.exists():
            print(f"""'{str(save_path)}' already exists!""")
        else:
            old_img = load_image(args.old_img)
            if args.new_pdf:
                new_img = get_best_matching_image(pdf_path=args.new_pdf, trg_img=old_img)
            else:
                new_img = load_image(args.new_img)

            out = resize(old_img=old_img, new_img=new_img)
            out = _sharpen(out)

            if args.side_length != 0:
                    out = _resize_image_using_shorter_side(out, side_length=args.side_length)

            save_image(img=out, path=str(save_path))
            print(f"""Saved the resized image as '{str(save_path)}'!""")
