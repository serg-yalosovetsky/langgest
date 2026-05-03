from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def get_volume() -> float | None:
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume  # type: ignore
        from comtypes import CLSCTX_ALL  # type: ignore

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        return volume.GetMasterVolumeLevelScalar()
    except ImportError:
        return None
    except Exception as e:
        logger.error("get_volume error: %s", e)
        return None


def set_volume(level: float) -> bool:
    """Set master volume 0.0–1.0."""
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume  # type: ignore
        from comtypes import CLSCTX_ALL  # type: ignore

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        volume.SetMasterVolumeLevelScalar(max(0.0, min(1.0, level)), None)
        logger.debug("Volume set to %.1f%%", level * 100)
        return True
    except ImportError:
        logger.warning("pycaw not installed — volume control unavailable")
        return False
    except Exception as e:
        logger.error("set_volume error: %s", e)
        return False


def change_volume(delta_percent: int) -> bool:
    """Change volume by delta_percent (-100 to 100)."""
    current = get_volume()
    if current is None:
        return False
    new_level = current + delta_percent / 100.0
    return set_volume(new_level)


def set_mute(muted: bool) -> bool:
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume  # type: ignore
        from comtypes import CLSCTX_ALL  # type: ignore

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        volume.SetMute(int(muted), None)
        logger.debug("Mute: %s", muted)
        return True
    except ImportError:
        logger.warning("pycaw not installed — mute control unavailable")
        return False
    except Exception as e:
        logger.error("set_mute error: %s", e)
        return False
