import mysql.connector

try:
    # 连接数据库（注意检查这里的信息）
    mydb = mysql.connector.connect(
        host="127.0.0.1",  # 本地主机
        user="root",  # 用户名
        password="123456",  # 你设置的密码
        database="mydb"  # 你要连接的数据库名
    )

    print("🎉 成功连上 MySQL 数据库！")

    # 测试一下执行 SQL 语句
    cursor = mydb.cursor()
    cursor.execute("SELECT VERSION()")
    result = cursor.fetchone()
    print("你的 MySQL 版本号是:", result[0])

    cursor.close()
    mydb.close()

except mysql.connector.Error as err:
    print(f"❌ 连接失败，报错信息: {err}")