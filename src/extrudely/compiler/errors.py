"""Compiler error types — structured errors for deterministic CadQuery compilation."""

class CompilerError(Exception):
    error_type: str
    location: str
    message: str

    def __init__(self, error_type: str, location: str, message: str):
        self.error_type = error_type
        self.location = location
        self.message = message
        super().__init__(message)

    def __str__(self):
        return f"[{self.error_type}] {self.location}: {self.message}"
