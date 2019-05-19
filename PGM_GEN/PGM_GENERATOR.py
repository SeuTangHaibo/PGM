#coding=UTF-8
__author__='H.TANG'
import re

RE_Switch = re.compile('S')
RE_Bus = re.compile('B')
RE_Power = re.compile('P')

#生成PPN模型节点
def GET_PGM_NODE(l):
    P_part = []
    B_part = []
    S_part = []
    for i in l:
        if RE_Bus.search(i):
            B_part.append(i)
        elif RE_Power.search(i):
            P_part.append(i)
        else:
            S_part.append(i)
    node_c=[]
    for i in P_part:
        for j in B_part:
            node_c.append('C'+i+j)
    for i in range(0,len(B_part)):
        for j in range(i+1,len(B_part)):
            if B_part[i] > B_part[j]:
                node_c.append('C'+B_part[i]+B_part[j])
            else:
                node_c.append('C'+B_part[j]+B_part[i])
    return S_part,node_c

#生成PPN模型边
def GET_PGM_EDGE(l):
    edges = []
    NS_index = []
    S_index = []
    for i in range(0,len(l)):
        if not RE_Switch.search(l[i]):
            NS_index.append(i)
        else:
            S_index.append(i)
    for i in range(0,len(NS_index)):
        for j in range(i,len(NS_index)):
            if NS_index[i]!=NS_index[j]:
                if l[NS_index[i]]>l[NS_index[j]]:
                    Cname = 'C'+l[NS_index[i]]+l[NS_index[j]]
                else:
                    Cname = 'C'+l[NS_index[j]]+l[NS_index[i]]
                ran = range(NS_index[i],NS_index[j])
                gap = [x for x in S_index if x in ran]
                S_list = [l[i] for i in gap]
                for item in S_list:
                    edges.append([item,Cname])        
    return edges

#已知图结构，获取图中的隐变量
def get_switch(node,edge):
    switch = []
    for row in edge:
        if node in row:
            switch.append(row[0])
    return switch