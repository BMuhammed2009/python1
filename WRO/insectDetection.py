"""import cv2
import numpy as np
from tkinter import *
from PIL import Image, ImageTk
import threading
import time
import os

mask_threshold = 800  # Set a threshold for motion detection sensitivity

""
    if you wanna use default camera,  write 0
    if you wanna use external camera, write 1
            (if '1' doesnt work try to use 2 )
""
camera_id = 0

class InsectDetectorApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.save_folder = "save"  # Folder to save detected images
        if not os.path.exists(self.save_folder):
            os.makedirs(self.save_folder)

        self.cap = cv2.VideoCapture(camera_id)  # Start video capture
        self.canvas = Canvas(window, width=self.cap.get(cv2.CAP_PROP_FRAME_WIDTH), height=self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.canvas.pack()

        self.btn_start = Button(window, text="Start", width=10, command=self.start_detection)
        self.btn_start.pack(anchor=CENTER, expand=True)

        self.btn_stop = Button(window, text="Stop", width=10, state=DISABLED, command=self.stop_detection)
        self.btn_stop.pack(anchor=CENTER, expand=True)

        self.scroll_frame = Frame(window)
        self.scroll_frame.pack(fill=BOTH, expand=True)
        self.canvas_gallery = Canvas(self.scroll_frame, bg='grey', height=200)
        self.scrollbar_gallery = Scrollbar(self.scroll_frame, orient="horizontal", command=self.canvas_gallery.xview)
        self.canvas_gallery.configure(xscrollcommand=self.scrollbar_gallery.set)
        self.scrollbar_gallery.pack(side=BOTTOM, fill=X)
        self.canvas_gallery.pack(side=LEFT, fill=BOTH, expand=True)
        self.frame_images = Frame(self.canvas_gallery, bg='grey')
        self.canvas_frame = self.canvas_gallery.create_window((0, 0), window=self.frame_images, anchor="nw")

        self.canvas_gallery.bind("<Configure>", self.on_canvas_configure)
        self.frame_images.bind("<Configure>", lambda e: self.canvas_gallery.configure(scrollregion=self.canvas_gallery.bbox("all")))

        self.background_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50, detectShadows=True)
        self.detect = False
        self.detection_thread = None

        self.update_video()
        self.window.mainloop()

    def on_canvas_configure(self, event):
        self.canvas_gallery.itemconfig(self.canvas_frame, width=event.width)

    def update_video(self):
        ret, frame = self.cap.read()
        if ret:
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            self.canvas.create_image(0, 0, image=self.photo, anchor=NW)
        self.window.after(10, self.update_video)

    def start_detection(self):
        self.detect = True
        self.btn_start.config(state=DISABLED)
        self.btn_stop.config(state=NORMAL)
        self.detection_thread = threading.Thread(target=self.detect_motion)
        self.detection_thread.start()

    def stop_detection(self):
        self.detect = False
        self.btn_start.config(state=NORMAL)
        self.btn_stop.config(state=DISABLED)
        self.detection_thread.join()
        self.refresh_gallery()

    def detect_motion(self):
        while self.detect:
            ret, frame = self.cap.read()
            if ret:
                motion_mask = self.background_subtractor.apply(frame)
                if cv2.countNonZero(motion_mask) > mask_threshold:
                    timestamp = int(time.time())
                    img_name = f"{self.save_folder}/detected_insect_{timestamp}.jpg"
                    cv2.imwrite(img_name, frame)

    def refresh_gallery(self):
        for widget in self.frame_images.winfo_children():
            widget.destroy()
        images = sorted(os.listdir(self.save_folder))
        for index, img_file in enumerate(images):
            if img_file.endswith('.jpg'):
                row = index // 5
                col = index % 5
                self.update_gallery(f"{self.save_folder}/{img_file}", row, col)

    def update_gallery(self, img_path, row, col):
        img = Image.open(img_path)
        img.thumbnail((100, 100))
        img = ImageTk.PhotoImage(img)
        panel = Label(self.frame_images, image=img)
        panel.image = img
        panel.grid(row=row, column=col, padx=10, pady=10)
        panel.bind('<Button-1>', lambda e, path=img_path: self.open_full_image(path))

    def open_full_image(self, path):
        top = Toplevel(self.window)
        img = Image.open(path)
        photo = ImageTk.PhotoImage(img)
        img_label = Label(top, image=photo)
        img_label.image = photo
        img_label.pack()

        btn_delete = Button(top, text="Delete Image", command=lambda: self.delete_image(path, top))
        btn_delete.pack()

    def delete_image(self, path, top):
        os.remove(path)
        top.destroy()
        self.refresh_gallery()

if __name__ == "__main__":
    root = Tk()
    InsectDetectorApp(root, "Insect Detector App")
"""
import cv2
import numpy as np
from tkinter import Tk, Canvas, Frame, Button, Label, Scrollbar, BOTH, LEFT, RIGHT, Y, X, CENTER, DISABLED, NORMAL, NW, Toplevel
from PIL import Image, ImageTk
import threading
import time
import os

# Set a threshold for motion detection sensitivity
# Hərəkəti aşkar etmə həssaslığı üçün bir hədd təyin edin
mask_threshold = 800

# Use default camera (0) or external camera (1 or 2)
# Default kameranı (0) və ya xarici kameranı (1 və ya 2) istifadə edin
camera_id = 1

class InsectDetectorApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.window.configure(bg="white")
        
        # Create a folder to save detected images
        # Aşkar edilən şəkilləri saxlamaq üçün bir qovluq yaradın
        self.save_folder = "save"
        if not os.path.exists(self.save_folder):
            os.makedirs(self.save_folder)

        # Start video capture
        # Video çəkməyi başlayın
        self.cap = cv2.VideoCapture(camera_id)
        self.canvas = Canvas(window, width=self.cap.get(cv2.CAP_PROP_FRAME_WIDTH), height=self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.canvas.pack()

        # Button Frame for alignment
        # Düzgünlük üçün düymə çərçivəsi
        self.btn_frame = Frame(window, bg="white")
        self.btn_frame.pack(anchor=CENTER, expand=True)

        # Start button - green
        # Start düyməsi - yaşıl
        self.btn_start = Button(self.btn_frame, text="Start", width=10, bg="green", fg="white", command=self.start_detection)
        self.btn_start.grid(row=0, column=0, padx=10, pady=10)

        # Stop button - yellow
        # Stop düyməsi - sarı
        self.btn_stop = Button(self.btn_frame, text="Stop", width=10, bg="yellow", fg="black", state=DISABLED, command=self.stop_detection)
        self.btn_stop.grid(row=0, column=1, padx=10, pady=10)

        # Delete All button - red
        # Bütün şəkilləri silmək üçün düymə - qırmızı
        self.btn_delete_all = Button(self.btn_frame, text="Delete All", width=10, bg="red", fg="white", command=self.delete_all_images)
        self.btn_delete_all.grid(row=0, column=2, padx=10, pady=10)

        # Frame and scrollbar for the gallery
        # Qalereya üçün çərçivə və scrollbar
        self.scroll_frame = Frame(window, bg="white")
        self.scroll_frame.pack(fill=BOTH, expand=True)

        # Configure vertical scrollbar
        # Şaquli scrollbarı konfiqurasiya edin
        self.canvas_gallery = Canvas(self.scroll_frame, bg='white')
        self.scrollbar_gallery = Scrollbar(self.scroll_frame, orient="vertical", command=self.canvas_gallery.yview)
        self.canvas_gallery.configure(yscrollcommand=self.scrollbar_gallery.set)
        self.scrollbar_gallery.pack(side=RIGHT, fill=Y)
        self.canvas_gallery.pack(side=LEFT, fill=BOTH, expand=True)

        # Create a frame to hold images, which will be centered
        # Şəkilləri saxlamaq üçün çərçivə yaradın və bu çərçivə mərkəzə yerləşdiriləcək
        self.frame_images_outer = Frame(self.canvas_gallery, bg="white")
        self.frame_images_outer.pack(anchor=CENTER, expand=True)

        self.frame_images = Frame(self.frame_images_outer, bg="white")
        self.frame_images.pack(anchor=CENTER, expand=True)

        self.canvas_frame = self.canvas_gallery.create_window((0, 0), window=self.frame_images_outer, anchor="center")

        self.canvas_gallery.bind("<Configure>", self.on_canvas_configure)
        self.frame_images.bind("<Configure>", lambda e: self.canvas_gallery.configure(scrollregion=self.canvas_gallery.bbox("all")))

        # Background subtractor for motion detection
        # Hərəkətin aşkar edilməsi üçün fon çıxarıcı
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50, detectShadows=True)
        self.detect = False
        self.detection_thread = None

        # Start video update loop
        # Video yeniləmə döngüsünə başlayın
        self.update_video()
        self.window.mainloop()

    def on_canvas_configure(self, event):
        # Adjust the canvas frame size when window is resized
        # Pəncərə ölçüsü dəyişdikdə kətan çərçivəsinin ölçüsünü tənzimləyin
        self.canvas_gallery.itemconfig(self.canvas_frame, width=event.width)

    def update_video(self):
        # Update the video frame
        # Video kadrını yeniləyin
        ret, frame = self.cap.read()
        if ret:
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            self.canvas.create_image(0, 0, image=self.photo, anchor=NW)
        self.window.after(10, self.update_video)

    def start_detection(self):
        # Start the motion detection
        # Hərəkət aşkar etməyi başlayın
        self.detect = True
        self.btn_start.config(state=DISABLED)
        self.btn_stop.config(state=NORMAL)
        self.detection_thread = threading.Thread(target=self.detect_motion)
        self.detection_thread.start()

    def stop_detection(self):
        # Stop the motion detection
        # Hərəkət aşkar etməyi dayandırın
        self.detect = False
        self.btn_start.config(state=NORMAL)
        self.btn_stop.config(state=DISABLED)
        self.detection_thread.join()
        self.refresh_gallery()

    def detect_motion(self):
        # Motion detection logic
        # Hərəkət aşkar etmə məntiqi
        while self.detect:
            ret, frame = self.cap.read()
            if ret:
                motion_mask = self.background_subtractor.apply(frame)
                if cv2.countNonZero(motion_mask) > mask_threshold:
                    timestamp = int(time.time())
                    img_name = f"{self.save_folder}/detected_insect_{timestamp}.jpg"
                    cv2.imwrite(img_name, frame)

    def refresh_gallery(self):
        # Refresh the gallery with saved images
        # Qalereyanı saxlanılan şəkillərlə yeniləyin
        for widget in self.frame_images.winfo_children():
            widget.destroy()
        images = sorted(os.listdir(self.save_folder))
        max_columns = 5  # Number of images per row / Hər sıra üçün şəkil sayı
        for index, img_file in enumerate(images):
            if img_file.endswith('.jpg'):
                row = index // max_columns
                col = index % max_columns
                self.update_gallery(f"{self.save_folder}/{img_file}", row, col)

    def update_gallery(self, img_path, row, col):
        # Update the gallery with a new image
        # Qalereyanı yeni bir şəkillə yeniləyin
        img = Image.open(img_path)
        img.thumbnail((100, 100))
        img = ImageTk.PhotoImage(img)
        panel = Label(self.frame_images, image=img, bg="white")
        panel.image = img
        panel.grid(row=row, column=col, padx=10, pady=10)
        panel.bind('<Button-1>', lambda e, path=img_path: self.open_full_image(path))

    def open_full_image(self, path):
        # Open the selected image in a new window
        # Seçilən şəkili yeni bir pəncərədə açın
        top = Toplevel(self.window)
        top.configure(bg="white")
        img = Image.open(path)
        photo = ImageTk.PhotoImage(img)
        img_label = Label(top, image=photo, bg="white")
        img_label.image = photo
        img_label.pack()

        btn_delete = Button(top, text="Delete Image", command=lambda: self.delete_image(path, top))
        btn_delete.pack()

    def delete_image(self, path, top):
        # Delete a specific image
        # Müəyyən bir şəkili silin
        os.remove(path)
        top.destroy()
        self.refresh_gallery()

    def delete_all_images(self):
        # Delete all images from the gallery
        # Qalereyadan bütün şəkilləri silin
        for img_file in os.listdir(self.save_folder):
            file_path = os.path.join(self.save_folder, img_file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        self.refresh_gallery()

if __name__ == "__main__":
    root = Tk()
    InsectDetectorApp(root, "Insect Detector App")
