import random
def game():
    p=int(input("请输入你的猜拳数字石头（1），剪刀（2），布（3）"))
    c=random.randint(1,3)
    print(c)
    # if(p==1 and c==2) or (p==2 and c==3) or (p==3 and c==2):
    # if p==0:
    #     break
    if p-c==-1 or p-c==2:
        print("你赢了")
    elif p==c:
        print("pingji")


    else:
         print("nishule")
    # if p==0:
    #    break

while True:
    game()