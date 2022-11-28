from core.exceptions import CustomException


class ProductNotFoundException(CustomException):
    code = 404
    error_code = "PRODUCT__NOT_FOUND"
    message = "product not found"


class ProductChangeNotAllowedException(CustomException):
    code = 400
    error_code = "PRODUCT__MODIFICATION_NOT_ALLOWED"
    message = "you cannot change this product"


class RoleNotAllowedException(CustomException):
    code = 400
    error_code = "PRODUCT__MODIFICATION_NOT_ALLOWED"
    message = "As a buyer, you cannot change this product"


class SellerBuyException(CustomException):
    code = 400
    error_code = "PRODUCT__SELLER_BUY_PRODUCTS"
    message = "only buyers can buy products"


class BuyOwnProductException(CustomException):
    code = 400
    error_code = "PRODUCT__BUY_OWN_PRODUCTS"
    message = "You cannot buy your products"


class InsufficientBalanceException(CustomException):
    code = 400
    error_code = "PRODUCT__INSUFFICIENT_BALANCE_TO_BUY"
    message = "In sufficient balance to buy product"


class ProductOutOfStockException(CustomException):
    code = 400
    error_code = "PRODUCT__INSUFFICIENT_BALANCE_TO_BUY"
    message = "In sufficient balance to buy product"
