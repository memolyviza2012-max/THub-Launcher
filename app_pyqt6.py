"""
THub Launcher 2.2 (PyQt6 High-Performance Edition)
===================================================
Ultra-fast, hardware-accelerated desktop modder hub.
Inspired by DLSS Swapper (16:9 widescreen cards, Obsidian Dark theme).
Spotlighting AI Helper Copilot and TStudio Translation Suite.
"""

import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QStackedWidget, QMessageBox, QDialog
)
from PyQt6.QtGui import QIcon, QPalette, QColor
from PyQt6.QtCore import pyqtSignal, QTimer, QThread

from ui_pyqt6.theme_qss import get_theme_stylesheet, get_theme_palette, OBSIDIAN_STYLESHEET
from ui_pyqt6.components.sidebar_qt import SidebarQt
from ui_pyqt6.components.header_bar_qt import HeaderBarQt
from ui_pyqt6.views.dashboard_view_qt import DashboardViewQt

from core.qt_tasks import BackgroundTasks
from core.config_manager import ConfigManager
from core.project_service import ProjectService
from core.tool_launcher import ToolLauncher
from i18n_helper import _, set_language

def get_thub_icon():
    """Finds and loads the highest-quality THub icon (.ico or .png)."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(base_dir, "assets", "THub.ico"),
        os.path.join(base_dir, "assets", "THub.png"),
    ]
    if hasattr(sys, '_MEIPASS'):
        candidates = [
            os.path.join(sys._MEIPASS, "assets", "THub.ico"),
            os.path.join(sys._MEIPASS, "assets", "THub.png"),
        ] + candidates

    for p in candidates:
        if p and os.path.exists(p):
            ico = QIcon(p)
            if not ico.isNull():
                return ico
    return QIcon()

class THubPyQt6App(QMainWindow):

    def __init__(self):
        super().__init__()

        self.tasks = BackgroundTasks(self)
        self._search_query = ""
        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(100)
        self._search_timer.timeout.connect(self._apply_search)
        self._knowledge_ready = False
        self._closing = False
        self._requested_route = "dashboard"

        # Core Services & Preferences
        self.cfg_manager = ConfigManager()
        saved_lang = self.cfg_manager.get("app_lang", "th")
        set_language(saved_lang)

        self.apply_theme()

        self.setWindowTitle(_("THub Launcher 2.2 - The Flagship Suite"))
        self.resize(1380, 840)
        self.setMinimumSize(1020, 640)

        # Set taskbar app ID on Windows
        if sys.platform == "win32":
            try:
                import ctypes
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('flagship.thub.launcher.pyqt6')
            except Exception:
                pass

        # Load Logo
        app_icon = get_thub_icon()
        if not app_icon.isNull():
            self.setWindowIcon(app_icon)

        self.project_service = ProjectService(self.cfg_manager)
        self.projects = self.project_service.get_all_projects(include_archived=True)
        self.active_project = self.projects[0] if self.projects else None

        # View instances (Lazy loaded on demand for instant startup!)
        self._views = {}

        self._build_shell()
        self.navigate_to("dashboard")

    def _build_shell(self):
        root_widget = QWidget(self)
        root_widget.setObjectName("MainRoot")
        self.setCentralWidget(root_widget)

        root_layout = QHBoxLayout(root_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1. Left Sidebar
        current_theme = self.cfg_manager.get("active_theme", "Dark")
        self.sidebar = SidebarQt(current_route="dashboard", current_theme=current_theme)
        self.sidebar.navigated.connect(self.navigate_to)
        self.sidebar.theme_picker_clicked.connect(self._open_theme_picker)
        self.sidebar.theme_toggle_clicked.connect(self._toggle_dark_light_theme)
        self.sidebar.lang_toggle_clicked.connect(self._toggle_language)
        self.sidebar.lang_selected.connect(self.set_app_language)
        root_layout.addWidget(self.sidebar)

        # 2. Main Content Column
        content_col = QWidget()
        col_layout = QVBoxLayout(content_col)
        col_layout.setContentsMargins(10, 8, 14, 10)
        col_layout.setSpacing(6)

        # 3. Top Header Bar
        active_count = sum(1 for p in self.projects if not p.get("is_archived", False))
        self.header_bar = HeaderBarQt(
            title="Dashboard",
            total_count=active_count
        )
        self.header_bar.search_changed.connect(self._on_search)
        self.header_bar.add_clicked.connect(self._open_add_wizard)
        self.header_bar.import_clicked.connect(self._open_import_wizard)
        self.header_bar.adopt_clicked.connect(lambda: self._open_adopt_wizard(self.active_project))
        col_layout.addWidget(self.header_bar)

        # 4. View Stack
        self.view_stack = QStackedWidget()
        col_layout.addWidget(self.view_stack)

        # Load Dashboard immediately (Primary view)
        self.dashboard_view = DashboardViewQt(self.projects)
        self.dashboard_view.tstudio_requested.connect(self._on_launch_tstudio)
        self.dashboard_view.ai_requested.connect(self._on_open_ai_for_project)
        self.dashboard_view.project_selected.connect(self._on_project_selected)
        self.dashboard_view.archive_toggled.connect(self._on_archive_toggled)
        self.dashboard_view.archive_requested.connect(self._on_archive_requested)
        self.dashboard_view.pin_toggled.connect(self._on_pin_toggled)
        self.dashboard_view.status_toggled.connect(self._on_status_toggled)
        self.dashboard_view.status_changed.connect(self._on_status_changed)
        self.dashboard_view.delete_requested.connect(self._on_delete_requested)
        self.dashboard_view.order_changed.connect(self._on_order_changed)
        self.dashboard_view.cover_edit_requested.connect(self._on_edit_cover)
        self.dashboard_view.engine_edit_requested.connect(self._on_edit_engine)
        self.dashboard_view.settings_requested.connect(self._on_edit_project_settings)
        self.dashboard_view.adopt_requested.connect(self._open_adopt_wizard)
        self.dashboard_view.move_requested.connect(self._open_move_dialog_for_project)
        self.dashboard_view.move_queue_requested.connect(self._open_move_queue_dialog)
        self.dashboard_view.counts_changed.connect(self.header_bar.update_counts)

        # Storage Telemetry Signal connections
        self.dashboard_view.storage_data_updated.connect(self.sidebar.update_storage_data)
        self.dashboard_view.storage_scanning_changed.connect(self.sidebar.set_storage_scanning)
        self.dashboard_view.storage_progress_changed.connect(self.sidebar.set_storage_progress)
        self.sidebar.project_selected.connect(self._on_sidebar_project_selected)
        self.sidebar.sort_size_requested.connect(self.dashboard_view._sort_projects_by_size)
        self.sidebar.refresh_requested.connect(self.dashboard_view._refresh_storage_scan)
        self.sidebar.move_queue_requested.connect(self._open_move_queue_dialog)
        # Resend initial cached storage sizes to populate the sidebar right away
        self.dashboard_view._apply_cached_storage_sizes()

        self.view_stack.addWidget(self.dashboard_view)
        self._views["dashboard"] = self.dashboard_view

        root_layout.addWidget(content_col, stretch=1)

    def navigate_to(self, route_id):
        self._requested_route = route_id
        if self._closing:
            return
        self.sidebar.set_active(route_id)
        if route_id in ("ai_helper", "knowledge") and not self._knowledge_ready:
            self.header_bar.set_title("กำลังโหลดคลังความรู้...")
            if "knowledge-init" not in self.tasks.jobs:
                def prepare():
                    from core.knowledge_service import KnowledgeService
                    from core.font_service import FontService
                    return KnowledgeService.get_instance(), FontService()
                self.tasks.submit("knowledge-init", prepare, self._services_loaded,
                                  lambda error: QMessageBox.warning(self, "โหลดคลังไม่สำเร็จ", error))
            return

        if route_id == "dashboard":
            self.header_bar.set_title("Dashboard (โปรเจกต์ม็อด)")
            active_count = sum(1 for p in self.projects if not p.get("is_archived", False))
            self.header_bar.update_counts(len(self.dashboard_view.filtered_projects), active_count)
            self.view_stack.setCurrentWidget(self.dashboard_view)

        elif route_id == "ai_helper":
            self.header_bar.set_title("🤖 AI Helper Copilot")
            if "ai_helper" not in self._views:
                from ui_pyqt6.views.ai_helper_view_qt import AIHelperViewQt
                view = AIHelperViewQt(self.projects, self.active_project, font_service=self._prepared_font_service)
                view.adopt_requested.connect(self._open_adopt_wizard)
                view.cover_updated.connect(self._on_cover_saved)
                self.view_stack.addWidget(view)

                self._views["ai_helper"] = view
            else:
                if self.active_project:
                    self._views["ai_helper"].set_project(self.active_project)
            self.view_stack.setCurrentWidget(self._views["ai_helper"])

        elif route_id == "apps":
            self.header_bar.set_title("✨ The Flagship Suite")
            if "apps" not in self._views:
                from ui_pyqt6.views.apps_view_qt import AppsViewQt
                view = AppsViewQt(self.active_project)
                self.view_stack.addWidget(view)
                self._views["apps"] = view
            else:
                self._views["apps"].active_project = self.active_project
            self.view_stack.setCurrentWidget(self._views["apps"])

        elif route_id == "knowledge":
            self.header_bar.set_title("📚 Modding Knowledge Base")
            if "knowledge" not in self._views:
                from ui_pyqt6.views.knowledge_view_qt import KnowledgeViewQt
                view = KnowledgeViewQt()
                self.view_stack.addWidget(view)
                self._views["knowledge"] = view
            self.view_stack.setCurrentWidget(self._views["knowledge"])

        elif route_id == "settings":
            self._open_global_settings()
            self.sidebar.set_active("dashboard")

    def _services_loaded(self, services):
        self._knowledge_ready = True
        self._prepared_font_service = services[1]
        self.navigate_to(self._requested_route)

    def _refresh_project_views(self):
        """Publish the current project registry to all instantiated THub views."""
        self.projects = self.project_service.get_all_projects(include_archived=True)
        active_key = (self.active_project or {}).get("path")
        self.active_project = next((p for p in self.projects if p.get("path") == active_key), self.projects[0] if self.projects else None)
        self.dashboard_view.update_projects(self.projects)
        ai_view = self._views.get("ai_helper")
        if ai_view:
            ai_view.active_project = self.active_project
            ai_view.update_projects(self.projects)
        apps = self._views.get("apps")
        if apps:
            apps.active_project = self.active_project

    def closeEvent(self, event):
        if not self._closing:
            self._closing = True
            self._search_timer.stop()
            self.dashboard_view.prepare_shutdown()
            self.tasks.cancel_all()
            # Modal dialogs may own media jobs or a project-move QThread.
            # Keep the application alive until those children also finish safely.
            for dialog in self.findChildren(QDialog):
                tasks = getattr(dialog, "tasks", None)
                if tasks:
                    tasks.cancel_all()
            for worker in self.findChildren(QThread):
                if worker.isRunning():
                    if hasattr(worker, "cancel"):
                        worker.cancel()
                    else:
                        worker.requestInterruption()
            for view in self._views.values():
                if view is not self.dashboard_view and hasattr(view, "tasks"):
                    timer = getattr(view, "_prompt_timer", None)
                    if timer:
                        timer.stop()
                    view.tasks.cancel_all()
        busy = self.dashboard_view.is_busy() or self.tasks.busy() or bool(BackgroundTasks._live)
        busy = busy or any(worker.isRunning() for worker in self.findChildren(QThread))
        busy = busy or any(view.tasks.busy() for view in self._views.values()
                           if view is not self.dashboard_view and hasattr(view, "tasks"))
        if busy:
            event.ignore()
            QTimer.singleShot(100, self.close)
            return
        if self.dashboard_view._dirty_notes:
            event.ignore()
            self._closing = False
            self.dashboard_view._closing = False
            self.tasks.closing = False
            for view in self._views.values():
                if hasattr(view, "tasks"):
                    view.tasks.closing = False
            self.dashboard_view.image_service.reopen()
            self.dashboard_view.apply_search_and_filter()
            QMessageBox.warning(self, "บันทึกโน้ตไม่สำเร็จ", "ยังมีโน้ตที่บันทึกไม่สำเร็จ กรุณาตรวจพื้นที่หรือสิทธิ์เขียนแล้วปิดอีกครั้ง")
            return
        event.accept()

    def _on_search(self, query):
        if self.view_stack.currentWidget() == self.dashboard_view:
            self._search_query = query
            self._search_timer.start()

    def _apply_search(self):
        if not self._closing and self.view_stack.currentWidget() == self.dashboard_view:
            self.dashboard_view.apply_search_and_filter(self._search_query)

    def _on_launch_tstudio(self, project):
        if not project or not isinstance(project, dict):
            return
        self.active_project = project
        p_path = project.get("path")
        try:
            ToolLauncher.launch_tstudio_for_project(p_path)
        except Exception as e:
            QMessageBox.critical(self, "Launch Error", f"ไม่สามารถเปิด TStudio ได้:\n{e}")

    def _on_open_ai_for_project(self, project):
        """Spotlight: Jumps straight to AI Helper with this project preselected!"""
        self.active_project = project
        self.navigate_to("ai_helper")

    def _on_project_selected(self, project):
        self.active_project = project

    def _on_sidebar_project_selected(self, project):
        if not project:
            return
        self.active_project = project
        if self.view_stack.currentWidget() != self.dashboard_view:
            self.navigate_to("dashboard")
        self.dashboard_view.select_project(project)

    def _open_add_wizard(self):
        from ui_pyqt6.dialogs.project_wizard_qt import ProjectWizardDialogQt
        wiz = ProjectWizardDialogQt(is_import_mode=False, parent=self)
        wiz.project_created.connect(self._on_project_created)
        wiz.exec()

    def _open_import_wizard(self):
        from ui_pyqt6.dialogs.project_wizard_qt import ProjectWizardDialogQt
        wiz = ProjectWizardDialogQt(is_import_mode=True, parent=self)
        wiz.project_created.connect(self._on_project_created)
        wiz.exec()

    def _open_adopt_wizard(self, project=None):
        from ui_pyqt6.dialogs.mod_adoption_wizard_dialog_qt import ModAdoptionWizardDialogQt
        init_path = ""
        if isinstance(project, dict):
            init_path = project.get("path", "")
        wiz = ModAdoptionWizardDialogQt(initial_path=init_path, parent=self)
        wiz.adoption_completed.connect(self._on_adoption_completed)
        wiz.exec()

    def _on_adoption_completed(self, project_entry, open_ai):
        self.projects = self.project_service.get_all_projects(include_archived=True)
        self._refresh_project_views()

        active_count = sum(1 for p in self.projects if not p.get("is_archived", False))
        self.header_bar.update_counts(len(self.dashboard_view.filtered_projects), active_count)

        target_proj = None
        p_name = project_entry.get("name") if isinstance(project_entry, dict) else ""
        for p in self.projects:
            if p.get("name") == p_name:
                target_proj = p
                break
        if not target_proj and self.projects:
            target_proj = self.projects[0]

        if target_proj:
            self.active_project = target_proj

        if open_ai and target_proj:
            self.navigate_to("ai_helper")
            ai_view = self._views.get("ai_helper")
            if ai_view:
                ai_view.set_project(target_proj)
                ai_view.set_prompt_type("continue")

    def _on_archive_toggled(self, project):
        p_name = project.get("name")
        is_archived = project.get("is_archived", False)
        if is_archived:
            self.project_service.set_archive(p_name, is_archived=False)
        else:
            from ui_pyqt6.dialogs.archive_select_dialog_qt import ArchiveSelectDialogQt
            chosen = ArchiveSelectDialogQt.get_archive_choice(self, p_name)
            if chosen:
                self.project_service.set_archive(p_name, is_archived=True, status=chosen)
            else:
                return
        self.projects = self.project_service.get_all_projects(include_archived=True)
        QTimer.singleShot(0, lambda: self._refresh_project_views())

    def _on_archive_requested(self, project, status):
        p_name = project.get("name")
        if status == "unarchive":
            self.project_service.set_archive(p_name, is_archived=False)
        else:
            self.project_service.set_archive(p_name, is_archived=True, status=status)
        self.projects = self.project_service.get_all_projects(include_archived=True)
        QTimer.singleShot(0, lambda: self._refresh_project_views())

    def _on_pin_toggled(self, project):
        p_name = project.get("name")
        self.project_service.toggle_pin(p_name)
        self.projects = self.project_service.get_all_projects(include_archived=True)
        QTimer.singleShot(0, lambda: self._refresh_project_views())

    def _on_status_toggled(self, project):
        p_name = project.get("name")
        updated = self.project_service.toggle_status(p_name)
        self.projects = self.project_service.get_all_projects(include_archived=True)
        if self.active_project and self.active_project.get("name") == p_name:
            self.active_project = updated or project
        QTimer.singleShot(0, lambda: self._refresh_project_views())

    def _on_status_changed(self, project, new_status):
        p_name = project.get("name")
        updated = self.project_service.set_status(p_name, new_status)
        self.projects = self.project_service.get_all_projects(include_archived=True)
        if self.active_project and self.active_project.get("name") == p_name:
            self.active_project = updated or project
        QTimer.singleShot(0, lambda: self._refresh_project_views())

    def _on_delete_requested(self, project):
        p_name = project.get("name")
        reply = QMessageBox.question(
            self,
            "ยืนยันการลบโปรเจกต์",
            f"คุณต้องการลบโปรเจกต์ '{p_name}' ออกจาก THub หรือไม่?\n\n(ไฟล์เกมและโฟลเดอร์ในคอมพิวเตอร์จะไม่ถูกลบ)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.project_service.delete_project(p_name)
            self.projects = self.project_service.get_all_projects(include_archived=True)
            QTimer.singleShot(0, lambda: self._refresh_project_views())

    def _on_order_changed(self, new_order):
        self.projects = new_order
        self.project_service.save_project_order(new_order)

    def _on_edit_cover(self, project):
        from ui_pyqt6.dialogs.cover_editor_dialog_qt import CoverEditorDialogQt
        dlg = CoverEditorDialogQt(project, parent=self)
        dlg.cover_saved.connect(self._on_cover_saved)
        dlg.exec()

    def _on_cover_saved(self, updated_project):
        from ui_pyqt6.components.project_card_qt import ProjectCardQt
        ProjectCardQt.clear_pixmap_cache()

        p_name = updated_project.get("name")
        for idx, p in enumerate(self.projects):
            if p.get("name") == p_name:
                self.projects[idx] = updated_project
                break
        self.project_service.save_project_order(self.projects)
        self._refresh_project_views()


    def _on_edit_engine(self, project):
        from ui_pyqt6.dialogs.engine_select_dialog_qt import EngineSelectDialogQt
        dlg = EngineSelectDialogQt(project, parent=self)
        dlg.engine_saved.connect(self._on_engine_saved)
        dlg.exec()

    def _on_engine_saved(self, updated_project):
        p_name = updated_project.get("name")
        engine_name = updated_project.get("engine", "Custom Engine")
        engine_color = updated_project.get("engine_color", "#94a3b8")
        self.project_service.update_project_engine(p_name, engine_name, engine_color)
        self.projects = self.project_service.get_all_projects(include_archived=True)
        self._refresh_project_views()


    def _on_edit_project_settings(self, project):
        from ui_pyqt6.dialogs.project_settings_dialog_qt import ProjectSettingsDialogQt
        dlg = ProjectSettingsDialogQt(project, parent=self)
        dlg.project_updated.connect(self._on_project_settings_saved)
        dlg.exec()

    def _on_project_settings_saved(self, updated_project):
        self.projects = self.project_service.get_all_projects(include_archived=True)
        if self.active_project and self.active_project.get("name") == updated_project.get("name"):
            self.active_project = updated_project
        self._refresh_project_views()

    def _open_move_dialog_for_project(self, project):
        self._open_move_queue_dialog(preselected_project=project)

    def _open_move_queue_dialog(self, preselected_project=None):
        from ui_pyqt6.dialogs.project_move_queue_dialog_qt import ProjectMoveQueueDialogQt
        dlg = ProjectMoveQueueDialogQt(self.projects, preselected_project=preselected_project, parent=self)
        dlg.projects_moved.connect(self._on_projects_moved)
        dlg.exec()

    def _on_projects_moved(self, moved_list):
        self.projects = self.project_service.get_all_projects(include_archived=True)
        if self.active_project:
            for name, new_path in moved_list:
                if self.active_project.get("name") == name:
                    self.active_project["path"] = new_path
        self._refresh_project_views()
        self.dashboard_view._refresh_storage_scan()

    def _open_global_settings(self):
        from ui_pyqt6.dialogs.settings_dialog_qt import SettingsDialogQt
        dlg = SettingsDialogQt(parent=self)
        dlg.settings_saved.connect(self._on_global_settings_saved)
        dlg.exec()

    def _open_theme_picker(self):
        from ui_pyqt6.dialogs.theme_picker_dialog import ThemePickerDialog
        current_theme = self.cfg_manager.get("active_theme", "Dark")
        dlg = ThemePickerDialog(current_theme=current_theme, parent=self)
        dlg.theme_selected.connect(self.apply_theme)
        dlg.show_at_widget(self.sidebar.btn_theme_picker)

    def _toggle_dark_light_theme(self):
        """Quick 1-click toggle between Dark and Light mode."""
        current = self.cfg_manager.get("active_theme", "Dark").lower()
        palette = get_theme_palette(current)
        if palette.get("is_light", False):
            next_theme = "dark"
        else:
            next_theme = "light"
        self.apply_theme(next_theme)

    def _toggle_language(self):
        """Quick 1-click toggle between Thai and English."""
        current_lang = self.cfg_manager.get("app_lang", "th")
        next_lang = "en" if current_lang == "th" else "th"
        self.set_app_language(next_lang)

    def set_app_language(self, lang_code: str):
        """Set application language dynamically, auto-save to config, and retranslate UI live."""
        self.cfg_manager.set("app_lang", lang_code, auto_save=True)
        set_language(lang_code)
        self.retranslate_ui()

    def apply_theme(self, theme_name=None):
        if theme_name:
            self.cfg_manager.set("active_theme", theme_name, auto_save=True)
            theme = theme_name
        else:
            theme = self.cfg_manager.get("active_theme", "Dark")
        qss = get_theme_stylesheet(theme)
        app = QApplication.instance()
        if app and app.styleSheet() != qss:
            app.setStyleSheet(qss)
        # Global Qt styling already reaches this window and its children. Applying
        # the same sheet locally repeats selector matching for every new card.
        if hasattr(self, "sidebar"):
            self.sidebar.update_theme_display(theme)

    def retranslate_ui(self):
        self.setWindowTitle(_("THub Launcher 2.2 - The Flagship Suite"))
        if hasattr(self, "sidebar"):
            self.sidebar.retranslate_ui()
        if hasattr(self, "header_bar"):
            self.header_bar.retranslate_ui()
        if hasattr(self, "dashboard_view"):
            self.dashboard_view.retranslate_ui()
        for v in getattr(self, "_views", {}).values():
            if hasattr(v, "retranslate_ui") and v != getattr(self, "dashboard_view", None):
                try:
                    v.retranslate_ui()
                except Exception:
                    pass

    def _on_global_settings_saved(self):
        self.apply_theme()
        self.retranslate_ui()
        self.projects = self.project_service.get_all_projects(include_archived=True)
        self._refresh_project_views()


    def _on_project_created(self, new_proj):
        self.projects = self.project_service.get_all_projects(include_archived=True)
        self.active_project = new_proj
        self._refresh_project_views()


def setup_crash_logger():
    """Installs global exception hook to prevent silent aborts in PyQt6 and log errors."""
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workspace", "logs")
    os.makedirs(log_dir, exist_ok=True)
    crash_log_file = os.path.join(log_dir, "crash_debug.log")

    class SafeStderr:
        def write(self, s):
            try:
                with open(crash_log_file, "a", encoding="utf-8", errors="replace") as f:
                    f.write(s)
            except Exception:
                pass
        def flush(self):
            pass

    if sys.stderr is None:
        sys.stderr = SafeStderr()
    if sys.stdout is None:
        sys.stdout = SafeStderr()

    def global_excepthook(exc_type, exc_value, exc_tb):
        import traceback
        from datetime import datetime
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_tb)
        full_msg = f"\n[{now_str}] UNHANDLED EXCEPTION:\n" + "".join(tb_lines)

        try:
            with open(crash_log_file, "a", encoding="utf-8", errors="replace") as f:
                f.write(full_msg + "\n" + "="*60 + "\n")
        except Exception:
            pass

        try:
            if QApplication.instance():
                err_summary = str(exc_value) or str(exc_type.__name__)
                QMessageBox.warning(
                    None,
                    "THub - แจ้งเตือนข้อผิดพลาด",
                    f"เกิดข้อผิดพลาดในการทำงาน:\n{err_summary}\n\nบันทึกประวัติข้อผิดพลาดไว้ที่ workspace/logs/crash_debug.log เรียบร้อยแล้ว",
                    QMessageBox.StandardButton.Ok
                )
        except Exception:
            pass

    sys.excepthook = global_excepthook

def main():
    if '--smoke-test' in sys.argv and not os.environ.get('THUB_CONFIG_PATH'):
        raise RuntimeError('Smoke tests require an isolated THUB_CONFIG_PATH')
    setup_crash_logger()
    # ── Multi-Call Binary / CLI & Tool Dispatcher ──
    # When packaged with PyInstaller, sys.executable points to THub.exe.
    # When launching flagship tools (TStudio, TRun, TPUA, TGlyph),
    # ToolLauncher executes THub.exe with the tool script as an argument.
    # Intercept this and execute the requested tool via runpy to prevent
    # spawning a duplicate THub launcher window.
    if len(sys.argv) > 1:
        target_script = None
        remaining_args = []
        arg1 = sys.argv[1]

        if arg1 in ("--tool", "-t") and len(sys.argv) > 2:
            tool_name = sys.argv[2].lower()
            remaining_args = sys.argv[3:]
            search_roots = [
                getattr(sys, '_MEIPASS', ''),
                os.path.dirname(sys.executable),
                os.path.dirname(os.path.abspath(__file__)),
            ]
            script_rel = {
                "tstudio": os.path.join("tools", "flagship", "TStudio", "tstudio_app.py"),
                "trun": os.path.join("tools", "flagship", "TRun", "trun_app.py"),
                "tpua": os.path.join("tools", "flagship", "TPUA", "tpua_app.py"),
                "tglyph": os.path.join("tools", "flagship", "TGlyph", "tglyph_app.py"),
            }.get(tool_name)
            if script_rel:
                for root in search_roots:
                    if root:
                        cand = os.path.join(root, script_rel)
                        if os.path.exists(cand):
                            target_script = cand
                            break
        elif arg1 in ("--script", "-s") and len(sys.argv) > 2:
            target_script = sys.argv[2]
            remaining_args = sys.argv[3:]
        elif arg1.endswith(".py") or (os.path.exists(arg1) and not os.path.isdir(arg1)):
            target_script = arg1
            remaining_args = sys.argv[2:]

        if target_script:
            if not os.path.isabs(target_script):
                search_roots = [
                    os.getcwd(),
                    getattr(sys, '_MEIPASS', ''),
                    os.path.dirname(sys.executable),
                    os.path.dirname(os.path.abspath(__file__)),
                ]
                for root in search_roots:
                    if root:
                        cand = os.path.abspath(os.path.join(root, target_script))
                        if os.path.exists(cand):
                            target_script = cand
                            break

            if os.path.exists(target_script):
                target_script = os.path.abspath(target_script)
                target_dir = os.path.dirname(target_script)
                core_dir = os.path.abspath(os.path.join(target_dir, "..", "Core"))

                if core_dir not in sys.path and os.path.exists(core_dir):
                    sys.path.insert(0, core_dir)
                if target_dir not in sys.path:
                    sys.path.insert(0, target_dir)

                sys.argv = [target_script] + remaining_args
                try:
                    os.chdir(target_dir)
                except Exception:
                    pass

                import runpy
                try:
                    runpy.run_path(target_script, run_name="__main__")
                    sys.exit(0)
                except SystemExit as se:
                    sys.exit(se.code if se.code is not None else 0)
                except Exception:
                    import traceback
                    traceback.print_exc()
                    sys.exit(1)

    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('flagship.thub.launcher.pyqt6')
        except Exception:
            pass

    app = QApplication(sys.argv)
    app_icon = get_thub_icon()
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)

    cfg = ConfigManager()
    saved_lang = cfg.get("app_lang", "th")
    set_language(saved_lang)
    saved_theme = cfg.get("active_theme", "Obsidian")

    # Anti-flicker: Pre-populate dark palette to prevent white/grey OS native window frame flash
    palette_data = get_theme_palette(saved_theme)
    bg_canvas = QColor(palette_data.get("bg_canvas", "#0b0e14"))
    pal = app.palette()
    pal.setColor(QPalette.ColorRole.Window, bg_canvas)
    pal.setColor(QPalette.ColorRole.Base, bg_canvas)
    app.setPalette(pal)

    app.setStyleSheet(get_theme_stylesheet(saved_theme))
    win = THubPyQt6App()

    # Fit window comfortably within screen working area and center it
    screen = app.primaryScreen()
    if screen:
        avail = screen.availableGeometry()
        target_w = min(1380, int(avail.width() * 0.96))
        target_h = min(840, int(avail.height() * 0.92))
        win.resize(target_w, target_h)
        x = avail.x() + (avail.width() - target_w) // 2
        y = avail.y() + (avail.height() - target_h) // 2
        win.move(x, y)

    win.show()
    if '--smoke-test' in sys.argv:
        def smoke_result():
            from core.safe_io import write_json_atomic
            result_path = os.environ.get('THUB_SMOKE_RESULT')
            if result_path:
                write_json_atomic(result_path, {
                    'ok': not win.dashboard_view._dirty_notes and not BackgroundTasks._live,
                    'frozen': bool(getattr(sys, 'frozen', False)),
                    'config_path': win.cfg_manager.config_path,
                    'modules': {name: getattr(sys.modules.get(name), '__file__', None) for name in (
                        'core.qt_tasks', 'core.project_backup', 'core.workspace_schema',
                        'ui_pyqt6.dialogs.bible_viewer_dialog_qt')},
                })
        app.aboutToQuit.connect(smoke_result)
        QTimer.singleShot(1200, win.close)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
