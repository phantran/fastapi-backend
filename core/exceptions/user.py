from core.exceptions import CustomException


class PasswordDoesNotMatchException(CustomException):
    code = 400
    error_code = "USER__PASSWORD_DOES_NOT_MATCH"
    message = "password does not match"


class DuplicateUsernameException(CustomException):
    code = 400
    error_code = "USER__DUPLICATED"
    message = "username already exists"


class UserNotFoundException(CustomException):
    code = 404
    error_code = "USER__NOT_FOUND"
    message = "user not found"


class InvalidCredentialsException(CustomException):
    code = 400
    error_code = "USER__INVALID_CREDENTIALS"
    message = "invalid user credentials "


class SellerDepositException(CustomException):
    code = 400
    error_code = "USER__DEPOSIT_NOT_BUYER"
    message = "only buyers can change deposit"
