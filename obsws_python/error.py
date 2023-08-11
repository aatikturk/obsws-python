class OBSSDKError(Exception):
    """Base class for OBSSDK errors"""


class OBSSDKTimeoutError(OBSSDKError):
    """Exception raised when a connection times out"""


class OBSSDKRequestError(OBSSDKError):
    """Exception raised when a request returns an error code"""

    def __init__(self, req_name, code, message=None):
        self.req_name = req_name
        self.code = code
        self.message = " ".join(
            [
                f"Request {self.req_name} returned code {self.code}.",
                f"With message: {message}" if message else "",
            ]
        )
        super().__init__(self.message)
