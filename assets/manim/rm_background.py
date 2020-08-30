import argparse
import cv2
import numpy as np




def show_img(img):
    cv2.imshow("image", img)
    cv2.waitKey(0)

def new_filename(name):
    ext = name.split('.')[-1]
    path = ".".join(name.split(".")[:-1])
    return f"{path}_with_alpha.{ext}"

def add_alpha(img, threshold: int):
    b_channel, g_channel, r_channel = cv2.split(img)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray[gray < threshold] = 0
    alpha_channel = 255 - gray

    return cv2.merge((b_channel, g_channel, r_channel, alpha_channel))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--image", required=True, help="Path to the image")
    parser.add_argument("-t", "--threshold", required=False, type=int, default=250, help="Add the threshold needed to make it transparent")
    args = vars(parser.parse_args())

    image = cv2.imread(args["image"])

    new_img = add_alpha(image, args["threshold"])
    new_filaname = new_filename(args["image"])

    cv2.imwrite(new_filaname, new_img)