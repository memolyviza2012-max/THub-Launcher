import os
import sys
import time
import shutil
import requests
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, 
    QListWidget, QPushButton, QLabel, QMessageBox, QFileDialog, QListWidgetItem
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from tstudio_i18n import _
import file_converter

class FetchCloudPluginsThread(QThread):
    finished_signal = pyqtSignal(list, str)
    
    def run(self):
        url = "https://api.github.com/repos/memolyviza2012-max/TFormat-Plugins/contents/"
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                data = res.json()
                plugins = [item for item in data if item.get("name", "").endswith("_parser.py")]
                self.finished_signal.emit(plugins, "")
            else:
                self.finished_signal.emit([], f"GitHub API Error: {res.status_code}")
        except Exception as e:
            self.finished_signal.emit([], f"Network Error: {str(e)}")

class DownloadPluginThread(QThread):
    finished_signal = pyqtSignal(bool, str)
    
    def __init__(self, download_url, save_path):
        super().__init__()
        self.download_url = download_url
        self.save_path = save_path
        
    def run(self):
        try:
            url = f"{self.download_url}?t={int(time.time())}"
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                with open(self.save_path, 'w', encoding='utf-8') as f:
                    f.write(res.text)
                self.finished_signal.emit(True, "")
            else:
                self.finished_signal.emit(False, f"Download failed with status {res.status_code}")
        except Exception as e:
            self.finished_signal.emit(False, f"Download error: {str(e)}")

class PluginManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("plugin_manager_title"))
        self.resize(500, 400)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        
        self.parsers_dir = file_converter.CUSTOM_PARSERS_DIR
        
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        self.init_installed_tab()
        self.init_cloud_tab()
        
    def init_installed_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.installed_list = QListWidget()
        self.installed_list.setStyleSheet("QListWidget { background-color: #1a2332; }")
        layout.addWidget(self.installed_list)
        
        btn_layout = QHBoxLayout()
        self.btn_add_local = QPushButton(_("plugin_btn_add_manual"))
        self.btn_add_local.clicked.connect(self.add_local_plugin)
        
        self.btn_delete = QPushButton(_("plugin_btn_delete"))
        self.btn_delete.clicked.connect(self.delete_plugin)
        
        btn_layout.addWidget(self.btn_add_local)
        btn_layout.addWidget(self.btn_delete)
        layout.addLayout(btn_layout)
        
        self.tabs.addTab(tab, _("plugin_tab_installed"))
        self.refresh_installed_list()
        
    def init_cloud_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.cloud_list = QListWidget()
        self.cloud_list.setStyleSheet("QListWidget { background-color: #2d1a32; }")
        layout.addWidget(self.cloud_list)
        
        btn_layout = QHBoxLayout()
        self.btn_refresh_cloud = QPushButton(_("plugin_btn_refresh"))
        self.btn_refresh_cloud.clicked.connect(self.fetch_cloud_plugins)
        
        self.btn_install_cloud = QPushButton(_("plugin_btn_download"))
        self.btn_install_cloud.clicked.connect(self.install_cloud_plugin)
        
        self.btn_install_all_cloud = QPushButton("Download/Update All")
        self.btn_install_all_cloud.clicked.connect(self.install_all_cloud_plugins)
        
        btn_layout.addWidget(self.btn_refresh_cloud)
        btn_layout.addWidget(self.btn_install_cloud)
        btn_layout.addWidget(self.btn_install_all_cloud)
        layout.addLayout(btn_layout)
        
        self.tabs.addTab(tab, _("plugin_tab_cloud"))
        self.fetch_cloud_plugins()
        
    def refresh_installed_list(self):
        self.installed_list.clear()
        if not os.path.exists(self.parsers_dir):
            return
        for file in os.listdir(self.parsers_dir):
            if file.endswith("_parser.py"):
                self.installed_list.addItem(file)
                
    def add_local_plugin(self):
        file_path, _ = QFileDialog.getOpenFileName(self, _("plugin_select_file_title"), "", _("plugin_python_files_filter"))
        if file_path:
            filename = os.path.basename(file_path)
            if not filename.endswith(".py"):
                QMessageBox.warning(self, _("plugin_invalid_file_title"), _("plugin_err_invalid_filename"))
                return
                
            dest = os.path.join(self.parsers_dir, filename)
            try:
                shutil.copy2(file_path, dest)
                QMessageBox.information(self, _("success_title"), _("plugin_success_install_manual", filename=filename))
                self.refresh_installed_list()
            except Exception as e:
                QMessageBox.critical(self, _("error_title"), _("plugin_err_install_manual", msg=str(e)))
                
    def delete_plugin(self):
        item = self.installed_list.currentItem()
        if not item:
            QMessageBox.warning(self, _("Warning"), _("plugin_warn_select_delete"))
            return
            
        filename = item.text()
        reply = QMessageBox.question(self, _("plugin_confirm_delete_title"), _("plugin_confirm_delete", filename=filename),
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                                     
        if reply == QMessageBox.StandardButton.Yes:
            try:
                os.remove(os.path.join(self.parsers_dir, filename))
                self.refresh_installed_list()
            except Exception as e:
                QMessageBox.critical(self, _("error_title"), _("plugin_err_delete", msg=str(e)))
                
    def fetch_cloud_plugins(self):
        self.cloud_list.clear()
        self.cloud_list.addItem(_("plugin_status_loading_cloud"))
        self.btn_refresh_cloud.setEnabled(False)
        self.btn_install_cloud.setEnabled(False)
        
        self.fetch_thread = FetchCloudPluginsThread()
        self.fetch_thread.finished_signal.connect(self.on_cloud_fetched)
        self.fetch_thread.start()
        
    def on_cloud_fetched(self, plugins, error_msg):
        self.cloud_list.clear()
        self.btn_refresh_cloud.setEnabled(True)
        self.btn_install_cloud.setEnabled(True)
        
        if error_msg:
            self.cloud_list.addItem(f"Failed to load: {error_msg}")
            return
            
        if not plugins:
            self.cloud_list.addItem(_("plugin_status_no_cloud"))
            return
            
        for plugin in plugins:
            item = QListWidgetItem(plugin.get("name", "Unknown"))
            # Store the raw download url in user data
            item.setData(Qt.ItemDataRole.UserRole, plugin.get("download_url", ""))
            self.cloud_list.addItem(item)
            
    def install_cloud_plugin(self):
        item = self.cloud_list.currentItem()
        if not item or not item.data(Qt.ItemDataRole.UserRole):
            QMessageBox.warning(self, _("Warning"), _("plugin_warn_select_download"))
            return
            
        filename = item.text()
        download_url = item.data(Qt.ItemDataRole.UserRole)
        save_path = os.path.join(self.parsers_dir, filename)
        
        self.btn_install_cloud.setEnabled(False)
        self.btn_install_cloud.setText(_("plugin_status_downloading", filename=filename))
        
        self.dl_thread = DownloadPluginThread(download_url, save_path)
        self.dl_thread.finished_signal.connect(lambda success, msg: self.on_plugin_downloaded(success, msg, filename))
        self.dl_thread.start()
        
    def on_plugin_downloaded(self, success, msg, filename):
        self.btn_install_cloud.setEnabled(True)
        self.btn_install_cloud.setText(_("plugin_btn_download"))
        
        if success:
            QMessageBox.information(self, _("success_title"), _("plugin_success_download", filename=filename))
            self.refresh_installed_list()
        else:
            QMessageBox.critical(self, _("error_title"), _("plugin_err_download", msg=msg))

    def install_all_cloud_plugins(self):
        self.download_queue = []
        for i in range(self.cloud_list.count()):
            item = self.cloud_list.item(i)
            url = item.data(Qt.ItemDataRole.UserRole)
            if url:
                self.download_queue.append((item.text(), url))
        
        if not self.download_queue:
            return
            
        self.btn_install_all_cloud.setEnabled(False)
        self.btn_install_cloud.setEnabled(False)
        self.btn_refresh_cloud.setEnabled(False)
        self._process_next_download()
        
    def _process_next_download(self):
        if not hasattr(self, 'download_queue') or not self.download_queue:
            self.btn_install_all_cloud.setEnabled(True)
            self.btn_install_cloud.setEnabled(True)
            self.btn_refresh_cloud.setEnabled(True)
            self.btn_install_all_cloud.setText("Download/Update All")
            QMessageBox.information(self, _("success_title"), "Downloaded and updated all plugins successfully!")
            self.refresh_installed_list()
            return
            
        filename, download_url = self.download_queue.pop(0)
        save_path = os.path.join(self.parsers_dir, filename)
        
        self.btn_install_all_cloud.setText(f"Downloading {filename}...")
        
        self.dl_thread = DownloadPluginThread(download_url, save_path)
        self.dl_thread.finished_signal.connect(self._on_single_queue_downloaded)
        self.dl_thread.start()
        
    def _on_single_queue_downloaded(self, success, msg):
        self._process_next_download()
