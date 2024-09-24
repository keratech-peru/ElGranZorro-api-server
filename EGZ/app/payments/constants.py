class Coupon:
    DURATION = 7
    PERCENT = 20

class ErrorCode:
    NOT_EXISTENT_COMMISSION_AGENT = "El agente comisionado no existe"
    PAYMENT_ALREADY_REGISTERED = "El pago ya se ha registrado, el par appuser_id y tournament_id debe ser unico."
    CUOPON_NOT_ALLOWE = "Cupon no permitido para tu usuario"
    USER_ALREADY_COMMISSION_AGENT = "Usuario ya es un agente comisionado"
    TOURNAMENT_DOES_NOT_EXIST = "El torneo no existe."
    TOKEN_GENERATION_FAILS = "Fallo la creacion del token"
    REJECTED_PAYMENT = "Pago rechazado"
    NOT_EXIST_COUPON = "Cupon no existente."
    EXPIRED_COUPON = "Cupon expirado."

class StatusPayments:
    RECEIVED = "RECIBIDO"
    APPROVED = "APROBADO"
    WAITING_FOR_REFOUND = "EN ESPERA DE DEVOLUCION"
    REFUND = "REEMBOLSO"
    FREE = "GRATIS"

COLORS_PAYMENTS = {
    StatusPayments.RECEIVED : "bg-yellow",
    StatusPayments.APPROVED : "bg-blue",
    StatusPayments.WAITING_FOR_REFOUND : "bg-green",
    StatusPayments.REFUND : "bg-red",
    StatusPayments.FREE : "bg-purple"
}