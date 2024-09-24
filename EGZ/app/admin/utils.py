from fastapi import APIRouter, Request
from app.admin.constants import RESOURCES, PAGINATION
from app.payments.constants import COLORS_PAYMENTS


def get_context_view_pagination(request: Request, table_name: str, page_number: int, list_all):
    page_size = PAGINATION[table_name]
    limit = len(list_all) if page_number*page_size > len(list_all) else page_number*page_size
    contex = {"request": request,"resources":RESOURCES}
    contex["tablas"] = list_all[(page_number-1)*page_size: limit]
    contex["table_name"] = table_name
    contex["page_number"] = page_number
    contex["total_items"] = len(list_all)
    contex["total_page"] = (contex["total_items"] + page_size - 1) // page_size
    contex["colors_payments"] =  COLORS_PAYMENTS if table_name == "payments" else {}
    return contex