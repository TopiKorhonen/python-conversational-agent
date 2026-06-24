from pathlib import Path

class MascotController:
    def __init__(self, assets_dir: Path):
        self.assets_dir = assets_dir.resolve()
        self.image_map = {
            "happy": "happy.png",
            "neutral": "neutral.png",
            "concerned": "sus.png",
            "thinking": "thinking.png",
            "listening": "thinking.png"
        }

    def get_image_path(self, emotion: str) -> Path:
        image_name = self.image_map.get(emotion, "neutral.png")
        return (self.assets_dir / image_name).resolve()