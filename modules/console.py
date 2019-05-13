import ctypes
import sys


class Console:
    """  """
    std_out_handle = ctypes.windll.kernel32.GetStdHandle(-11)

    def WR(self, msg):
        """
        background white

        text red

        Arguments:
            msg {str} -- messages
        """
        self.color_set(0x74)
        sys.stdout.write(msg+'\n')
        self.color_reset

    def BR(self, msg):
        """
        background black

        text red

        Arguments:
            msg {str} -- messages
        """
        self.color_set(0x04)
        sys.stdout.write(msg+'\n')
        self.color_reset

    def color_set(self, color, handle=std_out_handle):
        Bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
        return Bool

    @property
    def color_reset(self):
        self.color_set(0x07)
