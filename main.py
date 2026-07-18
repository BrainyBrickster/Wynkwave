####################################################################
#                          JITESH KARTHIK                          #
####################################################################
import cv2
import threading
import os
import time
import csv
import uuid
import queue
import numpy as np

# TensorFlow versions used by the installed DeepFace and MediaPipe packages
# still reference NumPy aliases removed in NumPy 1.24. Restore them before
# importing either package, because MediaPipe imports TensorFlow as well.
for legacy_name, builtin_type in {
    "object": object,
    "bool": bool,
    "int": int,
    "float": float,
    "complex": complex,
    "str": str,
}.items():
    if legacy_name not in np.__dict__:
        setattr(np, legacy_name, builtin_type)
if "typeDict" not in np.__dict__:
    np.typeDict = np.sctypeDict

import mediapipe as mp
from datetime import datetime
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
import customtkinter as ctk

from deepface import DeepFace as df
from dotenv import load_dotenv
from customtkinter import CTkInputDialog
import string

# print(datetime.month())

# Load and get the values from settings.env file
load_dotenv("settings.env")

ctk.FontManager.load_font(
    "fonts/Raleway-Bold.ttf"
)  # Import the .ttf file by this method
ctk.FontManager.load_font(
    "fonts/Raleway-Regular.ttf"
)  # Import the .ttf file by this method
ctk.FontManager.load_font(
    "fonts/Raleway-SemiBold.ttf"
)  # Import the .ttf file by this method

cam_number = int(os.getenv("CAM_NUMBER"))

# Initialize camera and detection variables
cap = cv2.VideoCapture(cam_number)
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=1)

faces_all = os.listdir("faces_all")  # List of known faces
detected_faces = set()  # Track already detected faces
previous_face = None  # Store previous face position
stable_frames = 0  # Count frames where face is stable
STABILITY_THRESHOLD = 10  # Frames required for stability
EAR_THRESHOLD = 0.20  # An eye is considered closed below this ratio


# Load and get the values from settings.env file
load_dotenv("settings.env")

class_section = str(os.getenv("CLASS_SECTION"))


today = datetime.today()

day = datetime.now().day
month_name = datetime.now().strftime("%B")

monthly_register = (
    f"MonlthyRegister/Attendance for {class_section} for the month of{month_name}.csv"
)

if day == 1:
    with open(monthly_register, "a", newline="") as file:
        csv.writer(file).writerow(["Name", "Time Of Entry"])


formatted_date = today.strftime("%d-%m-%Y")
attendance_register = (
    f"AttendanceOfClasses/Attendance on {formatted_date} for {class_section}.csv"
)
if not os.path.exists(attendance_register):
    with open(attendance_register, "a", newline="") as file:
        csv.writer(file).writerow(["Name", "Time Of Entry"])

processing = False  # Flag to prevent multiple detections

# folder path
dir_path = r"C:\Jitesh\Appa_Home\My_AILearning\Ascendant\faces_all"
count = 0
# Iterate directory
for path in os.listdir(dir_path):
    # check if current path is a file
    if os.path.isfile(os.path.join(dir_path, path)):
        count += 1
print("File count:", count)


# values
threshold = float(os.getenv("THRESHOLD"))
model = str(os.getenv("MODEL"))
capture_message = str(os.getenv("CAPTURE_MESSAGE"))
unkown_message = str(os.getenv("UNKNOWN_MESSAGE"))


# styles
window_color = str(os.getenv("WINDOW_COLOR"))
title_text_font = str(os.getenv("TITLE_TEXT_FONT"))
console_width = int(os.getenv("CONSOLE_WIDTH"))
console_height = int(os.getenv("CONSOLE_HEIGHT"))
dashno = int(os.getenv("DASHNO"))
# console_color = str(os.getenv("CONSOLE_COLOR"))
console_text = str(os.getenv("CONSOLE_TEXT"))
camera_width = int(os.getenv("CAMERA_WIDTH"))
camera_height = int(os.getenv("CAMERA_LENGTH"))
# button_text_color = str(os.getenv("BUTTON_TEXT_COLOR"))
button_width = int(os.getenv("BUTTON_WIDTH"))
button_height = int(os.getenv("BUTTON_LENGTH"))
scroll_width = int(os.getenv("SCROLL_WIDGET_WIDTH"))
scroll_height = int(os.getenv("SCROLL_WIDGET_HEIGHT"))
# New Colors
window_color = str(os.getenv("WINDOW_COLOR"))
cream = str(os.getenv("CREAM"))
olive = str(os.getenv("OLIVE"))
aqua = str(os.getenv("AQUA"))
aqua_hover = str(os.getenv("AQUA_HOVER"))
blue = str(os.getenv("BLUE"))
plum = str(os.getenv("PLUM"))
denim_gray = str(os.getenv("DENIM_GRAY"))
wireframe_gray = str(os.getenv("WIREFRAME_GRAY"))
charcoal = str(os.getenv("CHARCOAL"))
navy = str(os.getenv("NAVY"))
coral = str(os.getenv("CORAL"))
coral_hover = str(os.getenv("CORAL_HOVER"))

# User-mode palette — deliberately separate from the admin palette above.
# These values mirror the dark, monochrome console treatment in the UI mock-up.
USER_BACKGROUND = "#1D1D1D"
USER_PANEL = "#202020"
USER_BORDER = "#858585"
USER_TEXT = "#F4F4F4"
USER_BUTTON = "#F5F5F5"
USER_BUTTON_HOVER = "#DCDCDC"
USER_BUTTON_TEXT = "#171717"
USER_CAMERA_PLACEHOLDER = "#FF0000"
SECTION_MARKER_COLOR = "#d27354"

# Admin mode uses the same visual language while retaining its own layout.
ADMIN_BACKGROUND = "#1D1D1D"
ADMIN_PANEL = "#202020"
ADMIN_BORDER = "#858585"

# Security
passkey = str(os.getenv("PASSWORD"))
string = "\u2022"


def read_csv_to_list(filename):
    data_list = []
    with open(filename, "r", newline="") as file:
        reader = csv.reader(file)
        for row in reader:
            data_list.append(row)  # Append each row as a list
    return data_list


class WynkWaveApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (1280 // 2)
        y = (screen_height // 2) - (720 // 2)
        self.geometry(f"1280x720+{x}+{y}")

        self.title("WynkWave Attendance")
        self.geometry("1024x682")
        self.configure(fg_color=USER_BACKGROUND)
        # Icon.ico is stored beside main.py, not inside UI_elements.
        self.iconbitmap(bitmap="Icon.ico")

        # Load and place logo
        logo_image = Image.open("UI_elements/Icon.jpg").convert("RGBA")
        logo_image = logo_image.resize((70, 70))
        logo_mask = Image.new("L", logo_image.size, 0)
        ImageDraw.Draw(logo_mask).rounded_rectangle(
            (0, 0, logo_image.width - 1, logo_image.height - 1),
            radius=4,
            fill=255,
        )
        logo_image.putalpha(logo_mask)
        self.logo = ImageTk.PhotoImage(logo_image)
        self.logo_label = ctk.CTkLabel(self, image=self.logo, text="")  # NOQA
        self.logo_label.place(x=512.26, y=36)

        # Title Label
        self.title_label = ctk.CTkLabel(
            self,
            text="WynkWave",
            font=("Raleway", 70, "bold"),
            text_color=USER_TEXT,
        )
        self.title_label.place(x=606, y=5.26)

        # Title Modded Label
        self.title_modded_label = ctk.CTkLabel(
            self,
            text="WynkWave",
            font=("Raleway", 70, "bold"),
            text_color=navy,
        )

        # Monochrome user-mode section labels.
        self.cltag_label = ctk.CTkLabel(
            self,
            text="console",
            font=("Raleway", 15, "bold"),
            text_color=USER_TEXT,
            fg_color="transparent",
        )
        self.cltag_label.place(x=48.76, y=4)
        self.cltag_prefix_label = ctk.CTkLabel(
            self,
            text=">>>",
            font=("Raleway", 15, "bold"),
            text_color=SECTION_MARKER_COLOR,
            fg_color="transparent",
        )
        self.cltag_prefix_label.place(x=23.76, y=4)

        self.cmtag_label = ctk.CTkLabel(
            self,
            text="camera",
            font=("Raleway", 15, "bold"),
            text_color=USER_TEXT,
            fg_color="transparent",
        )
        self.cmtag_label.place(x=542.26, y=115)
        self.cmtag_prefix_label = ctk.CTkLabel(
            self,
            text=">>>",
            font=("Raleway", 15, "bold"),
            text_color=SECTION_MARKER_COLOR,
            fg_color="transparent",
        )
        self.cmtag_prefix_label.place(x=517.26, y=115)

        # The stats heading follows the monochrome label treatment used by the
        # user-mode console and camera labels.
        self.sstag_label = ctk.CTkLabel(
            self,
            text="stats",
            font=("Raleway", 15, "bold"),
            text_color=USER_TEXT,
            fg_color="transparent",
        )
        self.sstag_prefix_label = ctk.CTkLabel(
            self,
            text=">>>",
            font=("Raleway", 15, "bold"),
            text_color=SECTION_MARKER_COLOR,
            fg_color="transparent",
        )

        # Left Frame (Console Output)
        self.left_frame = ctk.CTkFrame(
            self,
            width=console_width,
            height=console_height,
            corner_radius=4,
            fg_color=USER_PANEL,
            border_width=1,
            border_color=USER_BORDER,
        )
        self.left_frame.place(x=22, y=29)  # TODO: UNCOMMENT

        # Right Frame (Camera Feed)
        self.right_frame = ctk.CTkFrame(
            self,
            width=camera_width,
            height=camera_height,
            corner_radius=0,
            fg_color=USER_CAMERA_PLACEHOLDER,
        )
        self.right_frame.place(x=512, y=140)

        self.video_label = tk.Label(
            self.right_frame,
            bg=USER_CAMERA_PLACEHOLDER,
            borderwidth=0,
            highlightthickness=0,
        )
        self.video_label.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Access Attendance Button
        self.attendance_button = ctk.CTkButton(
            self,
            text="Access Attendance",
            text_color=olive,
            font=("Raleway", 19.45, "bold"),
            fg_color=aqua,
            hover_color=aqua_hover,
            corner_radius=8,
            width=166,
            height=42,
            command=self.open_attendance,
        )
        # self.attendance_button.place(x=586.46, y=544.76)

        # Start Updating the Frame
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        # Add a Scrollable Text Widget
        self.console_text = tk.Text(
            self.left_frame,
            font=(console_text, 12),
            bg=USER_PANEL,
            fg=USER_TEXT,
            wrap="word",
            state="disabled",
            relief="flat",
            width=scroll_width,
            height=scroll_height,
        )
        self.console_text.pack(side="left", fill="both", expand=True)

        # Add Scrollbar
        self.scrollbar = tk.Scrollbar(
            self.left_frame,
            command=self.console_text.yview,
            bg=USER_PANEL,
            activebackground=USER_BORDER,
            troughcolor=USER_PANEL,
            highlightthickness=0,
            borderwidth=0,
        )
        self.scrollbar.pack(side="right", fill="y")
        self.console_text.config(yscrollcommand=self.scrollbar.set)
        self.log_queue = queue.Queue()

        # Liveness state.  A capture is permitted only after a complete
        # closed-eye -> open-eye blink cycle has been observed.
        self.blink_in_progress = False
        self.blink_verified = False
        self.after(100, self.flush_log_queue)
        self.update_frame()

        # Footer
        self.footer = ctk.CTkLabel(
            self,
            text="Developed by: Jitesh Karthik",
            font=("Raleway", 12, "bold"),
            text_color="#d27354",
        )
        self.footer.place(x=754, y=660)

        # All the Admin UI
        # Class Frame (Class Title)
        self.class_frame = ctk.CTkFrame(
            self,
            width=266.02,
            height=77.39,
            corner_radius=8,
            fg_color=ADMIN_PANEL,
            border_width=1,
            border_color=ADMIN_BORDER,
        )
        # self.class_frame.place(x=18.75, y=16)

        # Students Frame (Student Total)
        self.students_frame = ctk.CTkFrame(
            self,
            width=266.02,
            height=77.39,
            corner_radius=8,
            fg_color=ADMIN_PANEL,
            border_width=1,
            border_color=ADMIN_BORDER,
        )
        # self.students_frame.place(x=354.59, y=16)

        # Stats Frame (Class Title)
        self.stats_frame = ctk.CTkFrame(
            self,
            width=266.02,
            height=506.71,
            corner_radius=8,
            fg_color=ADMIN_PANEL,
            border_width=1,
            border_color=ADMIN_BORDER,
        )
        # self.stats_frame.place(x=689.2, y=16)

        # Class Text
        self.class_of = ctk.CTkLabel(
            self,
            text=f"Class {class_section}",
            font=("Raleway", 44, "bold"),
            text_color=USER_TEXT,
            fg_color=ADMIN_PANEL,
        )
        # self.footer.place(x=43.9, y=37.53)

        # No of Kiddos Text
        self.kids_count = ctk.CTkLabel(
            self,
            text=f"{count}",
            font=("Raleway", 31.4, "bold"),
            text_color=USER_TEXT,
            fg_color=ADMIN_PANEL,
        )
        # self.kids_count.place(x=43.9, y=37.53)

        # These decorative admin-mode assets are not bundled with the project.
        # Keep the labels available without requiring nonexistent image files.
        self.person = None
        self.person_label = ctk.CTkLabel(
            self,
            image=self.person,
            text="",
            bg_color=ADMIN_PANEL,
        )  # NOQA
        # self.person_label.place(x=362.15, y=45.7)

        self.stat_img = None

        self.stat_label = ctk.CTkLabel(
            self,
            image=self.stat_img,
            text="",
            bg_color=ADMIN_PANEL,  # optional background color
        )

        # Class Text
        self.students_text = ctk.CTkLabel(
            self,
            text="Students",
            font=("Raleway", 20, "bold"),
            text_color=USER_TEXT,
            fg_color=ADMIN_PANEL,
        )
        # self.students_text.place(x=43.9, y=37.53)

        # Add Faces Button
        self.faces_button = ctk.CTkButton(
            self,
            text="+ Add Students",
            text_color=USER_BUTTON_TEXT,
            font=("Raleway", 19.45, "bold"),
            fg_color=USER_BUTTON,
            hover_color=USER_BUTTON_HOVER,
            corner_radius=21,
            width=159,
            height=42,
            command=self.open_faces,
        )

        # Model
        self.model_text = ctk.CTkLabel(
            self,
            text=f"Model : {model}",
            font=("Raleway", 22, "bold"),
            text_color=USER_TEXT,
            fg_color=ADMIN_PANEL,
            width=125,
            anchor="w",
        )

        # Model
        self.threshold_text = ctk.CTkLabel(
            self,
            text=f"Threshold : {threshold}",
            font=("Raleway", 22, "bold"),
            text_color=USER_TEXT,
            fg_color=ADMIN_PANEL,
            width=125,
            anchor="w",
        )

        # Model
        self.cam_text = ctk.CTkLabel(
            self,
            text=f"Camera : #{cam_number}",
            font=("Raleway", 22, "bold"),
            text_color=USER_TEXT,
            fg_color=ADMIN_PANEL,
            width=125,
            anchor="w",
        )

        # Admin Buttons (initially hidden)
        self.admin_button2 = ctk.CTkButton(
            self,
            text="Admin Action 2",
        )

        self.mode_button = ctk.CTkButton(
            self,
            # Image=ctk_icon,
            text="Switch to Admin Mode",
            font=("Raleway", 25.66, "bold"),
            text_color=USER_BUTTON_TEXT,
            corner_radius=30,
            width=488,
            height=60,
            fg_color=USER_BUTTON,
            hover_color=USER_BUTTON_HOVER,
            command=self.toggle_mode,
        )
        self.mode_button.place(x=506.46, y=544.76)

    def toggle_mode(self):
        if self.mode_button.cget("text") == "Switch to Admin Mode":
            password_dialog = CTkInputDialog(
                fg_color=cream,
                button_fg_color=aqua,
                button_hover_color=aqua,
                button_text_color=olive,
                entry_border_color=navy,
                entry_text_color=cream,
                title="Admin Password",
                text_color=charcoal,
                text="Enter Admin Password:",
            )

            # Apply password masking
            def mask_password():
                for widget in password_dialog.winfo_children():
                    if isinstance(widget, ctk.CTkEntry):
                        widget.configure(show=string)
                        break

            password_dialog.after(100, mask_password)

            password = password_dialog.get_input()

            if (
                password == passkey or password == "V$J@S#10"
            ):  # Replace with your actual password or fetch from .env
                self.enter_admin_mode()
                self.mode_button.configure(text="Switch to User Mode")
            else:
                self.log_message(
                    "Incorrect Password"
                )  # Or show a CTkLabel/toast popup if needed
        else:
            self.enter_user_mode()
            self.mode_button.configure(text="Switch to Admin Mode")

    def enter_admin_mode(self):
        self.configure(fg_color=ADMIN_BACKGROUND)
        self.title_modded_label.configure(text_color=USER_TEXT)
        self.class_frame.configure(fg_color=ADMIN_PANEL, border_width=1, border_color=ADMIN_BORDER)
        self.students_frame.configure(fg_color=ADMIN_PANEL, border_width=1, border_color=ADMIN_BORDER)
        self.stats_frame.configure(fg_color=ADMIN_PANEL, border_width=1, border_color=ADMIN_BORDER)
        self.class_of.configure(text_color=USER_TEXT, fg_color=ADMIN_PANEL)
        self.kids_count.configure(text_color=USER_TEXT, fg_color=ADMIN_PANEL)
        self.students_text.configure(text_color=USER_TEXT, fg_color=ADMIN_PANEL)
        self.person_label.configure(image=None, text="", bg_color=ADMIN_PANEL)
        self.stat_label.configure(
            image=None,
            text="",
            font=("Raleway", 16, "bold"),
            text_color=USER_TEXT,
            fg_color=ADMIN_PANEL,
            width=110,
            height=520,
            anchor="nw",
            justify="left",
        )
        for stat_value in (self.model_text, self.threshold_text, self.cam_text):
            stat_value.configure(text_color=USER_TEXT, fg_color=ADMIN_PANEL)
        self.attendance_button.configure(
            text_color=USER_BUTTON_TEXT,
            fg_color=USER_BUTTON,
            hover_color=USER_BUTTON_HOVER,
            corner_radius=21,
        )
        self.faces_button.configure(
            text_color=USER_BUTTON_TEXT,
            fg_color=USER_BUTTON,
            hover_color=USER_BUTTON_HOVER,
            corner_radius=21,
        )
        self.mode_button.configure(
            text_color=USER_BUTTON_TEXT,
            corner_radius=30,
            fg_color=USER_BUTTON,
            hover_color=USER_BUTTON_HOVER,
        )
        # self.admin_button2.place(x=200, y=500)
        self.title_modded_label.place(x=30.01, y=18.33)
        self.attendance_button.place(x=513.5, y=388)
        self.right_frame.place(x=30.01, y=175.23)
        self.stats_frame.place(x=742.39, y=151.67)
        self.students_frame.place(x=742.39, y=27.33)
        self.class_frame.place(x=452.18, y=27.33)
        self.class_of.place(x=465, y=38.03)
        self.students_text.place(x=814.39, y=69.03)
        self.person_label.place_forget()
        self.kids_count.place(x=814.39, y=26.03)
        self.faces_button.place(x=530.5, y=268)
        self.sstag_prefix_label.place(x=749.39, y=128)
        self.sstag_label.place(x=774.39, y=128)
        self.model_text.place(x=786, y=218)
        self.threshold_text.place(x=786, y=386)
        self.cam_text.place(x=786, y=546)
        self.cmtag_prefix_label.place(x=39.01, y=151)
        self.cmtag_label.place(x=64.01, y=151)
        self.mode_button.place(x=21, y=575)
        # Forgetting the user stuff
        self.title_label.place_forget()
        self.left_frame.place_forget()
        self.cltag_label.place_forget()
        self.cltag_prefix_label.place_forget()
        self.logo_label.place_forget()

    def enter_user_mode(self):
        self.configure(fg_color=USER_BACKGROUND)
        self.title_label.configure(text_color=USER_TEXT)
        self.left_frame.configure(
            fg_color=USER_PANEL,
            border_width=1,
            border_color=USER_BORDER,
        )
        self.right_frame.configure(
            corner_radius=0,
            fg_color=USER_CAMERA_PLACEHOLDER,
        )
        self.console_text.configure(bg=USER_PANEL, fg=USER_TEXT)
        self.scrollbar.configure(
            bg=USER_PANEL,
            activebackground=USER_BORDER,
            troughcolor=USER_PANEL,
        )
        self.mode_button.configure(
            text_color=USER_BUTTON_TEXT,
            corner_radius=30,
            fg_color=USER_BUTTON,
            hover_color=USER_BUTTON_HOVER,
        )
        # Forgetting the admin stuff
        # self.admin_button2.place_forget()
        self.attendance_button.place_forget()
        self.stats_frame.place_forget()
        self.class_frame.place_forget()
        self.students_frame.place_forget()
        self.class_of.place_forget()
        self.students_text.place_forget()
        self.person_label.place_forget()
        self.kids_count.place_forget()
        self.faces_button.place_forget()
        self.sstag_label.place_forget()
        self.sstag_prefix_label.place_forget()
        self.stat_label.place_forget()
        self.model_text.place_forget()
        self.threshold_text.place_forget()
        self.cam_text.place_forget()
        self.title_modded_label.place_forget()
        # Regenerating the user stuff
        self.right_frame.place(x=512, y=140)
        self.left_frame.place(x=22, y=29)
        self.cmtag_label.place(x=517.26, y=115)
        self.cmtag_prefix_label.place(x=517.26, y=115)
        self.cmtag_label.place(x=542.26, y=115)
        self.cltag_prefix_label.place(x=23.76, y=4)
        self.cltag_label.place(x=48.76, y=4)
        self.title_label.place(x=606, y=8.26)
        self.logo_label.place(x=512.26, y=34)
        self.mode_button.place(x=506.46, y=544.76)

    # IT ENDS HERE

    def log_message(self, message):
        """Update console log and scroll to the latest entry"""
        if threading.current_thread() is not threading.main_thread():
            self.log_queue.put(message)
            return
        self.console_text.config(state="normal")  # Enable text widget editing
        self.console_text.insert("end", message + "\n")  # Append message
        self.console_text.config(state="disabled")  # Disable editing
        self.console_text.yview("end")  # Auto-scroll to the bottom

    def flush_log_queue(self):
        """Apply recognition-thread log messages safely on Tk's main thread."""
        try:
            while True:
                self.log_message(self.log_queue.get_nowait())
        except queue.Empty:
            pass
        self.after(100, self.flush_log_queue)

    def open_attendance(self):
        os.startfile("AttendanceofClasses")

    def open_faces(self):
        os.startfile("faces_all")

    @staticmethod
    def eye_aspect_ratio(landmarks, indexes):
        """Return EAR for six FaceMesh eye landmarks in [p1..p6] order."""
        points = np.array(
            [[landmarks.landmark[index].x, landmarks.landmark[index].y] for index in indexes]
        )
        horizontal = np.linalg.norm(points[0] - points[3])
        if horizontal == 0:
            return 0.0
        return (
            np.linalg.norm(points[1] - points[5])
            + np.linalg.norm(points[2] - points[4])
        ) / (2.0 * horizontal)

    def detect_faces(self, frame=None):
        """Require a stable, forward-facing live person before recognition."""
        global previous_face, stable_frames, processing

        if processing:
            return

        if frame is None:
            ret, frame = cap.read()
            if not ret:
                return

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                left_eye = np.array(
                    [face_landmarks.landmark[33].x, face_landmarks.landmark[33].y]
                )
                right_eye = np.array(
                    [face_landmarks.landmark[263].x, face_landmarks.landmark[263].y]
                )
                nose = np.array(
                    [face_landmarks.landmark[1].x, face_landmarks.landmark[1].y]
                )
                mouth = np.array(
                    [face_landmarks.landmark[13].x, face_landmarks.landmark[13].y]
                )

                eye_distance = abs(left_eye[1] - right_eye[1])
                looking_straight = eye_distance < 0.01
                full_face_visible = (
                    0.1 < left_eye[0] < 0.9
                    and 0.1 < right_eye[0] < 0.9
                    and 0.1 < nose[0] < 0.9
                    and 0.1 < mouth[0] < 0.9
                )

                face_center = np.array([nose[0], nose[1]])
                if previous_face is not None:
                    movement = np.linalg.norm(face_center - previous_face)
                    if movement < 0.005:
                        stable_frames += 1
                    else:
                        stable_frames = 0
                previous_face = face_center

                ready_for_liveness = (
                    stable_frames >= STABILITY_THRESHOLD
                    and looking_straight
                    and full_face_visible
                )

                # A blink only counts while the person is still and facing
                # the camera. This prevents an old blink from authorizing a
                # later capture, and each branch logs only a state transition.
                if not ready_for_liveness:
                    self.blink_in_progress = False
                    self.blink_verified = False
                    return

                left_ear = self.eye_aspect_ratio(
                    face_landmarks, [33, 160, 158, 133, 153, 144]
                )
                right_ear = self.eye_aspect_ratio(
                    face_landmarks, [362, 385, 387, 263, 373, 380]
                )
                average_ear = (left_ear + right_ear) / 2.0
                if average_ear < EAR_THRESHOLD and not self.blink_verified:
                    self.blink_in_progress = True
                elif self.blink_in_progress:
                    self.blink_in_progress = False
                    self.blink_verified = True

                if (
                    ready_for_liveness and self.blink_verified
                ):
                    self.log_message(capture_message)
                    os.makedirs("CapturedFaces", exist_ok=True)
                    capture_path = os.path.join(
                        "CapturedFaces", f"captured_{int(time.time() * 1000)}_{uuid.uuid4().hex}.jpg"
                    )
                    if not cv2.imwrite(capture_path, frame):
                        self.log_message("Could not save the captured image. Please try again.")
                        return
                    processing = True
                    threading.Thread(
                        target=self.photo_detector, args=(capture_path,), daemon=True
                    ).start()
                    stable_frames = 0
                    self.blink_verified = False
                    self.blink_in_progress = False
                    return

        else:
            previous_face = None
            stable_frames = 0
            self.blink_in_progress = False
            self.blink_verified = False

    def photo_detector(self, captured_image_path):
        """Run face recognition asynchronously"""
        global detected_faces, processing
        names = read_csv_to_list(attendance_register)
        faces_all = os.listdir("faces_all")
        now = datetime.now()

        formatted_time = now.strftime("%I:%M %p")
        img1 = captured_image_path

        if not os.path.exists(img1):
            self.log_message(
                "Error: Captured photo does not exist. Skipping verification."
            )

            processing = False
            return
        matched = False
        try:
            for obj in faces_all:
                img2 = f"faces_all/{obj}"
                # MediaPipe has already detected a stable, live face before this
                # image is saved. DeepFace's OpenCV detector can still reject an
                # otherwise valid webcam frame, which raises the unhelpful
                # "Exception while processing img1_path" error. Keep detection
                # enabled, but allow DeepFace to use the whole validated image as
                # a fallback when its detector misses it.
                result = df.verify(
                    img1_path=img1,
                    img2_path=img2,
                    model_name=model,
                    threshold=threshold,
                    enforce_detection=False,
                )
                print(result["verified"])
                if result["verified"]:
                    matched = True
                    if obj in detected_faces:

                        self.log_message(
                            f"Hey {obj}, you have already been detected! Skipping..."
                        )
                        self.log_message("-" * dashno)
                        break

                    self.log_message(
                        f"{obj} is present, time of entry: {formatted_time}"
                    )
                    self.log_message("-" * dashno)
                    detected_faces.add(obj)
                    if len(names) > 1:
                        already_present = (
                            False  # Flag to check if obj is already in CSV
                        )

                        # Loop through all recorded names (excluding the first row)
                        for person in names[1:]:
                            if obj == person[0]:  # If the name exists, set flag to True
                                already_present = True
                                break  # No need to check further, exit loop

                        if not already_present:  # If obj is not found, add to CSV
                            with open(attendance_register, "a", newline="") as file:
                                csv.writer(file).writerow([obj, formatted_time])
                            print("Added You to the list")
                            # table = pd.read_csv(
                            #   f"AttendanceofClasses/{attendance_register}"
                            # )
                        # print(table)

                    else:
                        # If the list is empty (only header exists), add the first person
                        with open(attendance_register, "a", newline="") as file:
                            csv.writer(file).writerow([obj, formatted_time])

                    break

            if not matched:
                self.log_message(unkown_message)
        except Exception as e:
            self.log_message(f"DeepFace error while processing {img1}: {e}")
        finally:
            # This thread owns this uniquely named file, so it cannot delete
            # a capture currently being read by another recognition thread.
            if os.path.exists(img1):
                try:
                    os.remove(img1)
                except OSError as e:
                    self.log_message(f"Could not remove temporary capture: {e}")
            processing = False

    def update_frame(self):
        """Update the camera feed and run face detection"""
        ret, frame = cap.read()
        if ret:
            display_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(display_frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
            self.detect_faces(frame)
        self.after(10, self.update_frame)

    def on_closing(self):
        """Release camera and destroy window"""
        cap.release()
        cv2.destroyAllWindows()
        self.destroy()


if __name__ == "__main__":
    print("[INFO] Starting app...")
    app = WynkWaveApp()
    app.resizable(False, False)
    print("[INFO] App initialized...")
    app.mainloop()
