class LinkedRecordNotFoundError(Exception):
    """Raised when a linked record is not found."""

    def __init__(self, record_type: str, old_id: str, original_exception=None):
        super().__init__(f"{record_type} not found for old ID: {old_id}")
        self.original_exception = original_exception
