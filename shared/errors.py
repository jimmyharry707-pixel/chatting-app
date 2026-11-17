"""Application exception hierarchy."""
class MessengerError(Exception): pass
class ValidationError(MessengerError): pass
class AuthenticationError(MessengerError): pass
class PermissionDenied(MessengerError): pass
class ResourceNotFound(MessengerError): pass
class NetworkError(MessengerError): pass
class ConflictError(MessengerError): pass
