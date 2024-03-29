import matplotlib.pyplot as plt
import sys
import numpy as np
import datetime

plt.rcParams['font.sans-serif']=['SimHei'] # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False # 用来正常显示负号

#设置用于图例的字体
font1 = {'family' : 'Times New Roman',
'weight' : 'normal',
'size' : 30,
}

#SOBT源数据读取
SOBT_raw = np.loadtxt('SOBT.txt')
SOBT_hour = SOBT_raw[:, 0]
SOBT_min = SOBT_raw[:, 1]

#基本参数的设定
flight_list = []    #航班号列表
route_list = []     #航路列表
SOBT_list = 98*[0] #计离时刻表初始化
LTOT_list = 98*[0] #最晚不延误时刻表初始化
CTOT_list = 98*[0] #模拟所有的航班CTOT时刻
err_list = 98*[0]  #CTOT与SOBT的差距
delta_alldirec = datetime.timedelta(minutes = 2) #全向 2 分钟间隔
delta_TAPEN = datetime.timedelta(minutes = 4) #TAPEN方向 4 分钟间隔
delta_TOL = datetime.timedelta(minutes = 4) #TOL方向 4 分钟间隔

#读取航班号列表（字符串格式）
with open('flight.txt', 'r') as f:
	for line in f:
		flight_list.append(list(line.strip('\n').split(',')))
def flight(i):
	return flight_list[i-1]

#读取航路列表（字符串格式）
with open('route.txt', 'r') as f:
	for line in f:
		route_list.append(list(line.strip('\n').split(',')))
def route(i):
	return route_list[i-1]

#生成「计离时刻SOBT」
def SOBT(i): #定义一个函数，用SOBT(i)表示从1～98个航班的「计离开时刻表」
	return datetime.datetime(2019, 8, 25, int(SOBT_hour[i-1]), int(SOBT_min[i-1]))
for i in range(1, 99):
	SOBT_list[i-1] = SOBT(i) #往初始时刻表里填入每一个航班的时刻

#计算「最晚不延误时刻LTOT」，在计离时刻基础上加25 mins
def LTOT(i):
	return SOBT(i) + datetime.timedelta(minutes = 25)
for i in range(1, 99):
	LTOT_list[i-1] = LTOT(i)

#计算模拟CTOT时刻表，并考虑航路限制，全向 2mins 的间隔， TAPEN 或 TOL 方向航路上的 4mins 间隔限制
def CTOT(i):
	if i == 1:    #第1架航班，没有前一架的限制
		return SOBT(i) + datetime.timedelta(minutes = 5)
	else:         #从第2架开始：
		if route(i) == ['NOLIMIT']:     #当观察的航班为 NOLIMIT
			return max((SOBT(i) + datetime.timedelta(minutes = 5)), (CTOT(i-1) + delta_alldirec))
		if route(i) == ['TOL']:         #当观察的航班为 TOL
			if route(i-1) == ['TOL']:   #当其前一班也为 TOL 时，需要间隔 4mins
				return max((SOBT(i) + datetime.timedelta(minutes = 5)), (CTOT(i-1) + delta_TOL))
			else:                       #当其前一班为 TAPEN 或 NOLIMIT 时，间隔 2mins 即可
				return max((SOBT(i) + datetime.timedelta(minutes = 5)), (CTOT(i-1) + delta_alldirec))
		if route(i) == ['TAPEN']:       #当观察的航班为 TAPEN  
			if route(i-1) == ['TAPEN']: #当其前一班也为 TAPEN 时，需要间隔 4mins
				return max((SOBT(i) + datetime.timedelta(minutes = 5)), (CTOT(i-1) + delta_TAPEN))
			else:
				return max((SOBT(i) + datetime.timedelta(minutes = 5)), (CTOT(i-1) + delta_alldirec))
for i in range(1, 99):
	CTOT_list[i-1] = CTOT(i) #得到 98 个航班的模拟 CTOT 时刻

#求CTOT与SOBT的时间差
def err(i):
	return CTOT(i) - SOBT(i)
for i in range(1, 99):
	err_list[i-1] = err(i)

#CTOT时刻写入txt文件保存
t = open('CTOT.txt', 'a')
t.close()
t = open('CTOT.txt', 'r+')
t.truncate()
for i in range(1, 99):
	t = open('CTOT.txt', 'a')
	t.writelines(str('\n第'+str(i)+'个航班的CTOT时刻：'+str(CTOT(i))))
	t.close()

#比较时间大小，生成临界延误航班报表（大于等于 -3 mins）
critical_delayed_number = 0
linjie = open('critical_delayedflights.txt', 'a')
linjie.close()
linjie = open('critical_delayedflights.txt', 'r+')
linjie.truncate()
for i in range(1, 99):
	if CTOT(i) >= (LTOT(i) - datetime.timedelta(minutes=3)):
		critical_delayed_number += 1
		print('第',critical_delayed_number,'个临界延误航班序号',i,'；','航班号', flight(i))
		linjie = open('critical_delayedflights.txt', 'a')
		linjie.writelines(str('\n第'+str(critical_delayed_number)+'个临界延误航班：'+str(flight(i))))
		linjie.close()
print('临界延误航班总架次：', critical_delayed_number)

#比较时间大小，生成纯延误航班报表（大于等于 1 mins）
delayed_number = 0
yanwu = open('delayedflights.txt', 'a')
yanwu.close()
yanwu = open('delayedflights.txt', 'r+')
yanwu.truncate()
for i in range(1, 99):
	if CTOT(i) >= (LTOT(i) + datetime.timedelta(minutes=1)):
		delayed_number += 1
		print('第',delayed_number,'个纯延误航班序号',i,'；','航班号', flight(i))
		yanwu = open('delayedflights.txt', 'a')
		yanwu.writelines(str('\n第'+str(delayed_number)+'个纯延误航班：'+str(flight(i))))
		yanwu.close()
print('纯延误航班总架次：', delayed_number)

#可视化数据准备
axes = plt.subplot(111)
type1_x = np.arange(1, 99)
type1_y = SOBT_list
type2_x = np.arange(1, 99)
type2_y = CTOT_list

#画散点图
type1 = axes.scatter(type1_x, type1_y, marker = '*', s = 50, c='green')
type2 = axes.scatter(type2_x, type2_y, s = 50, c='red')

# 设置坐标轴的取值范围
plt.ylim(((datetime.datetime(2019,8,25,6,0)), (datetime.datetime(2019,8,25,10,30))))

plt.xlabel('航班序号', fontsize = 26)
plt.ylabel('时刻', fontsize = 26)
plt.xticks(fontproperties = 'Times New Roman', size = 28)
plt.yticks(fontproperties = 'Times New Roman', size = 28)

axes.legend((type1, type2), ('SOBT', 'CTOT'), prop = font1, loc = 'best')
plt.savefig('comparison.png', dpi = 600, bbox_inches='tight')
plt.show()
