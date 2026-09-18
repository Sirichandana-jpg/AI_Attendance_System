import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
from PIL import Image, ImageTk
import csv
import os
from datetime import datetime

from src.database import database
from src.enrollment.student_registration import register_student
from src.video.video_processor import VideoProcessor
from src.attendance.attendance_manager import AttendanceManager

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AI Attendance Management System")
        self.geometry("1000x700")

        # Configure grid layout (1x2)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Create sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="AI Attendance", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.dashboard_btn = ctk.CTkButton(self.sidebar_frame, text="Dashboard", command=self.show_dashboard)
        self.dashboard_btn.grid(row=1, column=0, padx=20, pady=10)

        self.register_btn = ctk.CTkButton(self.sidebar_frame, text="Register", command=self.show_register)
        self.register_btn.grid(row=2, column=0, padx=20, pady=10)

        self.cctv_btn = ctk.CTkButton(self.sidebar_frame, text="CCTV", command=self.show_cctv)
        self.cctv_btn.grid(row=3, column=0, padx=20, pady=10)

        self.reports_btn = ctk.CTkButton(self.sidebar_frame, text="Reports", command=self.show_reports)
        self.reports_btn.grid(row=4, column=0, padx=20, pady=10)

        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 20))

        # Main content area
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Initialize frames
        self.frames = {}
        self.setup_dashboard_frame()
        self.setup_register_frame()
        self.setup_cctv_frame()
        self.setup_reports_frame()

        # Show Dashboard initially
        self.show_dashboard()

        # Database and Managers
        database.initialize_database()
        self.video_processor = None
        
        # Periodic Dashboard update
        self.update_dashboard_stats()

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def hide_all_frames(self):
        for frame in self.frames.values():
            frame.grid_forget()

    def show_dashboard(self):
        self.hide_all_frames()
        self.frames["dashboard"].grid(row=0, column=0, sticky="nsew")
        self.update_dashboard_stats()

    def show_register(self):
        self.hide_all_frames()
        self.frames["register"].grid(row=0, column=0, sticky="nsew")

    def show_cctv(self):
        self.hide_all_frames()
        self.frames["cctv"].grid(row=0, column=0, sticky="nsew")

    def show_reports(self):
        self.hide_all_frames()
        self.frames["reports"].grid(row=0, column=0, sticky="nsew")
        self.update_reports()

    # --- Dashboard ---
    def setup_dashboard_frame(self):
        frame = ctk.CTkFrame(self.main_frame)
        self.frames["dashboard"] = frame
        frame.grid_columnconfigure((0,1), weight=1)

        ctk.CTkLabel(frame, text="Dashboard", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, columnspan=2, pady=20)

        self.total_students_lbl = ctk.CTkLabel(frame, text="Total Students: 0", font=ctk.CTkFont(size=18))
        self.total_students_lbl.grid(row=1, column=0, pady=10)

        self.present_today_lbl = ctk.CTkLabel(frame, text="Present Today: 0", font=ctk.CTkFont(size=18))
        self.present_today_lbl.grid(row=1, column=1, pady=10)

        self.absent_today_lbl = ctk.CTkLabel(frame, text="Absent Today: 0", font=ctk.CTkFont(size=18))
        self.absent_today_lbl.grid(row=2, column=0, pady=10)

        self.attendance_perc_lbl = ctk.CTkLabel(frame, text="Attendance %: 0%", font=ctk.CTkFont(size=18))
        self.attendance_perc_lbl.grid(row=2, column=1, pady=10)

    def update_dashboard_stats(self):
        total_students = len(database.get_all_students())
        today = datetime.now().strftime("%Y-%m-%d")
        present = len(database.get_attendance_by_date(today))
        absent = total_students - present if total_students > 0 else 0
        perc = (present / total_students * 100) if total_students > 0 else 0

        self.total_students_lbl.configure(text=f"Total Students: {total_students}")
        self.present_today_lbl.configure(text=f"Present Today: {present}")
        self.absent_today_lbl.configure(text=f"Absent Today: {absent}")
        self.attendance_perc_lbl.configure(text=f"Attendance %: {perc:.1f}%")

    # --- Register ---
    def setup_register_frame(self):
        frame = ctk.CTkFrame(self.main_frame)
        self.frames["register"] = frame

        ctk.CTkLabel(frame, text="Register Student", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)

        self.reg_id = ctk.CTkEntry(frame, placeholder_text="Student ID", width=300)
        self.reg_id.pack(pady=10)

        self.reg_name = ctk.CTkEntry(frame, placeholder_text="Student Name", width=300)
        self.reg_name.pack(pady=10)
        
        self.reg_dept = ctk.CTkEntry(frame, placeholder_text="Department", width=300)
        self.reg_dept.pack(pady=10)

        btn = ctk.CTkButton(frame, text="Capture & Register", command=self.do_registration, width=300)
        btn.pack(pady=20)

    def do_registration(self):
        s_id = self.reg_id.get().strip()
        name = self.reg_name.get().strip()
        dept = self.reg_dept.get().strip()

        if not s_id or not name:
            messagebox.showerror("Error", "ID and Name are required.")
            return

        success = register_student(s_id, name, dept)
        if success:
            messagebox.showinfo("Success", f"{name} registered successfully!")
            self.reg_id.delete(0, 'end')
            self.reg_name.delete(0, 'end')
            self.reg_dept.delete(0, 'end')
            self.update_dashboard_stats()
        else:
            messagebox.showerror("Error", "Registration failed. See console for details.")

    # --- CCTV ---
    def setup_cctv_frame(self):
        frame = ctk.CTkFrame(self.main_frame)
        self.frames["cctv"] = frame
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(frame)
        top.grid(row=0, column=0, sticky="ew", pady=10)

        self.src_entry = ctk.CTkEntry(top, placeholder_text="Source (0 for webcam, or path)", width=300)
        self.src_entry.pack(side="left", padx=10)

        self.src_btn = ctk.CTkButton(top, text="Browse", command=self.browse_video, width=80)
        self.src_btn.pack(side="left", padx=5)

        self.start_btn = ctk.CTkButton(top, text="Start", command=self.start_cctv, width=80)
        self.start_btn.pack(side="left", padx=5)

        self.pause_btn = ctk.CTkButton(top, text="Pause", command=self.pause_cctv, width=80)
        self.pause_btn.pack(side="left", padx=5)

        self.stop_btn = ctk.CTkButton(top, text="Stop", command=self.stop_cctv, width=80)
        self.stop_btn.pack(side="left", padx=5)
        
        self.log_lbl = ctk.CTkLabel(top, text="Ready", text_color="green")
        self.log_lbl.pack(side="left", padx=20)

        self.video_label = tk.Label(frame, bg="black")
        self.video_label.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

    def browse_video(self):
        file = filedialog.askopenfilename(title="Select Video File")
        if file:
            self.src_entry.delete(0, 'end')
            self.src_entry.insert(0, file)

    def update_video_frame(self, rgb_frame):
        img = Image.fromarray(rgb_frame)
        # resize for display if needed
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)
        
    def log_cctv_event(self, msg):
        self.log_lbl.configure(text=msg)

    def start_cctv(self):
        if self.video_processor and self.video_processor.is_running:
            return
            
        src = self.src_entry.get().strip()
        if not src:
            src = 0
        elif src.isdigit():
            src = int(src)
            
        self.video_processor = VideoProcessor(
            source=src, 
            on_frame_callback=self.update_video_frame,
            on_event_callback=self.log_cctv_event
        )
        self.video_processor.start()

    def pause_cctv(self):
        if self.video_processor:
            if self.video_processor.is_paused:
                self.video_processor.resume()
                self.pause_btn.configure(text="Pause")
            else:
                self.video_processor.pause()
                self.pause_btn.configure(text="Resume")

    def stop_cctv(self):
        if self.video_processor:
            self.video_processor.stop()
            self.video_processor = None
            self.video_label.configure(image="")
            self.log_lbl.configure(text="Stopped")

    # --- Reports ---
    def setup_reports_frame(self):
        frame = ctk.CTkFrame(self.main_frame)
        self.frames["reports"] = frame
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(frame)
        top.grid(row=0, column=0, sticky="ew", pady=10)

        ctk.CTkLabel(top, text="Today's Attendance").pack(side="left", padx=10)
        
        btn_export = ctk.CTkButton(top, text="Export CSV", command=self.export_csv)
        btn_export.pack(side="right", padx=10)

        self.reports_text = ctk.CTkTextbox(frame)
        self.reports_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

    def update_reports(self):
        self.reports_text.delete("1.0", "end")
        today = datetime.now().strftime("%Y-%m-%d")
        records = database.get_attendance_by_date(today)
        
        if not records:
            self.reports_text.insert("end", "No attendance records for today.\n")
            return
            
        header = f"{'ID':<10} | {'Name':<20} | {'Time':<10} | {'Source':<15} | {'Confidence':<10} | {'Status'}\n"
        self.reports_text.insert("end", header)
        self.reports_text.insert("end", "-" * 80 + "\n")
        
        for r in records:
            line = f"{r['student_id']:<10} | {r['name']:<20} | {r['time']:<10} | {r['source']:<15} | {r['confidence']:<10.1f} | {r['status']}\n"
            self.reports_text.insert("end", line)
            
        self.reports_text.insert("end", "\n\n--- Absent Students ---\n")
        mgr = AttendanceManager()
        absent = mgr.get_absent_students()
        if not absent:
            self.reports_text.insert("end", "None\n")
        else:
            for s in absent:
                self.reports_text.insert("end", f"{s['student_id']:<10} | {s['name']:<20}\n")

    def export_csv(self):
        today = datetime.now().strftime("%Y-%m-%d")
        records = database.get_attendance_by_date(today)
        
        os.makedirs("attendance", exist_ok=True)
        file_path = os.path.join("attendance", f"attendance_{today}.csv")
        
        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Student ID", "Name", "Department", "Date", "Time", "Source", "Confidence", "Status"])
            for r in records:
                writer.writerow([r['student_id'], r['name'], r['department'], r['date'], r['time'], r['source'], f"{r['confidence']:.2f}", r['status']])
                
        messagebox.showinfo("Export", f"Exported to {file_path}")

if __name__ == "__main__":
    app = App()
    app.mainloop()