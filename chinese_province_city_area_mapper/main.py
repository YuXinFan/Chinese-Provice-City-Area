
import cpca
import sys
import os


if __name__ == "__main__":
    try:
        if len(list(sys.argv)) <= 1:
            addrs = ["上海上海市浦东新区上海市浦东新区沪城环路999号上海海洋大学本科生近邻宝"]
            df = cpca.transform(addrs) 
        elif os.path.exists(sys.argv[1]):
            addrs = cpca.InputFromCSV(sys.argv[1])
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
            print("文件路径错误，文件不存在")
            exit()
    except PermissionError:
        print("csv文档已被打开，请关闭csv文档")
    except:
        print("csv文档格式错误")
    finally:
        print("分析完成")