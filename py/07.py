# g#%%
# egg=0.68
# a=int(input("请输入数量"))
# money=egg*a
# print(money)
# a=2
# b=3.14
# c=a*b*2
# print(c)
# ega=int(input("请输入你的年龄"))
# if ega>=18:
#     print("可以进入")
# else:
#     print("不可以进入")
# from 练习1 import name
from statistics import median_low

# a=False
# b=8
# if a:
#     print("可以安检")
#     if b<=8:
#         print("可以上车")
#     else:
#         print("交出刀")
# else:
#     print("请先买票")

# import random
# while True:
#     a=int(input("请输入你的猜拳数字石头(1)剪刀(2)布（3）"))
#     c=random.randint(1,3)
#     if (a-c==-1) or (a-c==2):
#         print("你赢了")
#     elif a==c:
#      print("平局")
#     elif a==0:
#         break
#     else:
#         print("你输了")

# a=1
# while a<=100:
#     print("我错了")
#     a+=1

# a=1
# sum=0
# while a<=100:
#     if a%2==0:
#         sum=sum+a
#     a+=1
# print(sum)
#
# a=1
# sum=0
# while a<=100:
#     if a%2==1:
#         sum=sum+a
#     a+=1
# print(sum)

# a=1
# while a<=5:
#     print("这是第%d遍" % a)
#     if a==5:
#         break
#     a+=1

# a=0
# while a<=10:
#     a += 1
#     if a==5:
#         continue
#     print(a)

# a=1
# while a<=9:
#     b=1
#     while b<=a:
#         print("%d*%d=%d" % (b,a,a*b),end="\t")
#         b+=1
#     a+=1
#     print("")
#
# for a in range(1,10):
#     for b in range(1,a+1):
#         print("%d*%d=%d" % (b,a,b*a),end="\t")
#     a+=1
#     print("")
#
# import random
# c=random.randint(1,100)
# while True:
#     a = int(input("请输入数字"))
#     if a<c:
#         print("小")
#     elif a>c:
#         print("大")
#     else:
#         print("你赢了")
#         break

# a=153
# b=a//100
# c=(a//10)%10
# d=a%10
# if b**3+c**3+d**3==a:
#     print(a)
# sum=0
# for a in range(1,101):
#     sum=sum+a
# print(sum)
#
# sum=0
# for a in range(1,31):
#     if a%2==0:
#         sum=sum+a
# print(sum)
#
# a=1
# while a<=10:
#     print("*"*a)
#     a+=1
#
#
# a=1
# b=1
# while b<=8:
#     print(" "*(8-b),"*"*a)
#     a+=2
#     b+=1
# num_list=[]
# for i in range(1,101):
#     if i%2==1:
#         num_list.append(i)
# print(len(num_list))

# txt = "hello python"
# d = {}
# for ch in txt:
#     if ch in d:
#         d[ch]+=1
#     else:
#         d[ch] = 1
# print(d)

# for i in "apple":
#     print(i)
#
# for i in range(1,6):
#     print (i)
#
# for i in range(1,6):
#     num=("这是打印的第%d遍" % i)
#     print(num)
#
# sum=0
# for i in range(1,11):
#     sum=sum+i
# print(sum)
#
# sum=0
# for i in range(1,101):
#     if i%2==0:
#         sum=sum+i
# print(sum)
#
#
# for a in range(1,5):
#     print("*"*a)
# for a in range(1, 5):
#     for b in range(a):
#         print("*", end="")
#     print("")
# for a in range(1,3):
#     for b in range(3, ):
#         print("*",end="")
#     print("")
# for a in range(7, 13):
#     for b in range(a):
#         print(a, b)
#
# for i in range(1,5):
#     print("*"*i)
# i+=1
#
# a=[21,34,45,36,18]
# print(len(a))
#
#
# a=[14,15,17,38,91]
# b=(23,44,57,82,92)
# print(len(a))
# print(len(b))
#
# list=[17,21,38,55,43]
# del list[3]
# print(list)
#
# tuple=(19,37,21,42)
# print(max(tuple))
# print(min(tuple))

# lise=[11,25,33,72,81,99,83]
# print(lise[1::2])
#
# dict={"小明":88,"小红":97,"小白":98}
# if "小明" in dict:
#     print(("小明的分数是%d" % dict["小明"]))
# else:
#     print("查无此人")
# name=input("请输入您的姓名")
# name_list=({"name":"小明","age":18},{"name":"小红","age":17},
#            {"name":"小张","age":18})
# for a in name_list:
#     if a["name"]==name:
#         print("已报名")
#         break
# else:
#     print("请报名")
# print(2**8+2**5+2**3+2**2+2**1+2**0)
#
# num=int(0b11101)
# print(num)
#
# a=str(365)
# for j in a:
#     print(j)
#
for i in range(1000):
    a=str(i)
    sum=0
    e=0
    # print("a", a)
    for b in a:
        e+=int(b)

        sum+=int(b)
    # print("ehe", e)
    if sum==5:
        print(i)

# for i in range(100,1000):
#     a=str(i)
#     sum=0
#     for b in a:
#         sum+=int(b)**3
#     if sum==i:
#         print(sum)

# for i in range(2020,3000):
#     n=str(i)
#     a=n[0]
#     b=n[1]
#     c=n[2]
#     d=n[3]
#     if a==d and b==c:
#         print(i)

# list=[]
# for i in range(1,258):
#     if i%2==0:
#         list.append(i)
# print(list)

# m=[]
# for i in range(1,257):
#     if 256%i==0 and 368%i==0:
#         m.append(i)
# print(m)
# print(max(m))

# m=[]
# for i in range(1,101):
#     a=str(i)
#     sum=0
#     for b in a:
#         sum+=int(b)
#     if sum==i:
#             m.append(i)
# print(m)

# m=[]
# for a in range(1,100):
#     sum=0
#     for b in range(1,a):
#         if a%b==0:
#             sum+=b
#     if sum==a:
#         m.append(a)
# print(m)
# yearold=input("信息")
# if not bool(yearold):
#     print("qingshuru")
# else:
#     print("ninde")

# def speekName(myName):
#     print("我的名字是%s"% myName)
# speekName("xiao")
# speekName("dabai")
# print("我的名字是xiao")
# print("我的名字是dabai")

# def food(a):
#     b="番茄"
#     print(a+"炒"+b)
# food("鸡蛋")
# def shouyin(jiage,shuliang,shifu):
#     return shifu-jiage*shuliang
# while True:
#     jiage=float(input("请输入商品价钱(元)"))
#     shuliang=float(input("请输入购买商品的数量(个）"))
#     shifu=float(input("已付（元）"))
#     zhaoling=shouyin(jiage,shuliang,shifu)
#     print("已找零%s元" % zhaoling)
#     print("*"*20)


i=1
def wer():
    i=2
    print(i)
wer()
print(i)
def showplus(x):
    print(x)
    return x+1
num=showplus(6)
print(num)

def a():
    x=1
    def b():
        print(x)
    b()
a()

def sum(a,b):
    c=(a+b)
    print(c)
sum(1,2)

def show(name,age):
    print("我的名字是%s,我的年龄是%s" % (name,age))
show(age="20",name="小羊")

def show_one(user="吉",password="“123456"):
    print("帐号是:%s" % (user))
    print("密码是:%s" % (password))
show_one()
show_one("码""678910")

def add(x,y):
    return x+y
def apply (func,x,y):
    return func(x,y)
print(apply(add,2,1))

# def func1():
#     print("这是外函数")
#     def func2():
#         print("这是内涵数")
#         return func2()
# func1()()

class Dog():
    def __init__(self,name,age):
        self.name=name
        self.age=age
    def sit(self):
        print(self.name+"is nowsitting")
    def roll_over(self):
        print(self.name+"rolled,over")
my_dog=Dog("旺财",6)
my_dog.sit()

class Car():
    def __init__(self,make,model,year):
        self.make=make
        self.model=model
        self.year=year
    def get_data(self):
        data_sting=self.make+" "+self.model+" "+str(self.year)
        return data_sting
my_car=Car("奥迪","“A6","2015")
print(my_car.get_data())

class Electric(Car):
    def __init__(self,make,model,year):
        super().__init__(make,model,year)
        self.battery_size=70
    def battery_describe(self):
        print("电动汽车电池容量是："+str(self.battery_describe)+"-kWh")

