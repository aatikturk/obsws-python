class OBSSDKError(Exception):
    """Base class for OBSSDK errors"""


class OBSSDKTimeoutError(OBSSDKError):
    """Exception raised when a connection times out"""


class OBSSDKRequestError(OBSSDKError):
    """Exception raised when a request returns an error code"""

    def __init__(self, req_name, code, comment):
        self.req_name = req_name
        self.code = code
        message = f"Request {self.req_name} returned code {self.code}."
        if comment:
            message += f" With message: {comment}"
        super().__init__(message)
