from contextvars import ContextVar
from inspect import trace

from sqlalchemy.engine import default

trace_id_var:ContextVar[str]=ContextVar("trace_id",default="-")
user_id_var:ContextVar[str]=ContextVar("user_id",default="_")
# 把 trace_id 存入当前请求上下文
def set_trace_id(trase_id:str):
    trace_id_var.set(trase_id)
# 从当前请求上下文取出 trace_id
def get_trace_id()->str:
    return trace_id_var.get()
# 把 user_id 存入当前请求上下文
def set_user_id(user_id:str):
    user_id_var.set(user_id)
# 从当前请求上下文取出 user_id
def get_user_id()->str:
    return user_id_var.get()