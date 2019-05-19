#coding=UTF-8
__author__='H.TANG'

from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import BeliefPropagation

import pandas as pd
import random
from PGM_GEN.PGM_GENERATOR import GET_PGM_NODE,GET_PGM_EDGE,get_switch 
from itertools import product
from copy import deepcopy
import os
import re

RE_Switch = re.compile('S')

#所有节点集合
GNODES = ['SC11','SC22','SC33','SC44','SC55','SL12','SL32','SL34','SL45','SF1','SF2','SF3','SF4','SF5','SF6','P1',
         'P2','P3','P4','P5','B11','B21','B22','B31','B32','B41','B42','B43','B44','B51','B52']
GNODE_S,GNODE_C = GET_PGM_NODE(GNODES)
PATH = os.path.abspath('DATA/EDGES.xlsx')
EDGES = pd.read_excel(PATH).values.tolist() 

#不同规模网络节点集合
CG_9 = ['P1','SC11','B11','SL12','B21','SF1','B22','SF1','SC22','P2']
CG_11 = ['P2','SC22','B21','SF1','B22','SL32','B32','SF2','B31','SC33','P3']
CG_15 = ['P3','SC33','B31','SF2','B32','SL34','B44','SF3','B43','SF4','B42','SF5','B41','SC44','P4']

#选择一个网络规模，获取BN模型的训练数据
cg = CG_15
EDGES_N = [i for i in GET_PGM_EDGE(cg) if i in EDGES]
# EDGES_N.append(['SF2','CB32B31'])
# EDGES_N.append(['SL12','CB21B11'])

NODES_N = list(set(GET_PGM_NODE(cg)[0] + GET_PGM_NODE(cg)[1]) & set(GNODE_S+GNODE_C))
# NODES_N.append('CB32B31')
# NODES_N.append('CB21B11')
PPN_N = BayesianModel(EDGES_N)

Path = os.path.abspath("DATA/ND_Sample.xlsx")
ND_Sample = pd.read_excel(Path)
ND_Sample_N = ND_Sample.loc[:,NODES_N]

#节点分类
S_var = [];C_var = []
for item in ND_Sample_N.columns:
    if RE_Switch.search(item):
        S_var.append(item)
    else:
        C_var.append(item)

#生成随机误差
# OB = ['CP1B11', 'CP2B21', 'CB21B11', 'CB22B21']
# OB = ['CP2B21','CB22B21', 'CB32B22','CB32B31','CP3B31']
# OB = ['CP4B41', 'CB42B41', 'CB43B42', 'CB44B43', 'CB44B32', 'CB32B31', 'CP3B32']
# for i in OB:
#     ITEM = random.sample(ND_Sample_N.index.tolist(),25)
#     ND_Sample_N[i][ITEM] = (ND_Sample_N[i][ITEM]+1)%2
                
#计算CPD
for i in S_var:
    P2 = sum(ND_Sample_N[i])/len(ND_Sample_N)
    P1 = 1 - P2 
    CPD = TabularCPD(i, 2, [[P1],[P2]])
    PPN_N.add_cpds(CPD)
for i in C_var:
    P1 = []
    P2 = []
    i_switch = get_switch(i,EDGES_N)
    state=list(product(range(2), repeat=len(i_switch)))
    for ii in range(len(state)):
        ND_Sample_NS = deepcopy(ND_Sample_N)
        for jj in range(len(i_switch)):         
            ND_Sample_NS = ND_Sample_NS[ND_Sample_NS[i_switch[jj]]==state[ii][jj]]
        if len(ND_Sample_NS) != 0:
            P2.append(sum(ND_Sample_NS[i])/len(ND_Sample_NS))
            P1.append(1-sum(ND_Sample_NS[i])/len(ND_Sample_NS))
        else:
            P2.append(0)
            P1.append(1)
    CPD = TabularCPD(i, 2, [P1,P2], evidence=i_switch, evidence_card=[2]*len(i_switch))
    PPN_N.add_cpds(CPD)

error = 0
bp_N = BeliefPropagation(PPN_N)

#确定观测变量和隐变量，计算BP算法推理结果的误差
for i in range(0,500):
    ITEM = random.sample(ND_Sample_N.index.tolist(),1)
#     vbs = ['SL32','SC22','SF1','SC33','SF2']
    vbs = ['SC33','SF2','SL34','SF3','SF4','SF5','SC44']
#     VBS = {'SL32':int(ND_Sample_N['SL32'][ITEM]),'SC22':int(ND_Sample_N['SC22'][ITEM]),'SF1':int(ND_Sample_N['SF1'][ITEM]),
#            'SC33':int(ND_Sample_N['SC33'][ITEM]),'SF2':int(ND_Sample_N['SF2'][ITEM])}
#     EDS = {'CP2B21':int(ND_Sample_N['CP2B21'][ITEM]),'CB22B21':int(ND_Sample_N['CB22B21'][ITEM]),
#            'CB32B22':int(ND_Sample_N['CB32B22'][ITEM]),'CB32B31':int(ND_Sample_N['CB32B31'][ITEM]),
#            'CP3B31':int(ND_Sample_N['CP3B31'][ITEM])}    
    VBS = {'SC33':int(ND_Sample_N['SC33'][ITEM]),'SF2':int(ND_Sample_N['SF2'][ITEM]),
           'SL34':int(ND_Sample_N['SL34'][ITEM]),'SF3':int(ND_Sample_N['SF3'][ITEM]),
           'SF4':int(ND_Sample_N['SF4'][ITEM]),'SF5':int(ND_Sample_N['SF5'][ITEM]),
           'SC44':int(ND_Sample_N['SC44'][ITEM])}
    EDS = {'CP4B41':int(ND_Sample_N['CP4B41'][ITEM]),'CB42B41':int(ND_Sample_N['CB42B41'][ITEM]),
           'CB43B42':int(ND_Sample_N['CB43B42'][ITEM]),'CB44B43':int(ND_Sample_N['CB44B43'][ITEM]),
           'CB44B32':int(ND_Sample_N['CB44B32'][ITEM]),'CB32B31':int(ND_Sample_N['CB32B31'][ITEM]),
           'CP3B32':int(ND_Sample_N['CP3B32'][ITEM])}
    query = bp_N.map_query(variables=vbs,evidence=EDS)
    for key in query:
        if query[key] != VBS[key]:      
            error+=1     
print(error)