# Pyinstaller compatability code
import os
import customtkinter as ctk
import tkinter.filedialog as fd
import cv2, subprocess

current_dir = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(current_dir, "config.cfg")

def load_config():
    config = {}
    with open(CONFIG_FILE, "r") as file:
        section = None
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):  # Skip empty lines and comments
                continue
            if line.startswith("-"):
                section = line[2:].strip()
                config[section] = {}
            elif section and ":" in line:
                key, value = map(str.strip, line.split(":", 1))
                config[section][key] = value
    return config

def save_config(config):
    with open(CONFIG_FILE, "w") as file:
        for section, values in config.items():
            file.write(f"- {section}\n")
            for key, value in values.items():
                file.write(f"{key}: {value}\n")
            file.write("\n")

def format_duration(seconds):
    seconds = int(seconds)  # Ensure it's an integer
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if hours > 0:
        return f"{hours}h {minutes:02}m {seconds:02}s"
    elif minutes > 0:
        return f"{minutes}m {seconds:02}s"
    else:
        return f"{seconds}s"


class BlurConfigApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("500x800")
        self.color = os.path.join(current_dir, "night.json")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme(self.color)
        ctk.set_widget_scaling(1.2)
        self.title("Blur Config Editor")
        self.resizable(False,  True)
        self.config = load_config()
        self.widgets = {}
        self.video_path=None
        self.video_duration=0
        self.create_ui()
    
    def update_config(self, section, key, value):
        self.config[section][key] = value
        save_config(self.config)
    
    def load_file(self):
        file_path = fd.askopenfilename(
            title="Select a Video File",
            filetypes=[("Video Files", "*.mp4;*.avi;*.mov;*.mkv;*.wmv")]
        )
        
        if not file_path:  # User canceled the dialog
            return None

        # Verify file extension
        valid_extensions = (".mp4", ".avi", ".mov", ".mkv", ".wmv")
        if not file_path.lower().endswith(valid_extensions):
            print("Invalid file type selected.")
            return None

        # Get video duration
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            print("Failed to open video file.")
            return None

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        cap.release()

        if fps > 0:
            self.video_duration = frame_count / fps
        else:
            return None
    
        self.video_path=file_path

        file_name = os.path.basename(file_path)

        self.video_label.configure(text=f"{file_name}  |  Duration: {format_duration(self.video_duration)}")

    def start_render(self):
        if not hasattr(self, "video_path") or not self.video_path:
            print("No video file selected!")
            return
        
        output_folder = fd.askdirectory(title="Select Output Folder")
        if not output_folder:
            print("No output folder selected!")
            return
        
        # Construct the base output file name
        output_file_base = os.path.basename(self.video_path)
        output_file = os.path.join(output_folder, f"{output_file_base} - VectorBlur.mp4")
        
        # Check if the file already exists and append a number if necessary
        counter = 0
        while os.path.exists(output_file):
            counter += 1
            output_file = os.path.join(output_folder, f"{output_file_base} - VectorBlur ({counter}).mp4")
        
        # Build the command
        command = [
            r"C:\Program Files (x86)\blur\blur.exe",
            "--noui",
            "-i", self.video_path,
            "-c", CONFIG_FILE,
            "-o", output_file
        ]
        
        try:
            # Run the rendering command
            subprocess.run(command, check=True)
            print(f"Rendering started! Output file: {output_file}")
            
            # Open the output folder in File Explorer
            subprocess.Popen(f'explorer /select,"{output_file}"')
        
        except subprocess.CalledProcessError as e:
            print(f"Error during rendering: {e}")

    def create_ui(self):
        self.rowconfigure(list(range(8)), weight = 1)
        self.columnconfigure(list(range(2)), weight = 1)
        self.create_blur_menu()
        
        video_frame = ctk.CTkFrame(self)
        video_frame.grid(row=11, column=0, padx=5, pady=5, ipadx=5, ipady=5, sticky="NSEW", columnspan=2)

        self.video_label = ctk.CTkLabel(video_frame, text="No file loaded yet.")
        self.video_label.grid(row=0, column=0, padx=5, pady=5, ipadx=5, ipady=5, sticky="NSEW")

        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.grid(row=8, column=0, padx=5, pady=5, ipadx=5, ipady=5, sticky="NSEW", columnspan=2)
        
        self.file_button = ctk.CTkButton(bottom_frame, text="Select Video", command=self.load_file)
        self.file_button.pack(side='left', pady=10, padx=10)
        
        self.render_button = ctk.CTkButton(bottom_frame, text="Start Render", command=self.start_render)
        self.render_button.pack(side='right', pady=10, padx=10)
    
    def create_blur_menu(self):
        blur_tab = ctk.CTkScrollableFrame(self)
        blur_tab.grid(row=0, column=0, padx=5, pady=5, ipadx=5, ipady=5, sticky="NSEW", rowspan=8, columnspan=2)

        blur_section_label = ctk.CTkLabel(blur_tab, text="Blur Settings", font=ctk.CTkFont(size=24))
        blur_section_label.grid(row=0, column=0, padx=5, pady=5, ipadx=5, ipady=5, sticky="NSEW")

        blur_setting_frame = ctk.CTkFrame(blur_tab)
        blur_setting_frame.grid(row=1, column=0, padx=5, pady=5, ipadx=5, ipady=5, sticky="NSEW")

        blur_label = ctk.CTkLabel(blur_setting_frame, text="Enable Blur")
        blur_label.grid(row=0, column=0, padx=5, pady=5, ipadx=5, ipady=5, sticky="NSEW")
        blur_var = ctk.BooleanVar(value=self.config.get("blur", {}).get("blur", "true") == "true")
        blur_checkbox = ctk.CTkCheckBox(blur_setting_frame, variable=blur_var, text="", command=lambda: self.update_config("blur", "blur", str(blur_var.get()).lower()))
        blur_checkbox.grid(row=0, column=1, padx=5, pady=5, ipadx=5, ipady=5, sticky="NSEW")
        
        blur_amount_setting_frame = ctk.CTkFrame(blur_tab)
        blur_amount_setting_frame.grid(row=2, column=0, padx=5, pady=5, ipadx=5, ipady=5, sticky="NSEW")

        blur_amount_label = ctk.CTkLabel(blur_amount_setting_frame, text="Blur Amount")
        blur_amount_label.grid(row=0, column=0, padx=5, pady=5, ipadx=5, ipady=5, sticky="NSEW")
        blur_amount = ctk.DoubleVar(value=float(self.config.get("blur", {}).get("blur amount", 1)))
        blur_amount_display = ctk.CTkLabel(blur_amount_setting_frame, text=f"{blur_amount.get():.1f}")
        blur_amount_display.grid(row=0, column=1, padx=5, pady=5, ipadx=5, ipady=5, sticky="NSEW")
        blur_slider = ctk.CTkSlider(blur_amount_setting_frame, from_=0, to=5, variable=blur_amount, 
                                    command=lambda val: [blur_amount_display.configure(text=f"{val:.1f}"), self.update_config("blur", "blur amount", str(val))])
        blur_slider.grid(row=0, column=2, padx=5, pady=5, ipadx=5, ipady=5)
        
        
        blur_weighting_setting_frame = ctk.CTkFrame(blur_tab)
        blur_weighting_setting_frame.grid(row=3, column=0, padx=5, pady=5, ipadx=5, ipady=5, sticky="NSEW")

        blur_weighting_label = ctk.CTkLabel(blur_weighting_setting_frame, text="Blur Weighting")
        blur_weighting_label.grid(row=0, column=0, padx=5, pady=5, ipadx=5, ipady=5, sticky="NSEW")
        blur_weighting_options = ["equal", "gaussian", "gaussian_sym", "pyramid", "pyramid_sym"]
        blur_weighting = ctk.StringVar(value=self.config.get("blur", {}).get("blur weighting", "equal"))
        blur_dropdown = ctk.CTkOptionMenu(blur_weighting_setting_frame, values=blur_weighting_options, variable=blur_weighting, 
                                        command=lambda val: self.update_config("blur", "blur weighting", val))
        blur_dropdown.grid(row=0, column=1)

        interpolate_section_label = ctk.CTkLabel(blur_tab, text="Interpolation Settings", font=ctk.CTkFont(size=24))
        interpolate_section_label.grid(row=4, column=0, padx=5, pady=5, ipadx=5, ipady=5, sticky="NSEW")

        interpolate_setting_frame = ctk.CTkFrame(blur_tab)
        interpolate_setting_frame.grid(row=5, column=0, padx=5, pady=5, ipadx=5, ipady=5, sticky="NSEW")

        interpolate_label = ctk.CTkLabel(interpolate_setting_frame, text="Enable Interpolation")
        interpolate_label.grid(row=0, column=0, padx=5, pady=5, ipadx=5, ipady=5, sticky="NSEW")
        interpolate_var = ctk.BooleanVar(value=self.config.get("interpolation", {}).get("interpolate", "true") == "true")
        interpolate_checkbox = ctk.CTkCheckBox(interpolate_setting_frame, variable=interpolate_var, text="", command=lambda: self.update_config("interpolation", "interpolate", str(interpolate_var.get()).lower()))
        interpolate_checkbox.grid(row=0, column=1, padx=5, pady=5, ipadx=5, ipady=5, sticky="NSEW")

        interpolate_fps_frame = ctk.CTkFrame(blur_tab)
        interpolate_fps_frame.grid(row=6, column=0, padx=5, pady=5, ipadx=5, ipady=5, sticky="NSEW")

        interpolated_fps_label = ctk.CTkLabel(interpolate_fps_frame, text="Interpolated FPS")
        interpolated_fps_label.grid(row=0, column=0, padx=5, pady=5, ipadx=5, ipady=5, sticky="NSEW")
        interpolated_fps = ctk.IntVar(value=int(self.config.get("interpolation", {}).get("interpolated fps", 60)))
        interpolated_fps_display = ctk.CTkLabel(interpolate_fps_frame, text=f"{int(interpolated_fps.get()):03}")
        interpolated_fps_display.grid(row=0, column=1, padx=5, pady=5, ipadx=5, ipady=5, sticky="NSEW")
        interpolated_fps_slider = ctk.CTkSlider(interpolate_fps_frame, from_=1, to=999, variable=interpolated_fps, 
                                            command=lambda val: [interpolated_fps_display.configure(text=f"{int(val):03}"), self.update_config("interpolation", "interpolated fps", str(int(val)))])
        interpolated_fps_slider.grid(row=0, column=2, padx=5, pady=5, ipadx=5, ipady=5)

        render_section_label = ctk.CTkLabel(blur_tab, text="Rendering Settings", font=ctk.CTkFont(size=24))
        render_section_label.grid(row=7, column=0, padx=5, pady=5, ipadx=5, ipady=5, sticky="NSEW")

        render_quality_frame = ctk.CTkFrame(blur_tab)
        render_quality_frame.grid(row=8, column=0, padx=5, pady=5, ipadx=5, ipady=5, sticky="NSEW")

        quality_label = ctk.CTkLabel(render_quality_frame, text="Quality (0=highest)")
        quality_label.grid(row=0, column=0, padx=5, pady=5, ipadx=5, ipady=5, sticky="NSEW")
        quality = ctk.IntVar(value=int(self.config.get("rendering", {}).get("quality", 23)))
        quality_display = ctk.CTkLabel(render_quality_frame, text=f"{int(quality.get()):02}")
        quality_display.grid(row=0, column=1, padx=5, pady=5, ipadx=5, ipady=5, sticky="NSEW")
        quality_slider = ctk.CTkSlider(render_quality_frame, from_=0, to=51, variable=quality, 
                                    command=lambda val: [quality_display.configure(text=f"{int(val):02}"), self.update_config("rendering", "quality", str(int(val)))])
        quality_slider.grid(row=0, column=2, padx=5, pady=5, ipadx=5, ipady=5)

        render_deduplicate_frame = ctk.CTkFrame(blur_tab)
        render_deduplicate_frame.grid(row=9, column=0, padx=5, pady=5, ipadx=5, ipady=5, sticky="NSEW")

        deduplicate_label = ctk.CTkLabel(render_deduplicate_frame, text="Remove Duplicate Frames")
        deduplicate_label.grid(row=0, column=0, padx=5, pady=5, ipadx=5, ipady=5)
        deduplicate_var = ctk.BooleanVar(value=self.config.get("rendering", {}).get("deduplicate", "false") == "true")
        deduplicate_checkbox = ctk.CTkCheckBox(render_deduplicate_frame, variable=deduplicate_var, text="",
                                            command=lambda: self.update_config("rendering", "deduplicate", str(deduplicate_var.get()).lower()))
        deduplicate_checkbox.grid(row=0, column=1, padx=5, pady=5, ipadx=5, ipady=5)

        render_preview_frame = ctk.CTkFrame(blur_tab)
        render_preview_frame.grid(row=10, column=0, padx=5, pady=5, ipadx=5, ipady=5, sticky="NSEW")

        preview_label = ctk.CTkLabel(render_preview_frame, text="Enable Preview Window")
        preview_label.grid(row=0, column=0, padx=5, pady=5, ipadx=5, ipady=5)
        preview_var = ctk.BooleanVar(value=self.config.get("rendering", {}).get("preview", "false") == "true")
        preview_checkbox = ctk.CTkCheckBox(render_preview_frame, variable=preview_var, text="",
                                        command=lambda: self.update_config("rendering", "preview", str(preview_var.get()).lower()))
        preview_checkbox.grid(row=0, column=1, padx=5, pady=5, ipadx=5, ipady=5)

if __name__ == "__main__":
    app = BlurConfigApp()
    app.mainloop()
