import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

def upscale_image(image, scale_percent=200):
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)
    return cv2.resize(image, dim, interpolation=cv2.INTER_LINEAR)

def image_to_coloring_book(image, scale_percent=200):
    grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    upscaled_image = upscale_image(grayscale_image, scale_percent)
    blurred = cv2.GaussianBlur(upscaled_image, (5, 5), 0)
    adaptive_thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    inverted_image = cv2.bitwise_not(adaptive_thresh)
    return inverted_image

st.title("Image to Coloring Book Converter")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png", "bmp", "tiff"])

scale_percent = st.slider("Scale Percent", 1, 600, 200)

if uploaded_file is not None:
    image = np.array(Image.open(uploaded_file))
    st.image(image, caption='Original Image', use_column_width=True)

    processed_image = image_to_coloring_book(image, scale_percent)
    st.image(processed_image, caption='Processed Image', use_column_width=True)

    buf = io.BytesIO()
    result_image = Image.fromarray(processed_image)
    result_image.save(buf, format="PNG")
    byte_im = buf.getvalue()

    st.download_button(
        label="Download Processed Image",
        data=byte_im,
        file_name="processed_image.png",
        mime="image/png",
    )
