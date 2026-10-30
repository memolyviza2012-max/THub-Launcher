"""
THub Launcher 2.2 (Next-Gen Edition)
=====================================
Streamlined Modder Hub with 16:9 widescreen cards.
Unified Dashboard, Side-by-side TStudio & AI Helper spotlight.
"""

import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from ui.theme import Theme
from ui.components.sidebar import Sidebar
from ui.components.header_bar import HeaderBar
from ui.views.dashboard_view import DashboardView
from ui.views.ai_helper_view import AIHelperView
from ui.views.tstudio_view import TStudioView
from ui.views.apps_view import AppsView
from ui.views.knowledge_view import KnowledgeView
from ui.dialogs.project_wizard import ProjectWizardDialog
from core.config_manager import ConfigManager
from core.project_service import ProjectService
from core.tool_launcher import ToolLauncher

class THubNextGenApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Appearance & Window Configuration
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("THub Launcher - The Flagship Suite")
        self.geometry("1400x840")
        self.minsize(1020, 640)
        self.configure(fg_color=Theme.BG_CANVAS)

        if sys.platform == "win32":
            try:
                import ctypes
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('flagship.thub.launcher.nextgen')
            except Exception:
                pass

        # Core Services
        self.cfg_manager = ConfigManager()
        self.project_service = ProjectService(self.cfg_manager)
        self.projects = self.project_service.get_all_projects()
        self.active_project = self.projects[0] if self.projects else None

        # Grid Layout (Sidebar at col 0, Content at col 1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._build_shell()
        self.navigate_to("dashboard")

    def _build_shell(self):
        # 1. Left Sidebar
        self.sidebar = Sidebar(self, on_navigate=self.navigate_to, current_route="dashboard")
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # 2. Main Container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=(6, 14), pady=(6, 14))
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # 3. Top Header Bar
        self.header_bar = HeaderBar(
            self.main_container,
            title="Dashboard",
            total_count=len(self.projects),
            on_search=self._on_search_query,
            on_add=self._open_new_project_wizard,
            on_import=self._open_import_project_wizard,
            on_ai_copilot=lambda: self.navigate_to("ai_helper")
        )
        self.header_bar.grid(row=0, column=0, sticky="ew", pady=(0, 4))

        # 4. View Host Frame
        self.view_host = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.view_host.grid(row=1, column=0, sticky="nsew")
        self.view_host.grid_rowconfigure(0, weight=1)
        self.view_host.grid_columnconfigure(0, weight=1)

        self.current_view = None

    def navigate_to(self, route_id):
        """Switches views cleanly and fast."""
        self.sidebar.set_active(route_id)

        if self.current_view:
            self.current_view.destroy()
            self.current_view = None

        if route_id == "dashboard":
            self.header_bar.set_title("Dashboard (โปรเจกต์ม็อด)")
            self.header_bar.update_counts(len(self.projects), len(self.projects))
            self.current_view = DashboardView(
                self.view_host,
                projects=self.projects,
                on_tstudio_click=self._on_card_tstudio_launch,
                on_ai_click=self._on_card_ai_click,
                on_select_project=self._on_card_selected
            )
            self.current_view.grid(row=0, column=0, sticky="nsew")

        elif route_id == "ai_helper":
            self.header_bar.set_title("🤖 AI Helper Copilot")
            self.current_view = AIHelperView(
                self.view_host,
                projects=self.projects,
                active_project=self.active_project
            )
            self.current_view.grid(row=0, column=0, sticky="nsew")

        elif route_id == "tstudio":
            self.header_bar.set_title("📝 TStudio Translation Hub")
            self.current_view = TStudioView(
                self.view_host,
                projects=self.projects,
                active_project=self.active_project
            )
            self.current_view.grid(row=0, column=0, sticky="nsew")

        elif route_id == "apps":
            self.header_bar.set_title("✨ The Flagship Suite")
            self.current_view = AppsView(
                self.view_host,
                active_project=self.active_project
            )
            self.current_view.grid(row=0, column=0, sticky="nsew")

        elif route_id in ("knowledge", "tools", "settings"):
            self.header_bar.set_title("📚 Modding Knowledge Base" if route_id == "knowledge" else "🧰 Tool Library")
            self.current_view = KnowledgeView(self.view_host)
            self.current_view.grid(row=0, column=0, sticky="nsew")

    def _on_search_query(self, query):
        if isinstance(self.current_view, DashboardView):
            self.current_view.apply_search_and_filter(query)
            filtered_len = len(self.current_view.filtered_projects)
            self.header_bar.update_counts(filtered_len, len(self.projects))

    def _on_card_tstudio_launch(self, project):
        self.active_project = project
        p_path = project.get("path")
        try:
            ToolLauncher.launch_tstudio_for_project(p_path)
        except Exception as e:
            ctk.messagebox.showerror("Launch Error", f"ไม่สามารถเปิด TStudio ได้:\n{e}")

    def _on_card_ai_click(self, project):
        """Side-by-side AI Helper: Jumps to AI Copilot with this project preselected and analyzed!"""
        self.active_project = project
        self.navigate_to("ai_helper")

    def _on_card_selected(self, project):
        self.active_project = project

    def _open_new_project_wizard(self):
        ProjectWizardDialog(self, is_import_mode=False, on_created=self._on_project_added)

    def _open_import_project_wizard(self):
        ProjectWizardDialog(self, is_import_mode=True, on_created=self._on_project_added)

    def _on_project_added(self, new_project):
        self.projects = self.project_service.get_all_projects()
        self.active_project = new_project
        if isinstance(self.current_view, DashboardView):
            self.current_view.update_projects(self.projects)
            self.header_bar.update_counts(len(self.projects), len(self.projects))

if __name__ == "__main__":
    app = THubNextGenApp()
    app.mainloop()
