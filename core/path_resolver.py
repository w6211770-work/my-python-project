# from pathlib import Path
#
#
# class PathResolver:
#     """プロジェクト内のパスを一元管理するクラス"""
#
#     # core フォルダのパス
#     CORE_DIR = Path(__file__).resolve().parent
#
#     # プロジェクトルート（core の 1 つ上）
#     ROOT_DIR = CORE_DIR.parent
#
#     # data フォルダ
#     DATA_DIR = ROOT_DIR / "data"
#
#     # python_scripts フォルダ
#     PYTHON_SCRIPTS_DIR = DATA_DIR / "python_scripts"
#
#     @staticmethod
#     def script_path(filename: str) -> Path:
#         """python_scripts 内の特定ファイルのパスを返す"""
#         return PathResolver.PYTHON_SCRIPTS_DIR / filename
# from pathlib import Path
# import json
#
#
# class PathResolver:
#     """プロジェクト内のパスを一元管理するクラス"""
#
#     CORE_DIR = Path(__file__).resolve().parent
#     ROOT_DIR = CORE_DIR.parent
#
#     DATA_DIR = ROOT_DIR / "data"
#     PYTHON_SCRIPTS_DIR = DATA_DIR / "python_scripts"
#     CONFIG_FILE = DATA_DIR / "config.json"
#
#     @staticmethod
#     def script_path(filename: str) -> Path:
#         return PathResolver.PYTHON_SCRIPTS_DIR / filename
#
#     @staticmethod
#     def load_config() -> dict:
#         """config.json を読み込んで dict を返す"""
#         if not PathResolver.CONFIG_FILE.exists():
#             raise FileNotFoundError("config.json が見つかりません")
#
#         with open(PathResolver.CONFIG_FILE, "r", encoding="utf-8") as f:
#             return json.load(f)
from pathlib import Path
import json


class PathResolver:
    CORE_DIR = Path(__file__).resolve().parent
    ROOT_DIR = CORE_DIR.parent

    DATA_DIR = ROOT_DIR / "data"
    PYTHON_SCRIPTS_DIR = DATA_DIR / "python_scripts"
    CONFIG_FILE = DATA_DIR / "config.json"

    # ★ ログファイルのパスを追加
    KEY_MOUSE_LOG_FILE = DATA_DIR / "key_mouse_log.txt"

    @staticmethod
    def script_path(filename: str) -> Path:
        return PathResolver.PYTHON_SCRIPTS_DIR / filename

    @staticmethod
    def load_config() -> dict:
        """config.json を読み込んで dict を返す"""
        if not PathResolver.CONFIG_FILE.exists():
            raise FileNotFoundError("config.json が見つかりません")

        with open(PathResolver.CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def list_python_scripts():
        folder = PathResolver.PYTHON_SCRIPTS_DIR
        return [p.name for p in folder.glob("*.py")]

