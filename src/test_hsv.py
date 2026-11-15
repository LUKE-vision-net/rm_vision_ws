import cv2
import numpy as np

# 生成一张和 S0 一模一样的纯蓝图片
img = np.zeros((600, 800, 3), dtype=np.uint8)
cv2.rectangle(img, (400-40, 300-40), (400-20, 300+40), (255, 0, 0), -1) # 左边蓝条

# 1. 转 HSV
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# 2. 提取这个蓝条中心点（400-30, 300）的 HSV 值
# 注意：图片坐标是 (x, y)，但 numpy 数组是 [y, x]
target_pixel_bgr = img[300, 400-30] 
target_pixel_hsv = hsv[300, 400-30]

print(f"这个蓝条在 OpenCV 里的 BGR 值是: {target_pixel_bgr}")
print(f"这个蓝条在 OpenCV 里的 HSV 值是: {target_pixel_hsv}")