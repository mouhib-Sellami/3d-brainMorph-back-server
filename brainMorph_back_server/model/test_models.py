# import tensorflow as tf
# from tensorflow.keras import backend as K
# print(tf.__version__)
# import os

# os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
# def iou_coef(y_true, y_pred, smooth=100):
#     intersection = K.sum(y_true * y_pred)
#     sum = K.sum(y_true + y_pred)
#     iou = (intersection + smooth) / (sum - intersection + smooth)
#     return iou


# try:
#     new_model = tf.keras.models.load_model(
#         './model_v2.keras', custom_objects={'iou_coef': iou_coef},compile=False)
#     new_model.summary()

# except TypeError as e:
#     print(f"Error loading model: {e}")
#     print("Please ensure that the TensorFlow/Keras version and custom objects are compatible.")
# print("here")
# from skimage.io import imread, imshow,imsave
# from skimage.transform import resize
# import numpy as np

# image = imread("./test.tif")
# image = resize(image, (256, 256), mode="constant", preserve_range=True)

# import time
# x = time.time()
# predictions = new_model.predict(np.expand_dims(image, axis=0), verbose=0)
# y= time.time()
# print(y-x)
# print("*"*100)
# imsave("./test_mask.tif",predictions,)
# import matplotlib.pyplot as plt
# plt.imshow(np.squeeze(predictions),cmap="gray")
# plt.show()
