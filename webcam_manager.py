import cv2


class WebcamManager:
    def __init__(self, device_index: int = 0, width: int = 640, height: int = 480):
        """
        Initialize webcam.

        Args:
            device_index: Webcam index (usually 0)
            width: Desired frame width
            height: Desired frame height
        """
        self.device_index = device_index
        self.width = width
        self.height = height

        self.cap = cv2.VideoCapture(device_index)
        if not self.cap.isOpened():
            raise RuntimeError(
                f"❌ Could not open webcam (device index: {device_index})")

        # Set camera resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def get_frame(self):
        """Returns (success, frame).  
        success=False means no frame was captured."""
        if not self.cap:
            return False, None

        success, frame = self.cap.read()
        return success, frame

    def read(self):
        """Simple alias for get_frame()."""
        return self.get_frame()

    def is_opened(self) -> bool:
        """Check if webcam is still open."""
        return self.cap.isOpened() if self.cap else False

    def release(self):
        """Release webcam resource."""
        if self.cap:
            self.cap.release()
            self.cap = None

    def __del__(self):
        """Safety cleanup."""
        self.release()
