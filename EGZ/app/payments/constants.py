class Coupon:
    DURATION = 7
    PERCENT = 20

class ErrorCode:
    NOT_EXISTENT_COMMISSION_AGENT = "El agente comisionado no existe"
    USER_ALREADY_COMMISSION_AGENT = "Usuario ya es un agente comisionado"
    TOURNAMENT_DOES_NOT_EXIST = "El torneo no existe."
    TOKEN_GENERATION_FAILS = "Fallo la creacion del token"
    REJECTED_PAYMENT = "Pago rechazado"

URL_GENERATE_TOKEN = "https://api.mercadopago.com/platforms/pci/yape/v1/payment"
URL_PAYMENT = "https://api.mercadopago.com/v1/payments"