from abc import ABC

import pyautogui


class Screen(ABC):
    """Abstract class for getting screen info."""

    @staticmethod
    def get_size() -> tuple[int, int]:
        """Returns the size of the screen in pixels as a (width, height) tuple."""

        return pyautogui.size()
