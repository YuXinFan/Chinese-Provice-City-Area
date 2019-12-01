
import cpca
import sys
import os


if __name__ == "__main__":
    if len(list(sys.argv)) <= 1:
        addrs = ["上海上海市浦东新区上海市浦东新区沪城环路999号上海海洋大学本科生近邻宝"]
        df = cpca.transform(addrs) 
    elif os.path.exists(sys.argv[1]):
        addrs = cpca.InputFromCSV(sys.argv[1])
        #l = ['广东省深圳市宝安区麻烦送到广东省深圳市龙华区观澜松元环观中路370号易顺达电商物流园', '陕西省宝鸡市眉县首善街道首善镇平阳街30号眉县供电分公司', '吉林省延边朝鲜族自治州安图县一条街老健委家属楼一单元302', '重庆重庆市沙坪坝区沙坪坝康居西城六组团菜鸟驿站', '广西壮族自治区南宁市西乡塘区大学西路189号广西财经学院相思湖校区']
        df = cpca.transform(addrs) 
        pLine = "省：{\t"
        for k,v in df.province.items():
            pLine += "{}:{}\t".format(k, v)
        pLine += "}\n"
        cLine = "市：{\t"
        for k,v in df.city.items():
            cLine += "{}:{}\t".format(k, v)
        cLine += "}\n"
        aLine = "区: {\t"
        for k,v in df.area.items():
            aLine += "{}:{}\t".format(k, v)
        aLine += "}\n"
        cpca.AddToCSV(sys.argv[1], [pLine, cLine, aLine])
    else:
        addrs = ["上海上海市浦东新区上海市浦东新区沪城环路999号上海海洋大学本科生近邻宝"]
        df = cpca.transform(addrs) 
        print("文件路径错误，文件不存在")
        exit()