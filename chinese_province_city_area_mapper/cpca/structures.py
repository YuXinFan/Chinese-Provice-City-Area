# -*- coding: utf-8 -*-

from collections import defaultdict


P = 0
C = 1
A = 2


class AddrMap(defaultdict):
    """封装 '地名' -> [[相关地址列表], 地名全名]   这种映射结构"""

    def __init__(self):
        super().__init__(lambda: [[], None])

    def get_full_name(self, key):
        return self[key][1]

    def is_unique_value(self, key):
        """key所映射到的地址列表中的地址是否唯一"""
        if key not in self.keys():
            return False
        
        return len(self.get_relational_addrs(key)) == 1

    def get_relational_addrs(self, key):
        return self[key][0]

    def get_value(self, key, pos):
        """获得映射的第一个地址, 必须保证该key存在, 不然会出错"""
        return self.get_relational_addrs(key)[0][pos]

    def append_relational_addr(self, key, pca_tuple, full_name_pos):
        self[key][0].append(pca_tuple)
        if not self[key][1]:
            self[key][1] = pca_tuple[full_name_pos]


class Pca(object):

    def __new__(cls, *args, **kw):
        instance = object.__new__(cls)
        return instance

    def __init__(self, province = {}, city = {}, area = {}, province_pos = -1, city_pos = -1, area_pos = -1):
        self.province = province
        self.city = city
        self.area = area

        self.sequence = []
        self.pos = []

        self.province_pos = province_pos
        self.city_pos = city_pos 
        self.area_pos = area_pos

    def Increase(self, level, name, pos):
        if (level == P):
            self.province[name] += 1
        elif (level == C):
            self.city[name]  += 1
        elif (level == A):
            self.area[name]  += 1
        else:
            print("Increase level error") 
            return None
        self.sequence += [name]
        self.pos += [pos]
        return None


    def Insert(self, level, name, pos):
        if (level == P):
            self.province[name] = 1
        elif (level == C):
            self.city[name]  = 1
        elif (level == A):
            self.area[name]  = 1
        else:
            print("Insert level error") 
            return None
        self.sequence += [name]
        self.pos += [pos]
        return None 
    
    def Decrease(self, name):
        if name in self.province:
            if self.province[name] == 1:
                self.province.pop(name, None)
            else:
                self.province[name] -= 1
        elif name in self.city:
            if self.city[name] == 1:
                self.city.pop(name, None)
            else:
                self.city[name] -=1
        elif name in self.area:
            if self.area[name] == 1:
                self.area.pop(name, None)
            else:
                self.area[name] -=1
        else:
            print("Decrease error")
        return

    def Pruning(self):
        discreteIdx = [False for i in self.sequence]
        length = len(self.sequence)
        for i in range(len(self.sequence)):
            if self.sequence[i] in self.province and self.sequence[i] in self.city:
                cond1 =  (i+2) < length and  (self.sequence[i+1] in self.city) and (self.sequence[i+2] in self.area) \
                    and len(self.sequence[i] + self.sequence[i+1]) == (self.pos[i+2] - self.pos[i])
                cond2 = (i+1) < length and (self.sequence[i-1] in self.province) and \
                        (self.sequence[i+1] in self.area) and \
                        len(self.sequence[i-1] + self.sequence[i]) == (self.pos[i+1] - self.pos[i-1])
                discreteIdx[i] = cond1 or cond2
            elif self.sequence[i] in self.province:
                if (i+2) < length:
                    cond1 = (self.sequence[i+1] in self.city) 
                    cond2 = (self.sequence[i+2] in self.area) 
                    cond3 = len(self.sequence[i] + self.sequence[i+1]) == (self.pos[i+2] - self.pos[i])
                    discreteIdx[i] = cond1 and cond2 and cond3
            elif self.sequence[i] in self.city:
                if ((i+1) < length) and ( i >0):
                    discreteIdx[i] = (self.sequence[i-1] in self.province) and \
                        (self.sequence[i+1] in self.area) and \
                        len(self.sequence[i-1] + self.sequence[i]) == (self.pos[i+1] - self.pos[i-1])
            elif self.sequence[i] in self.area:
                if (i < length) and ( i > 1):
                    discreteIdx[i] = (self.sequence[i-2] in self.province) and \
                        (self.sequence[i-1] in self.city) and \
                        len(self.sequence[i-2] + self.sequence[i-1]) == (self.pos[i] - self.pos[i-2])
            else:
                print("Unknow error")

        #print(self.sequence)
        #print(discreteIdx)

        for i in range(len(discreteIdx)):
            if discreteIdx[i] == False:
                self.Decrease(self.sequence[i])
        return None

    def show(self):
        print("省:\n {")
        for k in self.province.keys():
            print("{} : {}\n".format(k, self.province[k]))
        print("}\n")

        print("市:\n {")
        for k in self.city.keys():
            print("{} : {}\n".format(k, self.city[k]))
        print("}\n")

        print("区:\n {")
        for k in self.area.keys():
            print("{} : {}\n".format(k, self.area[k]))
        print("}\n")
        return 

    def propertysList(self):
        result = [
            self.province,
            self.city,
            self.area
        ]

        return result

