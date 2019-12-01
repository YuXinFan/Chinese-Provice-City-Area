# -*- coding: utf-8 -*-
# __init__.py

##============Jieba User Dict============## 
import jieba
## 向分词库添加行政区名称使其得以被识别
jieba.add_word("西乡塘区")

## 从分词库删除分词名称使其不被识别
jieba.del_word("吉林省延边朝鲜族自治州")
jieba.del_word("上海市浦东新区")


##============Import Phase============##
import copy
from io import TextIOWrapper
import csv

from .structures import *


##============Global variable============## 
LogOut = False
Province = 'province'
City = 'city'
Area = 'area'
ErrorCode = -1
# 直辖市
munis = {'北京市', '天津市', '上海市', '重庆市','北京', '天津', '上海', '重庆'}

##============Help Function============## 
def Log(st):
    if LogOut:
        print(st)


def is_munis(city_name):
    return city_name in munis


def munisEq(left, right):
    return True if left[0:2] == right[0:2] else False

def InputFromCSV(file_path):
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        addrList2 = list(reader)
    addrList = [i[0].replace(" ", "") for i in addrList2]
    Log(addrList)
    return addrList


def AddToCSV(file_path, strList):
    with open(file_path,'a') as fd:
        for line in strList:
            fd.write(line)


def IsValid(pca):
    cond1 = sum(pca.province.values()) == sum(pca.city.values())
    cond2 = sum(pca.city.values()) == sum(pca.area.values())
    return cond1 and cond2


def ConcatPca(left, right):
    result = copy.copy(left)

    for k,v in right.province.items():
        if k in result.province: 
            result.province[k] += v
        else:
            result.province[k] = v

    for k,v in right.city.items():
        if k in result.city:
            result.city[k] += v
        else:
            result.city[k] = v
    
    for k,v in right.area.items():
        if k in result.area:
            result.area[k] += v
        else:
            result.area[k] = v
    return result


def _data_from_csv() -> (AddrMap, AddrMap, AddrMap, dict, dict):
    # 区名及其简写 -> 相关pca元组
    area_map = AddrMap()
    # 城市名及其简写 -> 相关pca元组
    city_map = AddrMap()
    # (省名全称, 区名全称) -> 相关pca元组
    province_area_map = AddrMap()
    # 省名 -> 省全名
    province_map = {}
    # (省名, 市名, 区名) -> (纬度,经度)
    latlng = {}
    # 数据约定:国家直辖市的sheng字段为直辖市名称, 省直辖县的city字段为空
    from pkg_resources import resource_stream

    with resource_stream('cpca.resources', 'pca.csv') as pca_stream:

        text = TextIOWrapper(pca_stream, encoding='utf8')
        pca_csv = csv.DictReader(text)
        for record_dict in pca_csv:
            latlng[(record_dict['sheng'], record_dict['shi'], record_dict['qu'])] = \
                (record_dict['lat'], record_dict['lng'])

            _fill_province_map(province_map, record_dict)
            _fill_area_map(area_map, record_dict)
            _fill_city_map(city_map, record_dict)
            _fill_province_area_map(province_area_map, record_dict)

    return area_map, city_map, province_area_map, province_map, latlng


def _fill_province_area_map(province_area_map: AddrMap, record_dict):
    pca_tuple = (record_dict['sheng'], record_dict['shi'], record_dict['qu'])
    key = (record_dict['sheng'], record_dict['qu'])
    # 第三个参数在此处没有意义, 随便给的
    province_area_map.append_relational_addr(key, pca_tuple, P)


def _fill_area_map(area_map: AddrMap, record_dict):
    area_name = record_dict['qu']
    pca_tuple = (record_dict['sheng'], record_dict['shi'], record_dict['qu'])
    area_map.append_relational_addr(area_name, pca_tuple, A)
    if area_name.endswith('市'):
        area_map.append_relational_addr(area_name[:-1], pca_tuple, A)


def _fill_city_map(city_map: AddrMap, record_dict):
    city_name = record_dict['shi']
    pca_tuple = (record_dict['sheng'], record_dict['shi'], record_dict['qu'])
    city_map.append_relational_addr(city_name, pca_tuple, C)
    if city_name.endswith('市'):
        city_map.append_relational_addr(city_name[:-1], pca_tuple, C)
    # 特别行政区
    elif city_name == '香港特别行政区':
        city_map.append_relational_addr('香港', pca_tuple, C)
    elif city_name == '澳门特别行政区':
        city_map.append_relational_addr('澳门', pca_tuple, C)
    

def _fill_province_map(province_map, record_dict):
    sheng = record_dict['sheng']
    if sheng not in province_map:
        province_map[sheng] = sheng
        # 处理省的简写情况
        # 普通省分 和 直辖市
        if sheng.endswith('省') or sheng.endswith('市'):
            province_map[sheng[:-1]] = sheng
        # 自治区
        elif sheng == '新疆维吾尔自治区':
            province_map['新疆'] = sheng
        elif sheng == '内蒙古自治区':
            province_map['内蒙古'] = sheng
        elif sheng == '广西壮族自治区':
            province_map['广西'] = sheng
            province_map['广西省'] = sheng
        elif sheng == '西藏自治区':
            province_map['西藏'] = sheng
        elif sheng == '宁夏回族自治区':
            province_map['宁夏'] = sheng
        # 特别行政区
        elif sheng == '香港特别行政区':
            province_map['香港'] = sheng
        elif sheng == '澳门特别行政区':
            province_map['澳门'] = sheng

##============Data Map============## 
area_map, city_map, province_area_map, province_map, latlng = _data_from_csv()


##============Functional Function============## 
def transform(location_strs, index=[], cut=True, lookahead=8, pos_sensitive=False, open_warning=True):
    """将地址描述字符串转换以"省","市","区"信息为列的DataFrame表格
        Args:
            locations:地址描述字符集合,可以是list, Series等任意可以进行for in循环的集合
                      比如:["徐汇区虹漕路461号58号楼5楼", "泉州市洛江区万安塘西工业区"]
            cut:[预留接口]使用分词，默认使用，分词模式速度较快，但是准确率可能会有所下降
            lookahead:[预留接口]，只有在cut为false的时候有效，表示最多允许向前看的字符的数量
                      默认值为8是为了能够发现"新疆维吾尔族自治区"这样的长地名
                      如果你的样本中都是短地名的话，可以考虑把这个数字调小一点以提高性能
            pos_sensitive:[预留接口]如果为True则会多返回三列，分别提取出的省市区在字符串中的位置，如果字符串中不存在的话则显示-1
        Returns:
            tfResult：一个Pca instance
    """

    from collections.abc import Iterable

    if not isinstance(location_strs, Iterable):
        from .exceptions import InputTypeNotSuportException
        raise InputTypeNotSuportException(
            'location_strs参数必须为可迭代的类型(比如list, Series等实现了__iter__方法的对象)')

    extract = [_handle_one_record(addr, cut, lookahead, pos_sensitive, open_warning) for addr in location_strs]

    tfResult = Pca({}, {}, {}, -1, -1, -1)
    for i in extract:
        tfResult = ConcatPca(tfResult, i)
    tfResult.show()
    return tfResult


def _handle_one_record(addr, cut, lookahead, pos_sensitive, open_warning):
    """处理一条记录"""

    # 空记录
    if not isinstance(addr, str) or addr == '' or addr is None:
        empty = {'省': '', '市': '', '区': ''}
        if pos_sensitive:
            empty['省_pos'] = -1
            empty['市_pos'] = -1
            empty['区_pos'] = -1
        return empty

    # 地名提取
    pca, addr = _extract_addr(addr, cut, lookahead)

    return pca if IsValid(pca) else Pca({}, {}, {}, -1, -1, -1)


def _extract_addr(addr, cut, lookahead):
    """提取地址中的省,市,区名称
       Args:
           addr:原始地址字符串
           cut: 是否分词
       Returns:
           Pca instance
    """
    return _jieba_extract(addr) if cut else _full_text_extract(addr, lookahead)


def _jieba_extract(addr):
    """基于结巴分词进行提取
    """
    

    result = Pca({}, {}, {}, -1, -1, -1)
    pos = 0
    truncate = 0

    lastMunis = ""

    def StringToLabel(pcaPropertyStr):
        if (pcaPropertyStr == Province):
            return P
        elif (pcaPropertyStr == City):
            return C
        elif (pcaPropertyStr == Area):
            return A
        else: 
            print("Wrong PCA Property")
            return ErrorCode
            

    def _update_pca(pca_property, name, full_name):
        """pca_property: 'province', 'city' or 'area'"""

        level = StringToLabel(pca_property)
        isExist = name in getattr(result, pca_property)
        if (isExist):
            result.Increase(level, name, pos)
        else:
            result.Insert(level, name, pos)
    def _normalUpdate(word):
        if word in province_map:
            _update_pca('province', word, province_map[word])
        elif word in city_map:
            _update_pca('city', word, city_map.get_full_name(word))
        elif word in area_map:
            _update_pca('area', word, area_map.get_full_name(word))

    for word in jieba.cut(addr, cut_all=False):

        # 处理直辖市一二级单位名称相同
        if not is_munis(word):
            _normalUpdate(word)
            lastMunis = ""
        else:
            if lastMunis != "":
                if munisEq(lastMunis, word):
                    _update_pca('city', word, city_map.get_full_name(word))
                    lastMunis = ""
                else:
                    _normalUpdate(word)
                    lastMunis = ""
            else:
                _normalUpdate(word)
                lastMunis = word
        pos += len(word)

    result.Pruning()

    return result, addr[truncate:]

