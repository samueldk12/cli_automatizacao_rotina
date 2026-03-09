from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Monitor:
    index: int
    x: int
    y: int
    width: int
    height: int
    is_primary: bool = True
    name: str = ""

    def __str__(self) -> str:
        primary = " [primário]" if self.is_primary else ""
        return f"Monitor {self.index + 1}: {self.width}x{self.height} @ ({self.x},{self.y}){primary}"


def get_monitors() -> List[Monitor]:
    """Detecta todos os monitores conectados."""
    try:
        import screeninfo

        result = []
        for i, m in enumerate(screeninfo.get_monitors()):
            result.append(
                Monitor(
                    index=i,
                    x=m.x,
                    y=m.y,
                    width=m.width,
                    height=m.height,
                    is_primary=getattr(m, "is_primary", i == 0),
                    name=getattr(m, "name", f"Monitor {i + 1}"),
                )
            )
        return result if result else [Monitor(0, 0, 0, 1920, 1080, True, "Monitor 1")]
    except Exception:
        return [Monitor(0, 0, 0, 1920, 1080, True, "Monitor 1")]


def get_monitor(index: int) -> Monitor:
    """Retorna o monitor pelo índice, ou o primeiro se não encontrado."""
    monitors = get_monitors()
    if 0 <= index < len(monitors):
        return monitors[index]
    return monitors[0]
