import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import win32clipboard
from io import BytesIO
from playsound import playsound

def upscale_image(image, scale_percent=200):
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)
    return cv2.resize(image, dim, interpolation=cv2.INTER_LINEAR)

def image_to_coloring_book(image_path, scale_percent=200):
    # Read the image
    original_image = cv2.imread(image_path)
    if original_image is None:
        print(f"Error: Unable to open image file {image_path}")
        return None, None

    grayscale_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)

    # Upscale the image
    upscaled_image = upscale_image(grayscale_image, scale_percent)

    # Apply Gaussian Blur to the image
    blurred = cv2.GaussianBlur(upscaled_image, (5, 5), 0)

    # Use adaptive thresholding to get a binary image
    adaptive_thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    # Invert the colors to make the outlines more visible
    inverted_image = cv2.bitwise_not(adaptive_thresh)

    return original_image, inverted_image

def resize_image(image, max_size):
    h, w = image.shape[:2]
    scale = min(max_size[0] / w, max_size[1] / h)
    return cv2.resize(image, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_LINEAR)

def open_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff")])
    if file_path:
        global original_image, processed_image, original_image_tk, processed_image_tk, current_image_path
        current_image_path = file_path
        original_image, processed_image = image_to_coloring_book(file_path, scale_percent=scale_percent.get())

        if original_image is not None and processed_image is not None:
            update_canvas_images()

def update_canvas_images():
    global original_image, processed_image, original_image_tk, processed_image_tk
    if original_image is not None and processed_image is not None:
        original_image_resized = resize_image(original_image, (canvas_width, canvas_height))
        processed_image_resized = resize_image(processed_image, (canvas_width, canvas_height))
        original_image_tk = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(original_image_resized, cv2.COLOR_BGR2RGB)))
        processed_image_tk = ImageTk.PhotoImage(image=Image.fromarray(processed_image_resized))
        canvas_original.create_image(0, 0, anchor=tk.NW, image=original_image_tk)
        canvas_processed.create_image(0, 0, anchor=tk.NW, image=processed_image_tk)

def process_image():
    global processed_image
    if current_image_path:
        _, processed_image = image_to_coloring_book(current_image_path, scale_percent=scale_percent.get())
        update_canvas_images()

def save_image():
    if processed_image is not None:
        save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if save_path:
            cv2.imwrite(save_path, processed_image)
            messagebox.showinfo("Image Saved", f"Processed image saved as {save_path}")
    else:
        messagebox.showwarning("No Image", "No processed image to save.")

def copy_image_to_clipboard(image):
    pil_image = Image.fromarray(image)
    output = BytesIO()
    pil_image.convert("RGB").save(output, format="BMP")
    data = output.getvalue()[14:]  # The BMP header is not required
    output.close()

    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()

    messagebox.showinfo("Copied", "Image copied to clipboard.")

def copy_processed_image_to_clipboard():
    global processed_image
    if processed_image is not None:
        copy_image_to_clipboard(processed_image)
    else:
        messagebox.showwarning("No Image", "No processed image to copy.")

def update_preview(event=None):
    process_image()

def update_scale_percent(value):
    scale_percent.set(int(float(value)))
    scale_percent_entry.delete(0, tk.END)
    scale_percent_entry.insert(0, str(scale_percent.get()))

def update_entry_from_slider(event=None):
    update_scale_percent(scale_slider.get())
    process_image()

def update_slider_from_entry(event=None):
    try:
        value = int(scale_percent_entry.get())
        if 1 <= value <= 600:
            scale_slider.set(value)
            process_image()
    except ValueError:
        pass

def play_sound():
    # Replace 'sound.mp3' with the path to your sound file
    playsound('sound.mp3')

# Create the main window
root = tk.Tk()
root.title("Image to Coloring Book Converter")
root.geometry("1200x700")
root.configure(bg="#333333")  # Dark background color

# Style configuration
style = ttk.Style()
style.theme_use("clam")

style.configure('TButton', font=('Arial', 12), padding=10, background="#555555", foreground="#ffffff")
style.configure('TLabel', font=('Arial', 12), background="#333333", foreground="#ffffff")
style.configure('TEntry', font=('Arial', 12), padding=5, fieldbackground="#555555", foreground="#ffffff")
style.configure('TFrame', background="#333333")

# Canvas dimensions
canvas_width = 500
canvas_height = 500

# Create and place the widgets
frame_buttons = ttk.Frame(root, padding="10 10 10 10")
frame_buttons.grid(row=0, column=0, columnspan=6)

open_button = ttk.Button(frame_buttons, text="Open Image", command=open_image)
open_button.grid(row=0, column=0, padx=10, pady=10)

save_button = ttk.Button(frame_buttons, text="Save Image", command=save_image)
save_button.grid(row=0, column=1, padx=10, pady=10)

process_button = ttk.Button(frame_buttons, text="Process Image", command=process_image)
process_button.grid(row=0, column=2, padx=10, pady=10)

copy_button = ttk.Button(frame_buttons, text="Copy to Clipboard", command=copy_processed_image_to_clipboard)
copy_button.grid(row=0, column=3, padx=10, pady=10)

scale_percent = tk.IntVar(value=200)
scale_label = ttk.Label(frame_buttons, text="Scale Percent:")
scale_label.grid(row=0, column=4, padx=10, pady=10)
scale_slider = ttk.Scale(frame_buttons, from_=1, to=600, orient='horizontal', variable=scale_percent, command=update_scale_percent)
scale_slider.grid(row=0, column=5, padx=10, pady=10)
scale_slider.bind("<ButtonRelease-1>", update_entry_from_slider)

scale_percent_entry = ttk.Entry(frame_buttons, width=5)
scale_percent_entry.grid(row=0, column=6, padx=10, pady=10)
scale_percent_entry.insert(0, "200")
scale_percent_entry.bind("<Return>", update_slider_from_entry)

frame_images = ttk.Frame(root, padding="10 10 10 10")
frame_images.grid(row=1, column=0, columnspan=4)

canvas_original = tk.Canvas(frame_images, width=canvas_width, height=canvas_height, bg="#ffffff", bd=2, relief="groove")
canvas_original.grid(row=1, column=0, padx=10, pady=10)

canvas_processed = tk.Canvas(frame_images, width=canvas_width, height=canvas_height, bg="#ffffff", bd=2, relief="groove")
canvas_processed.grid(row=1, column=1, padx=10, pady=10)

original_image = None
processed_image = None
original_image_tk = None
processed_image_tk = None
current_image_path = None

# Start the Tkinter event loop
root.mainloop()
