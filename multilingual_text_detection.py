import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
from PIL import Image, ImageTk
import easyocr
import numpy as np
from googletrans import Translator
import threading
from google.cloud import translate_v2 as translate
import os
# Set Google Cloud credentials (replace with your actual path)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"D:\MP_NEW\textrecognitontranslation-d9b93d1d6990.json"

# Initialize the translator
translator = translate.Client()


# Global Variables
image_path = None
image_display = None
detected_text = {"kannada": "", "english": ""}
current_language = None

# GUI Setup
root = ctk.CTk()
root.geometry("950x800")
root.title("Text Detection & Translation")

# Configure grid layout
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=0)  # Top controls
root.rowconfigure(1, weight=1)  # Main content
root.rowconfigure(2, weight=0)  # Bottom controls

# Top Frame
top_frame = ctk.CTkFrame(root)
top_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
top_frame.columnconfigure(0, weight=1)
top_frame.columnconfigure(1, weight=0)

# App Title
title_label = ctk.CTkLabel(top_frame, text="Multilingual OCR & Translation", font=("Arial", 20, "bold"))
title_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)

# Theme Switch
theme_switch = ctk.CTkSwitch(top_frame, text="🌙 Dark Mode")
theme_switch.grid(row=0, column=1, sticky="e", padx=10, pady=10)

# Main Content Frame
main_frame = ctk.CTkFrame(root)
main_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
main_frame.columnconfigure(0, weight=1)
main_frame.columnconfigure(1, weight=1)
main_frame.rowconfigure(0, weight=0)
main_frame.rowconfigure(1, weight=1)

# Image Section
image_section = ctk.CTkFrame(main_frame, corner_radius=15)
image_section.grid(row=0, rowspan=2, column=0, sticky="nsew", padx=10, pady=10)
image_section.columnconfigure(0, weight=1)
image_section.rowconfigure(0, weight=0)
image_section.rowconfigure(1, weight=1)
image_section.rowconfigure(2, weight=0)

# Image Preview Label
preview_label = ctk.CTkLabel(image_section, text="", font=("Arial", 14))
preview_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 0))

# Image Display
image_label = ctk.CTkLabel(image_section, text="No image selected", width=450, height=450, fg_color="#333333")
image_label.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

# Image Controls
image_controls = ctk.CTkFrame(image_section, corner_radius=10, fg_color="transparent")
image_controls.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
image_controls.columnconfigure((0, 1), weight=1)

# Text Section
text_section = ctk.CTkFrame(main_frame, corner_radius=15)
text_section.grid(row=0, rowspan=2, column=1, sticky="nsew", padx=10, pady=10)
text_section.columnconfigure(0, weight=1)
text_section.rowconfigure(0, weight=0)
text_section.rowconfigure(1, weight=0)
text_section.rowconfigure(2, weight=1)
text_section.rowconfigure(3, weight=0)

# Text Controls Header
text_header = ctk.CTkFrame(text_section, corner_radius=10, fg_color="transparent")
text_header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
text_header.columnconfigure(0, weight=1)
text_header.columnconfigure(1, weight=0)

# Text Output Label
output_label = ctk.CTkLabel(text_header, text="Detected Text:", font=("Arial", 14))
output_label.grid(row=0, column=0, sticky="w")

# Language Indicator
language_indicator = ctk.CTkLabel(text_header, text="No text detected", text_color="gray")
language_indicator.grid(row=0, column=1, sticky="e")

# Translation Controls
translation_controls = ctk.CTkFrame(text_section, corner_radius=10, fg_color="transparent")
translation_controls.grid(row=1, column=0, sticky="ew", padx=10, pady=(5, 10))
translation_controls.columnconfigure((0, 1), weight=1)

# Translate to English Button
translate_to_en_button = ctk.CTkButton(
    translation_controls,
    text="🇬🇧 Translate to English",
    fg_color="#22A7F0",
    hover_color="#1B86C1",
    state="disabled"
)
translate_to_en_button.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

# Translate to Kannada Button
translate_to_kn_button = ctk.CTkButton(
    translation_controls,
    text="🇮🇳 Translate to Kannada",
    fg_color="#FF5C5C",
    hover_color="#D64545",
    state="disabled"
)
translate_to_kn_button.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

# Text Output
text_output = ctk.CTkTextbox(text_section, width=400, height=400, corner_radius=10)
text_output.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

# Text Utility Controls
text_utils = ctk.CTkFrame(text_section, corner_radius=10, fg_color="transparent")
text_utils.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
text_utils.columnconfigure((0, 1), weight=1)

# Copy Text Button
copy_button = ctk.CTkButton(text_utils, text="📋 Copy Text", fg_color="#4CAF50", hover_color="#388E3C")
copy_button.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

# Save Text Button
save_button = ctk.CTkButton(text_utils, text="💾 Save Text", fg_color="#9C27B0", hover_color="#7B1FA2")
save_button.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

# Bottom Controls
bottom_frame = ctk.CTkFrame(root, corner_radius=15)
bottom_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
bottom_frame.columnconfigure(0, weight=1)
bottom_frame.columnconfigure(1, weight=0)

# Progress Bar
progress_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
progress_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
progress_frame.columnconfigure(0, weight=1)

progress_bar = ctk.CTkProgressBar(progress_frame)
progress_bar.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
progress_bar.set(0)  # Initialize at 0

status_label = ctk.CTkLabel(progress_frame, text="Ready", anchor="w")
status_label.grid(row=1, column=0, sticky="ew", padx=5)

# Footer
footer_label = ctk.CTkLabel(bottom_frame, text="Developed by team 078", text_color="#AAAAAA", font=("Arial", 12))
footer_label.grid(row=0, column=1, sticky="e", padx=10, pady=10)

# Select Image Button
select_button = ctk.CTkButton(image_controls, text="📂 Select Image", fg_color="#FF5C5C", hover_color="#D64545")
select_button.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

# OCR Button
ocr_button = ctk.CTkButton(image_controls, text="🔍 Run OCR", fg_color="#22A7F0", hover_color="#1B86C1",
                           state="disabled")
ocr_button.grid(row=0, column=1, sticky="ew", padx=5, pady=5)


# Function Definitions
def toggle_theme():
    """Switch between dark and light mode."""
    if theme_switch.get() == 1:
        ctk.set_appearance_mode("dark")
    else:
        ctk.set_appearance_mode("light")


def select_image():
    """Select image from the file system and display it."""
    global image_path, image_display
    image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg")])
    if image_path:
        image = cv2.imread(image_path)
        image_display = image.copy()  # Save original for processing
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)

        # Resize for display
        image = image.resize((450, 450), Image.Resampling.LANCZOS)
        image_tk = ImageTk.PhotoImage(image)
        image_label.configure(image=image_tk)
        image_label.image = image_tk

        # Enable OCR button when image is selected
        ocr_button.configure(state="normal")

        # Show image preview label
        preview_label.configure(text="Image Preview:")


def update_progress(value):
    """Updates the progress bar and status label."""
    progress_bar.set(value)
    if value < 1.0:
        status_label.configure(text="Processing...")
    else:
        status_label.configure(text="Processing complete")


def run_ocr_thread():
    """Run OCR in a separate thread to keep UI responsive."""
    threading.Thread(target=run_ocr).start()


def run_ocr():
    """Runs OCR and displays the best result."""
    global detected_text, current_language

    if not image_path:
        messagebox.showinfo("Info", "Please select an image first.")
        return

    # Update UI to show processing
    text_output.delete(1.0, tk.END)  # Clear previous output
    update_progress(0.1)
    text_output.insert(tk.END, "Processing image...\n")

    try:
        # Load Image
        image = cv2.imread(image_path)
        if image is None:
            messagebox.showerror("Error", "Failed to load image.")
            return

        # 🟢 Kannada OCR (EasyOCR)
        update_progress(0.3)
        text_output.delete(1.0, tk.END)
        text_output.insert(tk.END, "Detecting Kannada text...\n")
        reader_kn = easyocr.Reader(['kn'], gpu=False)
        results_kn = reader_kn.readtext(image_path)

        kannada_text = ""
        for _, text, confidence in results_kn:
            if confidence > 0.2:  # Consider only high confidence text
                kannada_text += f"{text} "

        detected_text["kannada"] = kannada_text.strip()

        # 🔵 English OCR (EasyOCR)
        update_progress(0.6)
        text_output.delete(1.0, tk.END)
        text_output.insert(tk.END, "Detecting English text...\n")
        reader_en = easyocr.Reader(['en'], gpu=False)
        results_en = reader_en.readtext(image_path)

        english_text = ""
        for _, text, confidence in results_en:
            if confidence > 0.1:  # Use lower threshold for English
                english_text += f"{text} "

        detected_text["english"] = english_text.strip()

        # Select the best OCR result
        if detected_text["kannada"]:
            current_language = "kannada"
            final_text = detected_text["kannada"]
        elif detected_text["english"]:
            current_language = "english"
            final_text = detected_text["english"]
        else:
            current_language = None
            final_text = "No text detected."

        # Clear and display the best result
        text_output.delete(1.0, tk.END)
        text_output.insert(tk.END, final_text)

        # Enable translation buttons if text was detected
        if current_language:
            if current_language == "kannada":
                translate_to_en_button.configure(state="normal")
                translate_to_kn_button.configure(state="disabled")
            else:
                translate_to_kn_button.configure(state="normal")
                translate_to_en_button.configure(state="disabled")
        else:
            translate_to_en_button.configure(state="disabled")
            translate_to_kn_button.configure(state="disabled")

        # Debugging Output (print to console)
        print(f"Kannada Detected: {detected_text['kannada']}")
        print(f"English Detected: {detected_text['english']}")

        # Update progress to complete
        update_progress(1.0)

        # Update language indicator
        if current_language:
            language_indicator.configure(
                text=f"Detected: {'Kannada' if current_language == 'kannada' else 'English'}",
                text_color=("#FF5C5C" if current_language == "kannada" else "#22A7F0")
            )
        else:
            language_indicator.configure(text="No text detected", text_color="gray")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{e}")
        update_progress(0)
        status_label.configure(text="Error occurred")


def translate_text(target_language):
    """Translate text between Kannada and English using Google Cloud Translation API."""
    global current_language, detected_text

    if not current_language:
        messagebox.showinfo("Info", "No text detected to translate.")
        return

    try:
        update_progress(0.5)
        status_label.configure(text="Translating...")

        if target_language == "english" and current_language == "kannada":
            # Translate Kannada to English
            translated_text = translator.translate(detected_text["kannada"], source_language='kn', target_language='en')['translatedText']
            detected_text["english"] = translated_text
            current_language = "english"

        elif target_language == "kannada" and current_language == "english":
            # Translate English to Kannada
            translated_text = translator.translate(detected_text["english"], source_language='en', target_language='kn')['translatedText']
            detected_text["kannada"] = translated_text
            current_language = "kannada"

        # Update UI
        text_output.delete(1.0, tk.END)
        text_output.insert(tk.END, translated_text)

        # Toggle translation buttons
        translate_to_en_button.configure(state="disabled" if current_language == "english" else "normal")
        translate_to_kn_button.configure(state="disabled" if current_language == "kannada" else "normal")
        language_indicator.configure(text=f"Detected: {'English' if current_language == 'english' else 'Kannada'}",
                                     text_color="#22A7F0" if current_language == "english" else "#FF5C5C")

        # Update progress to complete
        update_progress(1.0)
        status_label.configure(text="Translation complete")

    except Exception as e:
        messagebox.showerror("Error", f"Translation failed:\n{e}")
        update_progress(0)
        status_label.configure(text="Error occurred")


# Bind Functions to Buttons
theme_switch.configure(command=toggle_theme)
select_button.configure(command=select_image)
ocr_button.configure(command=run_ocr_thread)
translate_to_en_button.configure(command=lambda: translate_text("english"))
translate_to_kn_button.configure(command=lambda: translate_text("kannada"))
copy_button.configure(command=lambda: root.clipboard_clear() or root.clipboard_append(
    text_output.get(1.0, tk.END).strip()) or root.update())
save_button.configure(
    command=lambda: filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")]) and open(
        filedialog.asksaveasfilename(), "w").write(text_output.get(1.0, tk.END).strip()))

# Start the GUI event loop
root.mainloop()

# Translate English to Kannada