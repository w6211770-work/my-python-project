from path_resolver import PathResolver


class Config:
    """設定値を扱うクラス（読み込みは一度だけ）"""

    _config = None

    @classmethod
    def load(cls):
        if cls._config is None:
            cls._config = PathResolver.load_config()
        return cls._config

    @classmethod
    def get(cls, key, default=None):
        config = cls.load()
        return config.get(key, default)
