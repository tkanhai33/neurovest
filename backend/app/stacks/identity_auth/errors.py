class AuthenticationError(Exception):
    """Base class for controlled authentication failures."""


class MissingSecretError(AuthenticationError):
    """Raised when the JWT secret boundary is unavailable."""


class InvalidTokenError(AuthenticationError):
    """Raised when a token is malformed or fails validation."""


class ExpiredTokenError(InvalidTokenError):
    """Raised when a token is expired."""


class TokenNotYetValidError(InvalidTokenError):
    """Raised when a token's not-before claim is in the future."""


class RevokedTokenError(InvalidTokenError):
    """Raised when a token identifier has been revoked."""


class InvalidPasswordHashError(AuthenticationError):
    """Raised when a stored password hash is malformed."""
