a=1
while a<=9:
    b=1
    while b<=a:
        print("%d*%d=%d" %(a,b,a*b),end="\t")
        b+=1
    print("")
    a+=1
for a in range (1,10):
    print("打印第%d遍" %a)
    for b in range(1,a+1):
        print("%d*%d=%d" % (a, b, a * b), end="\t")
a=1
while a<=9:
    b=1
    while b<=9:
        print(b)
        b+=1
    print(a)
    a+=1
i=1
while i<=3:
    j=1
    while j<4:
        print(j)
        j+=1
    i+=1
x=1
while x<=3:
    y=5
    while y<=7:
        print(y)
        y+=1
    x+=1
m=1
while m<=5:
    n=2
    while n<=4:
        print(n)
        n+=1
    m+=1
a=1
while a<=9:
     b=1
     while b<=a:
         # b<=9
         print("%d*%d+%d" %(a,b,a*b))
         b+=1
     a+=1
m=1
while m<=5:
    n=1
    while n<=m:
        print("%d+%d=%d" %(n,m,m+n))
        n+=1
    m+=1
x=1
while x<=6:
    y=1
    while y<=x:
        print("%d*%d=%d" %(y,x,y*x))
        y+=1
    x+=1
for a in range(1,11):
     print("打印第%d遍" % a)
for a in range(1,10):
    for b in range(1,a+1):
        print("%d*%d=%d" % (a,b,a*b),end="\t")
    print("")
for a in range(1,6):
    for b in range(1,a+1):
        print("%d+%d=%d" % (a,b,a*b),end="\t")
    print("")
for a in range(1,5):
    for b in range(1,a+1):
        print(b,end="\t")
    print("")
for a in range(2,7):
    for b in range(2,a+1):
        print(b,end="\t")
    print("")

