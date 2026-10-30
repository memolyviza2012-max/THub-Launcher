import os
import sys
import subprocess

class ToolLauncher:
    """Safely launches Flagship Suite and third-party tools with workspace context."""

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    FLAGSHIP_DIR = os.path.join(BASE_DIR, "tools", "flagship")

    FLAGSHIP_TOOLS = {
        "TStudio": {
            "name": "TStudio",
            "desc": "Universal Line-by-Line AI Translation Studio",
            "script": os.path.join("TStudio", "tstudio_app.py"),
            "color": "#38bdf8", # Cyan
            "supports_project": True
        },
        "TRun": {
            "name": "TRun",
            "desc": "Batch Automated Translation Runner",
            "script": os.path.join("TRun", "trun_app.py"),
            "color": "#22c55e", # Green
            "supports_project": True
        },
        "TPUA": {
            "name": "TPUA",
            "desc": "Private Use Area Thai Font Manager",
            "script": os.path.join("TPUA", "tpua_app.py"),
            "color": "#c084fc", # Purple
            "supports_project": False
        },
        "TGlyph": {
            "name": "TGlyph",
            "desc": "Font Atlas & Texture Generator",
            "script": os.path.join("TGlyph", "tglyph_app.py"),
            "color": "#fb923c", # Orange
            "supports_project": False
        }
    }

    @classmethod
    def get_flagship_dir(cls):
        """Resolves the flagship tools directory across dev and frozen environments."""
        candidates = []
        if getattr(sys, 'frozen', False):
            if hasattr(sys, '_MEIPASS'):
                candidates.append(os.path.join(sys._MEIPASS, "tools", "flagship"))
            candidates.append(os.path.join(os.path.dirname(sys.executable), "_internal", "tools", "flagship"))
            candidates.append(os.path.join(os.path.dirname(sys.executable), "tools", "flagship"))
        candidates.append(os.path.join(cls.BASE_DIR, "tools", "flagship"))
        candidates.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools", "flagship")))
        for c in candidates:
            if c and os.path.isdir(c):
                return os.path.abspath(c)
        return cls.FLAGSHIP_DIR

    @classmethod
    def launch_flagship(cls, tool_id, project_path=None):
        """Launches a Flagship tool (e.g. TStudio) with optional project context."""
        info = cls.FLAGSHIP_TOOLS.get(tool_id)
        if not info:
            raise ValueError(f"Unknown flagship tool: {tool_id}")

        flagship_dir = cls.get_flagship_dir()
        full_script = os.path.join(flagship_dir, info["script"])
        if not os.path.exists(full_script):
            raise FileNotFoundError(f"Script not found at: {full_script}")

        cmd = [sys.executable, full_script]
        if project_path and info["supports_project"]:
            cmd.append(project_path)

        work_dir = os.path.dirname(full_script)
        # Windows creation flag for detached background process
        creation_flags = 0x00000008 if sys.platform == "win32" else 0

        # Redirect stderr to a log file so crashes and errors are never silently swallowed
        app_base = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else cls.BASE_DIR
        log_dir = os.path.join(app_base, "workspace", "logs")
        try:
            os.makedirs(log_dir, exist_ok=True)
            err_log_path = os.path.join(log_dir, f"{tool_id}.log")
            err_target = open(err_log_path, "w", encoding="utf-8", errors="replace")
        except Exception:
            err_target = subprocess.DEVNULL

        try:
            proc = subprocess.Popen(
                cmd, cwd=work_dir, creationflags=creation_flags,
                stdout=subprocess.DEVNULL, stderr=err_target
            )
        finally:
            if hasattr(err_target, "close"):
                err_target.close()
        return proc

    @classmethod
    def launch_tstudio_for_project(cls, project_path):
        """Dedicated high-priority launcher for TStudio."""
        return cls.launch_flagship("TStudio", project_path=project_path)

    @classmethod
    def launch_trun_for_project(cls, project_path):
        """Dedicated high-priority launcher for TRun."""
        return cls.launch_flagship("TRun", project_path=project_path)

    @classmethod
    def open_folder(cls, path):
        """Opens folder in Windows Explorer."""
        if os.path.exists(path):
            if sys.platform == "win32":
                os.startfile(os.path.abspath(path))
            else:
                subprocess.Popen(["xdg-open", path])
