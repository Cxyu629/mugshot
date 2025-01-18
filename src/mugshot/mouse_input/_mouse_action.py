from abc import ABC
import pyautogui

from mugshot.mouse_input._screen import Screen

type Point = tuple[int, int]


class MouseAction(ABC):
    """Abstract class for sending mouse actions."""

    is_left_down = False
    is_right_down = False

    @staticmethod
    def move_to(x: int, y: int):
        """Moves cursor to coordinates (`x`, `y`) on the screen. If outside boundaries of the
        screen, it moves to the nearest edge."""

        def bound(point, size):
            return (
                min(max(point[0], 1), size[0] - 2),
                min(max(point[1], 1), size[1] - 2),
            )

        bound_x, bound_y = bound((x, y), Screen.get_size())
        pyautogui.moveTo(bound_x, bound_y)

    @staticmethod
    def get_position() -> Point:
        """Returns the cursor's current coordinates."""
        pos = pyautogui.position()
        return (int(pos.x), int(pos.y))

    @classmethod
    def left_down(cls):
        """Presses the left mouse button down."""
        if not cls.is_left_down:
            pyautogui.mouseDown(button="left")
            cls.is_left_down = True

    @classmethod
    def left_up(cls):
        """Releases the left mouse button if it was previously pressed down."""
        if cls.is_left_down:
            pyautogui.mouseUp(button="left")
            cls.is_left_down = False

    @classmethod
    def left_click(cls):
        """Performs a left mouse button click."""
        if not cls.is_left_down:
            pyautogui.leftClick()

    @classmethod
    def right_down(cls):
        """Presses the right mouse button down."""
        if not cls.is_right_down:
            pyautogui.mouseDown(button="right")
            cls.is_right_down = True

    @classmethod
    def right_up(cls):
        """Releases the right mouse button if it was previously pressed down."""
        if cls.is_right_down:
            pyautogui.mouseUp(button="right")
            cls.is_right_down = False

    @classmethod
    def right_click(cls):
        """Performs a right mouse button click."""
        if not cls.is_right_down:
            pyautogui.rightClick()

    @staticmethod
    def clear_down():
        """Clears left_down and right_down."""
        MouseAction.left_up()
        MouseAction.right_up()

    @staticmethod
    def v_scroll(clicks: int):
        """Performs vertical scrolling by `clicks` amount."""
        pyautogui.vscroll(clicks)

    @staticmethod
    def h_scroll(clicks: int):
        """Performs horizontal scrolling by `clicks` amount. Functionality limited to Linux."""
        pyautogui.hscroll(clicks)
