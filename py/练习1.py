from time import clock_settime

h=input("请输入你的身高")
kg=input("请输入你的体重")
print("个人信息")
print("我的身高是",h)
print("我的体重是",kg)
name="杨晓静"
ega=29
print("我的名字是",name,"我的年龄是",ega)
s1="我喜欢"
s2="python"
sa=s1+s2
print(sa)
s1="我今年"
s2="22"
s3=(s1+s2)
print(s3)
egg=0.68
a=20
money=egg*a
print(money)
egg=int(input("请输入鸡蛋的数量"))
b=0.68
money=egg*b
print(money)

ega=int(input("请输入你的年龄"))
if 18<ega<50:
    print("可以进入网吧")
else:
    print("不可以进入网吧")
a=100
b=79
if  a>=80 or b>=80:
    print("可以去迪士尼玩")
else:
    print("不可以去迪士尼玩")
ega=int(input("请输入你的年龄"))
if 18<ega<100:
    print("可以用身份证住酒店")
else:
    print("需要监护人陪同")