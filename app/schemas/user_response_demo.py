from pydantic import BaseModel

# 数据库中的用户模型（含密码哈希）
class UserInDB(BaseModel):
    user_id:str
    username:str
    email:str
    password_hash:str
# 对外返回的用户模型（不含敏感字段）
class UserResponse(BaseModel):
    user_id:str
    username_id:str
    email:str
user=UserInDB(user_id="u_10001",username="dawei",email="dawei@example.com"
              ,password_hash="hasged_posswork_xxx")
response=UserResponse(user_id=user.user_id,username_id=user.username
                     ,email=user.email)
print(response.model_dump())