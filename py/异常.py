try:
    (6/0)
except ZeroDivisionError:
    print("零不能作为被除数")

print("请输入两个数值进行除法运算")
print("按Q键退出")
while True:
    a=input("\n被除数：")
    if a=="Q":
        break
    b=input("除数：")
    if b=="Q":
        break
    try:
        c=int(a)/int(b)
    except:
        print("输入数据有误，请核对数据后重新填写")
    else:
        print("结果为%s" % c)

