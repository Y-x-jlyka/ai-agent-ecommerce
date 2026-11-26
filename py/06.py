# a=1
# b=" "
# d=10
# while a<=10:
#      c=(d-a)
#      print(b*c,"*"*a)
#      a+=1
#
# b="*"
# for a in range(1,11):
#     print("*"*a)
#     a+=1
#
# b=" "
# d=10
# for a in range (1,11):
#     c=10-a
#     print(b * c, "*" * a)
#
# a=1
# for b in range(1,11):
#     print(" "*(10-b),"*"*a)
#     a+=2
#
#
# name_list=["1","2","3"]
# print(name_list)
#
#
#
# list1=["张三",18]
# list2=["王五",20,"小李",19]
# list3=[list1,list2]
# print(list3)
#
# list=["苹果","橘子","梨","西红柿","辣椒","胡萝卜"]
# print(list[:3:2])
# print(list[::3])
# print(list[2::3])
# print(list[::-1])

# import random
# while True:
#     c=random.randint(1,100)
#     while True:
#         a = int(input("请输入你数字"))
#         if a<c:
#             print("猜小了")
#         elif a>c:
#             print("猜大了")
#         else:
#             print("猜对了")
#             break

for a in range(1,11):
    print("*"*a)
    a+=1
a=1
for b in range(1,11):
    print(" "*(10-b),"*"*a)
    a+=2
a=19
for b in range(1,11):
    print(" "*(b-1),"*"*a)
    a-=2
a=1
for b in range(1,9):
    print(" "*(8-b),"*"*a)
    a+=2

a=13
for b in range(1,8):
    print(" "*(b-1),"*"*a)
    a-=2
# import random
# while True:
#     c=random.randint(1,100)
#     isdui=True
#     while isdui:
#         a = int(input("请输入你数字"))
#         if a<c:
#             print("猜小了")
#         elif a>c:
#             print("猜大了")
#         else:
#             print("猜对了")
#             isdui=False
#     print("答案是",c,"开始下一轮")