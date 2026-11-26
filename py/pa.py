from sqlalchemy import create_engine
engine=create_engine("mysql+pymysql://root:123456@127.0.0.1:3306/mydb?charset=utf8")
print(engine)

import pandas as pd
formlist=pd.read_sql_query("show tables",con=engine)
print("mydb数据库数据表清单为：""\n",formlist)
detail1=pd.read_sql_table("meal_order_detail1",con=engine)
print("使用read_sql_tabl读取订单详情表的长度为：",len(detail1))
print(detail1)