

class FetchError(Exception):
    """An error that can occur when fetching data from an API.

    Client code might want to retry after a delay in case it was a transient
    failure.

    """

    def __init__(self, original):
        self.original_exception = original

