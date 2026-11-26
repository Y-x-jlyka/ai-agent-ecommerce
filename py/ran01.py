# import random
# a=random.randint(10,14)
# b=random.randint(13,14)
# c=random.randint(1,14)
# print(a,b,c)
# p=int(input("请输入你的猜拳数字石头（1），剪刀（2），布（3）"))
# c=random.randint(1,3)
# print(c)
# # if(p==1 and c==2) or (p==2 and c==3) or (p==3 and c==2):
# if p-c==-1 or p-c==2:
#     print("你赢了")
# elif p==c:
#     print("pingji")
# else:
#     print("nishule")
# a=1
# sum=0
# while a<=100:
#     if a%2==0:
#         sum=sum+a
#     a=a+1
# print(sum)
a=1
sum=0
while a<=30:
    if a%3==0:
        sum=sum+a
    a+=1
print(sum)

a=1
sum=0
while a<=40:
    if a%7==0:
        sum=sum+a
    a+=1
print(sum)

food_list=["苹果","梨","橘子","桃子","西瓜","猕猴桃"]
print(food_list.index("苹果"))
print(food_list.index("liulian"))

a_list=[17,19,23,11,5,2]
a_list.sort()
print(a_list)


fruits={"苹果","梨","橘子","桃子","西瓜","猕猴桃"}
print(fruits)
for i in fruits:
    print(i)
print("你真是个“好人”啊")
s1="苹果橘子梨榴莲"
print(s1[2:4])
print(s1[::3])

num=("0123456789")
print(num[-2: ])

