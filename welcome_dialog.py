#!/usr/bin/env python3
"""
Welcome Dialog for AugmentCode-Free
Shows welcome message and language selection on first run.
"""

import tkinter as tk
from tkinter import ttk
import webbrowser
from language_manager import get_language_manager, get_text


class WelcomeDialog:
    """Welcome dialog for first run"""
    
    def __init__(self, parent, config_manager):
        self.parent = parent
        self.config_manager = config_manager
        self.language_manager = get_language_manager(config_manager)
        self.result = None
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(get_text("dialogs.titles.welcome_title"))
        self.dialog.geometry("500x600")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg='#f5f5f5')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self._center_dialog()
        
        # Setup UI
        self._setup_ui()
        
        # Handle window close
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _center_dialog(self):
        """Center dialog on screen"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (600 // 2)
        self.dialog.geometry(f"500x600+{x}+{y}")
    
    def _setup_ui(self):
        """Setup the welcome dialog UI"""
        # Main frame
        main_frame = tk.Frame(self.dialog, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, 
                              text=get_text("dialogs.titles.welcome_title"),
                              font=('Microsoft YaHei', 18, 'bold'),
                              fg='#1f2937', bg='#f5f5f5')
        title_label.pack(pady=(0, 20))
        
        # Welcome message
        welcome_text = get_text("dialogs.messages.welcome_message")
        welcome_label = tk.Label(main_frame,
                                text=welcome_text,
                                font=('Microsoft YaHei', 11),
                                fg='#4b5563', bg='#f5f5f5',
                                wraplength=440, justify='left')
        welcome_label.pack(pady=(0, 30))
        
        # Language selection frame
        lang_frame = tk.Frame(main_frame, bg='#f5f5f5')
        lang_frame.pack(fill='x', pady=(0, 20))
        
        lang_label = tk.Label(lang_frame,
                             text=get_text("app.language"),
                             font=('Microsoft YaHei', 12, 'bold'),
                             fg='#374151', bg='#f5f5f5')
        lang_label.pack(anchor='w', pady=(0, 10))
        
        # Language selection
        lang_select_frame = tk.Frame(lang_frame, bg='#ffffff', relief='solid', bd=1)
        lang_select_frame.pack(fill='x', pady=(0, 10))
        
        # Style for combobox
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Welcome.TCombobox',
                       fieldbackground='#ffffff',
                       background='#ffffff',
                       borderwidth=0,
                       relief='flat')
        
        self.language_var = tk.StringVar()
        available_langs = self.language_manager.get_available_languages()
        lang_values = list(available_langs.values())
        
        # Set current language as default
        current_lang = self.language_manager.get_language()
        current_display = available_langs.get(current_lang, lang_values[0])
        self.language_var.set(current_display)
        
        self.language_combo = ttk.Combobox(lang_select_frame,
                                          textvariable=self.language_var,
                                          values=lang_values,
                                          state="readonly",
                                          font=('Microsoft YaHei', 11),
                                          style='Welcome.TCombobox')
        self.language_combo.pack(fill='x', padx=15, pady=10)
        self.language_combo.bind('<<ComboboxSelected>>', self._on_language_change)
        
        # Warning frame
        warning_frame = tk.Frame(main_frame, bg='#fef3c7', relief='solid', bd=1)
        warning_frame.pack(fill='x', pady=(20, 30))
        
        warning_text = get_text("dialogs.messages.first_run_warning")
        warning_label = tk.Label(warning_frame,
                                text=warning_text,
                                font=('Microsoft YaHei', 10),
                                fg='#92400e', bg='#fef3c7',
                                wraplength=440, justify='left')
        warning_label.pack(padx=15, pady=15)
        
        # GitHub link
        github_frame = tk.Frame(main_frame, bg='#f5f5f5')
        github_frame.pack(fill='x', pady=(0, 30))
        
        github_label = tk.Label(github_frame,
                               text=get_text("copyright.github"),
                               font=('Microsoft YaHei', 10, 'underline'),
                               fg='#3b82f6', bg='#f5f5f5',
                               cursor='hand2')
        github_label.pack()
        github_label.bind('<Button-1>', self._open_github)
        
        # Buttons frame
        buttons_frame = tk.Frame(main_frame, bg='#f5f5f5')
        buttons_frame.pack(fill='x', pady=(20, 0))
        
        # Continue button
        continue_btn = tk.Button(buttons_frame,
                               text=get_text("buttons.ok"),
                               font=('Microsoft YaHei', 12, 'bold'),
                               bg='#4f46e5', fg='white',
                               relief='flat', cursor='hand2',
                               bd=0, pady=12, padx=30,
                               command=self._on_continue)
        continue_btn.pack(side='right', padx=(10, 0))
        
        # Don't show again checkbox
        self.show_again_var = tk.BooleanVar(value=True)
        show_again_cb = tk.Checkbutton(buttons_frame,
                                      text="下次启动时显示此对话框" if current_lang == "zh_CN" else "Show this dialog on next startup",
                                      variable=self.show_again_var,
                                      font=('Microsoft YaHei', 9),
                                      fg='#6b7280', bg='#f5f5f5',
                                      selectcolor='#f5f5f5')
        show_again_cb.pack(side='left')
    
    def _on_language_change(self, event=None):
        """Handle language change"""
        selected_display = self.language_var.get()
        available_langs = self.language_manager.get_available_languages()
        
        # Find language code by display name
        for code, display in available_langs.items():
            if display == selected_display:
                self.language_manager.set_language(code)
                self._update_texts()
                break
    
    def _update_texts(self):
        """Update all texts after language change"""
        # Update dialog title
        self.dialog.title(get_text("dialogs.titles.welcome_title"))
        
        # Note: For simplicity, we'll just update the checkbox text
        # Full UI refresh would require recreating all widgets
        current_lang = self.language_manager.get_language()
        checkbox_text = "下次启动时显示此对话框" if current_lang == "zh_CN" else "Show this dialog on next startup"
        
        # Find and update checkbox (this is a simplified approach)
        for widget in self.dialog.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Frame):
                        for grandchild in child.winfo_children():
                            if isinstance(grandchild, tk.Checkbutton):
                                grandchild.config(text=checkbox_text)
    
    def _open_github(self, event=None):
        """Open GitHub repository"""
        try:
            webbrowser.open(get_text("copyright.github"))
        except Exception as e:
            print(f"Error opening GitHub link: {e}")
    
    def _on_continue(self):
        """Handle continue button"""
        # Save show again preference
        self.config_manager.set_show_welcome(self.show_again_var.get())
        
        # Mark first run as complete
        self.config_manager.mark_first_run_complete()
        
        self.result = True
        self.dialog.destroy()
    
    def _on_close(self):
        """Handle dialog close"""
        self.result = False
        self.dialog.destroy()
    
    def show(self):
        """Show dialog and return result"""
        self.dialog.wait_window()
        return self.result


class AboutDialog:
    """About dialog showing copyright and project information"""

    def __init__(self, parent, config_manager=None, show_dont_show_again=False):
        self.parent = parent
        self.language_manager = get_language_manager()
        self.config_manager = config_manager
        self.show_dont_show_again = show_dont_show_again
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(get_text("dialogs.titles.about_title"))
        self.dialog.geometry("500x580")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg='#f5f5f5')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self._center_dialog()
        
        # Setup UI
        self._setup_ui()
    
    def _center_dialog(self):
        """Center dialog on screen"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (580 // 2)
        self.dialog.geometry(f"500x580+{x}+{y}")
    
    def _setup_ui(self):
        """Setup the about dialog UI"""
        # Main frame
        main_frame = tk.Frame(self.dialog, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Title
        title_label = tk.Label(main_frame,
                              text=get_text("app.title"),
                              font=('Microsoft YaHei', 20, 'bold'),
                              fg='#1f2937', bg='#f5f5f5')
        title_label.pack(pady=(0, 10))
        
        # Version
        version_label = tk.Label(main_frame,
                                text=get_text("app.version"),
                                font=('Microsoft YaHei', 12),
                                fg='#6b7280', bg='#f5f5f5')
        version_label.pack(pady=(0, 30))
        
        # Copyright notice
        copyright_label = tk.Label(main_frame,
                                  text=get_text("copyright.notice"),
                                  font=('Microsoft YaHei', 11),
                                  fg='#374151', bg='#f5f5f5')
        copyright_label.pack(pady=(0, 10))
        
        # License
        license_label = tk.Label(main_frame,
                                text=get_text("copyright.license"),
                                font=('Microsoft YaHei', 11),
                                fg='#374151', bg='#f5f5f5')
        license_label.pack(pady=(0, 20))
        
        # GitHub link
        github_label = tk.Label(main_frame,
                               text=get_text("copyright.github"),
                               font=('Microsoft YaHei', 11, 'underline'),
                               fg='#3b82f6', bg='#f5f5f5',
                               cursor='hand2')
        github_label.pack(pady=(0, 30))
        github_label.bind('<Button-1>', self._open_github)
        
        # Warning frame
        warning_frame = tk.Frame(main_frame, bg='#fef3c7', relief='solid', bd=1)
        warning_frame.pack(fill='x', pady=(0, 30))
        
        warning_text = get_text("copyright.fraud_warning")
        warning_label = tk.Label(warning_frame,
                                text=warning_text,
                                font=('Microsoft YaHei', 9),
                                fg='#92400e', bg='#fef3c7',
                                wraplength=450, justify='center')
        warning_label.pack(padx=15, pady=15)

        # Don't show again checkbox (only if enabled)
        if self.show_dont_show_again and self.config_manager:
            self.dont_show_var = tk.BooleanVar()
            dont_show_frame = tk.Frame(main_frame, bg='#f5f5f5')
            dont_show_frame.pack(fill='x', pady=(10, 0))

            dont_show_cb = tk.Checkbutton(dont_show_frame,
                                         text="不再显示此对话框",
                                         variable=self.dont_show_var,
                                         font=('Microsoft YaHei', 10),
                                         bg='#f5f5f5', fg='#6b7280',
                                         activebackground='#f5f5f5',
                                         relief='flat', bd=0)
            dont_show_cb.pack()

        # Close button
        close_btn = tk.Button(main_frame,
                             text=get_text("buttons.ok"),
                             font=('Microsoft YaHei', 12, 'bold'),
                             bg='#4f46e5', fg='white',
                             relief='flat', cursor='hand2',
                             bd=0, pady=12, padx=30,
                             command=self._close_dialog)
        close_btn.pack(pady=(20, 0))
    
    def _close_dialog(self):
        """Handle dialog close with don't show again option"""
        if (self.show_dont_show_again and self.config_manager and
            hasattr(self, 'dont_show_var') and self.dont_show_var.get()):
            self.config_manager.set_show_about_on_startup(False)
        self.dialog.destroy()

    def _open_github(self, event=None):
        """Open GitHub repository"""
        try:
            webbrowser.open(get_text("copyright.github"))
        except Exception as e:
            print(f"Error opening GitHub link: {e}")

    def show(self):
        """Show dialog"""
        self.dialog.wait_window()
