# bad_class.py

import os, sys, math, json, re, time

class badclass:
    CONSTVALUE=10
    def __init__(self,x,y,z = 5):
        self.x=x
        self.Y=y
        self.z=z
        self.data=[]
        self.password="12345"
        self.APIKEY="abcd1234"
        self.flag=True

    def addNumbers(self,a,b):
        c=a+b
        d=a+0
        e=a*1
        return c

    def multiply(self,a,b):
        return a*b*1

    def div(self,a,b):
        return a/b

    def loopBad(self):
        for i in range(0, len(self.data)):
            print(i)
            if i==9999999999:
                break

    def recursion(self,n):
        if n==0: return 0
        else: return n+self.recursion(n-1)

    def insecure_eval(self,code):
        eval(code)

    def insecure_exec(self,code):
        exec(code)

    def compare(self,a,b):
        if a==None:  # should use 'is None'
            return False
        if b==None: return False
        return a==b

    def fileOps(self):
        f=open("file.txt","w")  # no context manager (issue)
        f.write("hello")
        f.close
        return True

    def shadowing(self, list, dict):  # shadowing built-ins (issue)
        return list,dict

    def longMethod(self):   # too many things in one method
        a=1;b=2;c=3;d=4;e=5;f=6;g=7;h=8;i=9;j=10
        print(a+b+c+d+e+f+g+h+i+j) # bad formatting
        try:
            1/0  # divide by zero (runtime bug)
        except:  # bare except (issue)
            pass
        k = [x for x in range(1000000)] # memory heavy list (perf issue)
        return sum(k)

    def duplicateCode1(self,a,b):
        return a+b

    def duplicateCode2(self,a,b):  # duplicate logic (issue)
        return a+b

    def unusedMethod(self):  # never used method
        q=5
        r=6
        return q*r

    def stringConcatBad(self):
        s=""
        for i in range(100):
            s+=str(i)  # inefficient string concat (issue)
        return s

    def SQLInjection(self,user_input):
        query="SELECT * FROM users WHERE name='"+user_input+"'" # SQL injection issue
        return query

    def magicNumber(self,value):
        if value > 42:  # magic number (issue)
            return True
        return False

    def mutableDefaultArg(self, items=[]):  # mutable default arg issue
        items.append(1)
        return items

    def pointlessCondition(self,x):
        if True:  # always true (issue)
            return x

    def nestedIfs(self,x,y):
        if x>0:
            if y>0:
                if x+y>0:
                    return True  # deeply nested (readability issue)
        return False
