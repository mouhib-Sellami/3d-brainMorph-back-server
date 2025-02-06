import numpy as np
from skimage.transform import resize
from skimage.io import imread, imsave
import tensorflow as tf
from tensorflow.keras import backend as K
import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
model = None


def iou_coef(y_true, y_pred, smooth=100):
    intersection = K.sum(y_true * y_pred)
    sum = K.sum(y_true + y_pred)
    iou = (intersection + smooth) / (sum - intersection + smooth)
    return iou


def init_model():
    try:
        global model
        model_path = os.path.join(
            os.getcwd(), 'brainMorph_back_server', 'model', 'model_v2.keras')
        model = tf.keras.models.load_model(
            model_path, custom_objects={'iou_coef': iou_coef}, compile=False)
    except TypeError as e:
        print(f"Error loading model: {e}")
    return model


def predict_save_image(image_path, model):
    if not model:
        raise Exception("model not loaded")
    else:
        image = imread(image_path)
        if image.shape == (1, 256, 256, 1):
            image = np.squeeze(image, axis=0)
            image = np.repeat(image, 3, axis=-1)
        image = resize(image, (256, 256), mode="constant",
                       preserve_range=True)
        predictions = model.predict(
            np.expand_dims(image, axis=0), verbose=0)
        image = np.squeeze(predictions, axis=0)

        image = np.squeeze(image, axis=-1)
        image[image > 0.1] = 1
        image[image < 0.1] = 0
        image = image * 255
        image = np.clip(image, 0, 1)
        output_path = image_path[:-4]
        print(output_path)
        output_path += "_mask.tif"
        imsave(output_path, image,)
