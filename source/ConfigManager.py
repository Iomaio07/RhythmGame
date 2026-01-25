class ConfigManager:
    def __init__(self, filename='config.txt'):
        self.filename = filename
        self.default_config = {
            'master_volume': 100,
            'music_volume': 100,
            'sfx_volume': 100,
            'fps': 60
        }

    def load_config(self):
        """Загружает настройки из файла"""
        try:
            config = {}
            with open(self.filename, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()

            for key in self.default_config:
                if key not in config:
                    config[key] = str(self.default_config[key])

            return config
        except FileNotFoundError:
            self.save_config(self.default_config)
            return self.default_config

    def save_config(self, config):
        with open(self.filename, 'w', encoding='utf-8') as f:
            for key, value in config.items():
                f.write(f"{key}={value}\n")

    def load_settings_to_vars(self):
        global master_volume, music_volume, sfx_volume, fps

        config = self.load_config()

        master_volume = int(config.get('master_volume', 100)) / 100
        music_volume = int(config.get('music_volume', 100)) / 100
        sfx_volume = int(config.get('sfx_volume', 100)) / 100
        fps = int(config.get('fps', 60))

        return {
            'master_volume': int(config.get('master_volume', 100)),
            'music_volume': int(config.get('music_volume', 100)),
            'sfx_volume': int(config.get('sfx_volume', 100)),
            'fps': str(config.get('fps', 60))
        }
