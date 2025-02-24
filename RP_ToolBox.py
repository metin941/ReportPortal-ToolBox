import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox, scrolledtext
from tkinter import filedialog
import requests
import json
import tkinter as tk
from tkinter import messagebox, scrolledtext
from datetime import datetime
import webbrowser
import os
import configparser

class ToolTip:
    def __init__(self, widget, text, x_offset=5, y_offset=5, position='right'):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.position = position  # 'right', 'left', 'above', 'below'
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        widget_x = self.widget.winfo_rootx()
        widget_y = self.widget.winfo_rooty()
        widget_width = self.widget.winfo_width()
        widget_height = self.widget.winfo_height()

        # Calculate the position of the tooltip based on the chosen position
        if self.position == 'right':
            x = widget_x + widget_width + self.x_offset
            y = widget_y + self.y_offset
        elif self.position == 'left':
            x = widget_x - self.x_offset - 150  # Assuming 150px width for tooltip
            y = widget_y + self.y_offset
        elif self.position == 'above':
            x = widget_x + self.x_offset
            y = widget_y - 30  # Just above the widget
        elif self.position == 'below':
            x = widget_x + self.x_offset
            y = widget_y + widget_height + self.y_offset  # Just below the widget

        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip, text=self.text, background="#FAF09B", relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self, event):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class RpToolBox:
    
    def __init__(self, root):
        self.root = root
        self.root.title("ReportPortal API GUI")
        self.root.geometry("690x490")
        self.root.resizable(False, False)

        # Initialize UUIDs
        self.item_id = None
        self.launch_uuid = None
        self.suite_uuid = None
        self.test_uuid = None
        self.status = None
        self.base_url = None
        self.api_key = None
        self.project_name = None

        # Setup UI
        self.setup_ui()
        self.create_menu()
        self.create_copyright_label()

    def add_tooltip(self, widget, text):
        ToolTip(widget, text)

    def get_timestamp(self):
        return datetime.utcnow().isoformat() + "Z"

    def log_message(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.yview(tk.END)

    def load_config(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        try:
            self.base_url = config.get('settings', 'base_url')
            self.api_key = config.get('settings', 'api_key')
            self.project_name = config.get('settings', 'project_name')
        except configparser.NoOptionError as e:
            messagebox.showerror("Error", f"Missing configuration: {e}")
            return False
        return True

    def get_uuid_and_name(self):
        if not self.load_config():
            return
        
        self.item_id = self.input_id.get().strip()

        if not self.item_id:
            messagebox.showerror("Error", "Please enter a valid ID!")
            return
        
        url = f"{self.base_url}/{self.project_name}/item/{self.item_id}"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            uuid = data.get("uuid", "N/A")
            name = data.get("name", "N/A")

            # Display the UUID and name
            self.log_message(f"Item ID: {self.item_id}\nUUID: {uuid}\nName: {name}")
        else:
            messagebox.showerror("Error", f"Failed to fetch data! Status Code: {response.status_code}")

    def stop_test(self):
        if not self.load_config():
            return
        
        self.test_uuid = self.input_test_case_uuid.get().strip()
        self.status = self.input_status_test_case.get().strip()
        if not self.test_uuid:
            messagebox.showerror("Error", "Please enter valid UUID!")
            return
        url = f"{self.base_url}/{self.project_name}/item/{self.test_uuid}?projectName={self.project_name}"
        payload = {"endTime": self.get_timestamp(), "status": self.status}
        requests.put(url, headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}, json=payload)
        self.log_message("Test stopped.")

    def stop_test_suite(self):
        if not self.load_config():
            return
        
        self.suite_uuid = self.input_test_suite_uuid.get().strip()
        self.status = self.input_status_test_suite.get().strip()
        if not self.suite_uuid:
            messagebox.showerror("Error", "Please enter valid UUID!")
            return
        url = f"{self.base_url}/{self.project_name}/item/{self.suite_uuid}?projectName={self.project_name}"
        payload = {"endTime": self.get_timestamp(), "status": self.status}
        requests.put(url, headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}, json=payload)
        self.log_message("Test Suite stopped.")

    def stop_launch(self):
        if not self.load_config():
            return
        
        self.launch_uuid = self.input_stop_launch_uuid.get().strip()
        self.status = self.input_status_launch.get().strip()
        if not self.launch_uuid:
            messagebox.showerror("Error", "Please enter valid UUID!")
            return
        url = f"{self.base_url}/{self.project_name}/launch/{self.launch_uuid}/finish?projectName={self.project_name}"
        payload = {"endTime": self.get_timestamp(), "status": self.status}
        requests.put(url, headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}, json=payload)
        self.log_message("Launch stopped.")

    def setup_ui(self):
        self.label_test_case_uuid = Label(self.root, text="Test case uuid:").place(x=10, y=23)
        self.input_test_case_uuid = Entry(self.root, width=55)
        self.input_test_case_uuid.place(x=100, y=23)
        ToolTip(self.input_test_case_uuid,"Enter valid uuid for 'Test case' \n You can get the uuid from ID \n Use last field") 

        self.input_status_test_case = ttk.Combobox(self.root, values=["PASSED", "FAILED", "FOR_INVESTIGATION"], state="readonly")
        self.input_status_test_case.place(x=440, y=23)
        self.input_status_test_case.current(0)

        self.btn_stop_test_case = Button(self.root, text="Stop test case", command=self.stop_test).place(x=590, y=20)

        #=========================================================================

        self.label_test_suite_uuid = Label(self.root, text="Test suite uuid:").place(x=10, y=53)
        self.input_test_suite_uuid = Entry(self.root, width=55)
        self.input_test_suite_uuid.place(x=100, y=53)
        ToolTip(self.input_test_suite_uuid,"Enter valid uuid for 'Test suite' \n You can get the uuid from ID \n Use last field")

        self.input_status_test_suite = ttk.Combobox(self.root, values=["PASSED", "FAILED", "FOR_INVESTIGATION"], state="readonly")
        self.input_status_test_suite.place(x=440, y=53)
        self.input_status_test_suite.current(0)

        self.btn_stop_test_suite = Button(self.root, text="Stop test suite", command=self.stop_test_suite).place(x=590, y=50)

        #=========================================================================

        self.label_launch_uuid = Label(self.root, text="Launch uuid:").place(x=10, y=83)
        self.input_stop_launch_uuid = Entry(self.root, width=55)
        self.input_stop_launch_uuid.place(x=100, y=83)
        ToolTip(self.input_stop_launch_uuid,"Enter valid uuid for 'Launch' \n You can get the uuid from ID \n Use last field")

        self.input_status_launch = ttk.Combobox(self.root, values=["PASSED", "FAILED", "FOR_INVESTIGATION"], state="readonly")
        self.input_status_launch.place(x=440, y=83)
        self.input_status_launch.current(0)

        self.btn_stop_launch = Button(self.root, text="Stop launch", command=self.stop_launch).place(x=590, y=80)

        #=======================================================================
        self.label_get_uuid = Label(self.root, text="Get UIID from ID:").place(x=10, y=113)
        self.input_id = Entry(self.root, width=79)
        self.input_id.place(x=105, y=113)
        ToolTip(self.input_id,"Enter ID \n You can get the ID from RP url \n eg. '62086118'")

        self.btn_get_uuid = Button(self.root,width=10, text="GET", command=self.get_uuid_and_name).place(x=590, y=110)

        #=======================================================================

        self.btn_clear_log = Button(self.root,width=10, text="Clear Log", command=self.clear_log).place(x=10, y=450)

        #=======================================================================
        self.log_text = scrolledtext.ScrolledText(self.root, height=15, width=80, state=tk.DISABLED)
        self.log_text.place(x=10, y=200)

    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        menu_bar.add_cascade(label="RP API Settings", command=self.open_api_settings)
        menu_bar.add_cascade(label="Info", command=self.open_info)
        self.root.config(menu=menu_bar)

    def open_info(self):

        text = ("This tool is intended for stopping test launches and test suites within Report Portal via its API. "
                "\n\nPlease use it with caution, as improper use may disrupt ongoing testing processes.\n\n"
                "This tool is designed to stop ongoing test launches and test suites remotely providing real-time control over test executions. "
                "\nWhether it's due to an error, the need for intervention, or any other reason this tool allows users to halt tests instantly, ensuring efficient "
                "management of test processes without unnecessary delays.\n\n"
                "For more info:↪ metin.hasanov@siemens.com ↩")
        info_window = tk.Toplevel(self.root)
        info_window.title("Tool Info")
        info_window.geometry("500x500")
        tk.Label(info_window, text=text,justify=tk.LEFT, wraplength=450).pack(pady=10)

    def create_copyright_label(self):
        def open_github(event):
            webbrowser.open("https://github.com/metin941/ReportPortal-ToolBox")

        label = tk.Label(
            self.root, text="v1.0 © M.Hasanov 2025", font=("Arial", 10, "italic"), cursor="hand2"
        )
        label.place(x=530, y=460)

        label.bind("<Button-1>", open_github)

    def open_api_settings(self):
        api_settings = ApiSettings()
        api_settings.run()

        # After the user updates settings, load them into RpToolBox
        self.base_url = api_settings.base_url_entry.get().strip()
        self.api_key = api_settings.api_key_entry.get().strip()
        self.project_name = api_settings.project_name_entry.get().strip()

        if not self.base_url or not self.api_key or not self.project_name:
            messagebox.showerror("Error", "API settings are incomplete!")
        else:
            messagebox.showinfo("Settings", "API settings loaded successfully!")
    
    def clear_log(self):
        self.log_text.config(state=tk.NORMAL)  # Enable editing
        self.log_text.delete(1.0, tk.END)  # Clear all content
        self.log_text.config(state=tk.DISABLED)  # Disable editing

class ApiSettings:
    def __init__(self):
        self.root = Tk()
        self.root.title("ReportPortal API Settings")
        self.root.geometry("550x200")
        self.root.resizable(False, False)
        self.config = configparser.ConfigParser()  # To manage configuration
        self.config_file = 'config.ini'  # Path to your config file
        self.setup_widgets()

    def setup_widgets(self):
        self.base_url_label = Label(self.root, text="Base URL:")
        self.base_url_label.place(x=15, y=24)
        self.base_url_entry = Entry(self.root, width=70)
        self.base_url_entry.place(x=100, y=24)
        ToolTip(self.base_url_entry,"Enter base url for siemens \n you can get the base url from RP or  \n test suite file") 
        

        self.api_key_label = Label(self.root, text="API Key:")
        self.api_key_label.place(x=15, y=54)
        self.api_key_entry = Entry(self.root, width=70)
        self.api_key_entry.place(x=100, y=54)
        ToolTip(self.api_key_entry,"Enter API key \n you can get the api key from test suite file \n it should match the test suite that you want to stop!") 

        self.project_name_label = Label(self.root, text="Project Name:")
        self.project_name_label.place(x=15, y=84)
        self.project_name_entry = Entry(self.root, width=70)
        self.project_name_entry.place(x=100, y=84)
        ToolTip(self.project_name_entry,"Enter project name \n you can get the project name from test suite file \n Note: type it in lowercase")

        self.save_button = Button(self.root, text="Save Settings", command=self.save_settings)
        self.save_button.place(x=100, y=114)

    def save_settings(self):
        # Save the settings into a config file
        base_url = self.base_url_entry.get().strip()
        api_key = self.api_key_entry.get().strip()
        project_name = self.project_name_entry.get().strip()

        if not base_url or not api_key or not project_name:
            messagebox.showerror("Error", "All fields are required!")
            return

        if not os.path.exists(self.config_file):
            with open(self.config_file, 'w') as f:
                f.write("[settings]\n")

        self.config.read(self.config_file)
        if not self.config.has_section('settings'):
            self.config.add_section('settings')

        self.config.set('settings', 'base_url', base_url)
        self.config.set('settings', 'api_key', api_key)
        self.config.set('settings', 'project_name', project_name)

        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

        messagebox.showinfo("Success", "Settings saved successfully!")

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = RpToolBox(root)
    root.mainloop()
