# -*- coding: utf-8 -*-
"""Untitled17.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1TA87T5MmMDQjV7IKsUucTiPeNBQUxSQE
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt

# Load images
query_img_read = cv2.imread('query.jpg')   # Object image

query_img = cv2.imread('query.jpg', cv2.IMREAD_GRAYSCALE)   # Object image
target_img = cv2.imread('target.jpg', cv2.IMREAD_GRAYSCALE) # Scene image

# Initialize SIFT detector
sift = cv2.SIFT_create()

# Find keypoints and descriptors
kp1, des1 = sift.detectAndCompute(query_img, None)
kp2, des2 = sift.detectAndCompute(target_img, None)

# Use FLANN based matcher for better performance
FLANN_INDEX_KDTREE = 1
index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
search_params = dict(checks=50)

flann = cv2.FlannBasedMatcher(index_params, search_params)
matches = flann.knnMatch(des1, des2, k=2)

# Store good matches using Lowe's ratio test
good_matches = []
for m, n in matches:
    if m.distance < 0.7 * n.distance:
        good_matches.append(m)

if len(good_matches) > 10:
    # Get matching keypoints
    src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

    # Find homography
    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

    # Get the size of query image
    h, w = query_img.shape

    # Define query corners
    pts = np.float32([[0, 0], [0, h], [w, h], [w, 0]]).reshape(-1, 1, 2)
    dst = cv2.perspectiveTransform(pts, M)

    # Draw polygon (rectangle) around the detected object
    target_img_color = cv2.cvtColor(target_img, cv2.COLOR_GRAY2BGR)
    cv2.polylines(target_img_color, [np.int32(dst)], True, (0, 255, 0), 3, cv2.LINE_AA)

    # Display the result
    plt.imshow(query_img_read)
    plt.title("query")
    plt.axis('off')
    plt.show()
    plt.figure(figsize=(12, 8))
    plt.imshow(cv2.cvtColor(target_img_color, cv2.COLOR_BGR2RGB))
    plt.title("Target Image")
    plt.axis('off')
    plt.show()

else:
    print("Not enough matches are found - {}/10".format(len(good_matches)))