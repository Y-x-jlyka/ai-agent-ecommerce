from fastapi import Query
# 分页参数：页码 + 每页数量
class PaginationParams:
    # 接收并保存分页参数
    def __init__(self,page:int=Query(default=1,ge=1,description="页码"),
                 page_size:int=Query(default=10,ge=1,le=100,description="每页数量")):
        self.page=page
        self.page_size=page_size
    @property
    # 计算数据库查询的偏移量
    def offset(self)->int:
        return (self.page-1)*self.page_size