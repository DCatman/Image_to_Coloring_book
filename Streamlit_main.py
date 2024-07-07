import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import pyperclip


def upscale_image(image, scale_percent=200):
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)
    return cv2.resize(image, dim, interpolation=cv2.INTER_LINEAR)


def image_to_coloring_book(image, scale_percent=200):
    grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Upscale the image
    upscaled_image = upscale_image(grayscale_image, scale_percent)

    # Apply Gaussian Blur to the image
    blurred = cv2.GaussianBlur(upscaled_image, (5, 5), 0)

    # Use adaptive thresholding to get a binary image
    adaptive_thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    # Invert the colors to make the outlines more visible
    inverted_image = cv2.bitwise_not(adaptive_thresh)

    return inverted_image


def copy_image_to_clipboard(image):
    pil_image = Image.fromarray(image)
    output = io.BytesIO()
    pil_image.convert("RGB").save(output, format="BMP")
    data = output.getvalue()[14:]  # The BMP header is not required
    output.close()

    pyperclip.copy(data)


def main():
    st.title("Image to Coloring Book Converter")

    uploaded_file = st.file_uploader("Choose an image...", type=["png", "jpg", "jpeg", "bmp", "tiff"])
    scale_percent = st.slider("Scale Percent", min_value=1, max_value=600, value=200)

    if uploaded_file is not None:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, 1)

        processed_image = image_to_coloring_book(image, scale_percent)

        col1, col2 = st.columns(2)

        with col1:
            st.header("Original Image")
            st.image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), caption='Original Image', use_column_width=True)

        with col2:
            st.header("Processed Image")
            st.image(processed_image, caption='Processed Image', use_column_width=True)

        if st.button('Save Processed Image'):
            result = Image.fromarray(processed_image)
            buf = io.BytesIO()
            result.save(buf, format="PNG")
            byte_im = buf.getvalue()
            st.download_button(label="Download Processed Image", data=byte_im, file_name="processed_image.png",
                               mime="image/png")

        if st.button('Copy Processed Image to Clipboard'):
            copy_image_to_clipboard(processed_image)
            st.success("Processed image copied to clipboard!")


if __name__ == "__main__":
    main()
