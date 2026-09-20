# import os
# import pickle
# import numpy as np
# import cv2
# from keras.applications.resnet50 import ResNet50, preprocess_input
# from keras.layers import GlobalMaxPooling2D
# import tensorflow as tf
# from numpy.linalg import norm

# # Load ResNet50 model
# model = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
# model.trainable = False
# model = tf.keras.Sequential([model, GlobalMaxPooling2D()])

# # Path to your images
# image_directory = r'D:\Work folder\projects\git code\Fashion recomendation system\Fashion-Recommendations--main\New folder\images'


# # Function to extract features from an image
# def extract_feature(img_path, model):
#     img = cv2.imread(img_path)
#     img = cv2.resize(img, (224, 224))
#     img = np.array(img)
#     expand_img = np.expand_dims(img, axis=0)
#     pre_image = preprocess_input(expand_img)
#     result = model.predict(pre_image).flatten()
#     normalized = result / norm(result)
#     return normalized

# # Extract features for all images
# feature_list = []
# filenames = []
# for filename in os.listdir(image_directory):
#     if filename.endswith('.jpg') or filename.endswith('.png'):  # Adjust based on your image formats
#         img_path = os.path.join(image_directory, filename)
#         feature = extract_feature(img_path, model)
#         feature_list.append(feature)
#         filenames.append(img_path)

# # Save the features and filenames into pickle files
# with open('featurevector.pkl', 'wb') as f:
#     pickle.dump(np.array(feature_list), f)
    
# with open('filenames.pkl', 'wb') as f:
#     pickle.dump(filenames, f)

# print("Feature vectors and filenames have been saved.")


import os
import pickle
import numpy as np
import cv2
from keras.applications.resnet50 import ResNet50, preprocess_input
from keras.layers import GlobalMaxPooling2D
import tensorflow as tf
from numpy.linalg import norm
from multiprocessing import Pool

# Load ResNet50 model
model = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
model.trainable = False
model = tf.keras.Sequential([model, GlobalMaxPooling2D()])

# Path to your images
image_directory = r'D:\Work folder\projects\git code\Fashion recomendation system\Fashion-Recommendations--main\New folder\image'

# Function to extract features from an image
def extract_feature(img_path):
    try:
        img = cv2.imread(img_path)
        if img is None:
            print(f"Warning: Unable to load image {img_path}")
            return None  # Skip this image
        img = cv2.resize(img, (224, 224))
        img = np.array(img)
        expand_img = np.expand_dims(img, axis=0)
        pre_image = preprocess_input(expand_img)
        result = model.predict(pre_image).flatten()
        normalized = result / norm(result)
        return normalized, img_path
    except Exception as e:
        print(f"Error processing image {img_path}: {e}")
        return None

# Function to process images in parallel
def process_images(image_paths):
    with Pool(processes=4) as pool:  # Use 4 processes (one for each core)
        results = pool.map(extract_feature, image_paths)
    return [result for result in results if result is not None]  # Filter out None values

# Main guard for Windows compatibility
if __name__ == '__main__':
    # Get all image paths in the directory
    image_paths = [
        os.path.join(image_directory, filename)
        for filename in os.listdir(image_directory)
        if filename.endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'))
    ]

    # Process the images and extract features
    feature_list = []
    filenames = []

    results = process_images(image_paths)

    # Store the results into feature_list and filenames
    for feature, filename in results:
        feature_list.append(feature)
        filenames.append(filename)

    # Save the features and filenames into pickle files
    with open('featurevector.pkl', 'wb') as f:
        pickle.dump(np.array(feature_list), f)

    with open('filenames.pkl', 'wb') as f:
        pickle.dump(filenames, f)

    print("Feature vectors and filenames have been saved.")
