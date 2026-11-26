from enum import Enum
from pydantic import BaseModel,Field
# 用户角色枚举（管理员/普通用户/访客）
class UserRole(str,Enum):
    ADMIN="admin"
    USER="user"
    GUEST="guest"
# 当前登录用户信息
class CurrentUser(BaseModel):
    user_id:str=Field(...,description="用户ID")
    username:str=Field(...,description="用户名")
    role:UserRole=Field(default=UserRole.USER,description="用户角色")
    is_active:bool=Field(default=True,description="是否启用")