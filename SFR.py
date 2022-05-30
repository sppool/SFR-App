import numpy as np
import math
import matplotlib
import matplotlib.pyplot as plt
import cv2


def show_(img, s=5):  # show the image
    img = img.copy()
    img = img.astype(np.uint8)
    plt.figure(figsize=(s, s))
    if img.ndim == 3:  # color image
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # OpenCV 的色彩空間 BRG
        plt.imshow(img, vmin=0, vmax=255)
    else:  # gray image
        plt.imshow(img, cmap='gray', vmin=0, vmax=255)
    plt.xticks([]), plt.yticks([])
    plt.show()


def CreakRoi(roi):
    # 檢查 Roi 翻轉成正確的方向
    h_val = np.abs(roi[0, :].mean() - roi[-1, :].mean())
    v_val = np.abs(roi[:, 0].mean() - roi[:, -1].mean())
    if h_val > v_val:
        roi = roi.T
    if roi[:, 0].mean() > roi[:, -1].mean():
        roi = roi[:, ::-1]

    return roi


def get_linear_reg(arr):
    n = arr.shape[0]
    X = np.vstack((np.ones(n), np.arange(n))).T
    b = np.linalg.inv(X.T.dot(X)).dot(X.T).dot(arr)
    outputs = X.dot(b)

    return outputs


def GetFFTArr(roi):
    # 檢查 Roi 翻轉成正確的方向(上下左右的排列而已 非角度)
    roi = CreakRoi(roi)

    # 取得需要旋轉的角度
    diff = np.abs(np.diff(roi.astype(np.int64), 1, 1))
    # diff = np.diff(roi.astype(np.int64), 1, 1)

    # 取得斜線資料
    # n = diff.shape[1]
    # x = (diff * np.arange(0, n)).sum(1) / diff.sum(1) # 取水平px重心
    x = diff.argmax(1)  # 取最大值

    # 取角度的方法
    l = get_linear_reg(x)
    angle = np.rad2deg(np.arctan(l[1] - l[0]))

    # 旋轉Roi
    h, w = roi.shape
    M = cv2.getRotationMatrix2D((w/2, h/2), -angle, 1)
    cut = math.ceil(np.abs(h * np.sin(np.deg2rad(angle)) / 2))
    if cut != 0:
        roi_rot = cv2.warpAffine(roi, M, (w, h))[cut:-cut, cut:-cut]
    else:
        roi_rot = roi

    # LSF
    diff_rot = np.diff(roi_rot.astype(np.int64), 1, 1)
    # plt.imshow(diff_rot)
    # plt.show()

    LSF = diff_rot.mean(0)
    # plt.plot(LSF)
    # plt.show()

    # 傅立葉轉換且正規化
    fft = np.fft.fft(LSF)
    n = fft.size + 1
    fft = np.abs(fft[:n // 2])
    fft /= fft[0]
    fft *= 100  # 百分比

    return fft


def GetArrFreqVal(fft, freq):
    if freq == 1:
        return fft[-1]

    if freq == 0:
        return fft[0]

    # 取指定頻率的值
    f_ind = (fft.size - 1) * freq
    i_ind = int(f_ind)
    f_ind -= i_ind
    res = fft[i_ind]
    offset = (fft[i_ind] - fft[i_ind + 1]) * f_ind
    res += offset

    return res


def ShowFFTImg(fft):
    # Shoe 圖
    plt.close()
    plt.plot(np.linspace(0, 1, fft.size), fft)
    plt.ylim(bottom=0, top=fft.max() * 1.05)
    plt.show()
