# coding=utf-8
"""
author: Cao Zhanxiang
project: Audio
file: ChNumToNum.py
date: 2021/7/28
function: 
"""

chinese_number_dict = {'零': 0, '一': 1, '二': 2, '两': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10, '百': 100, '千': 1000, '万': 10000, "亿": 100000000}
not_in_decimal = "十百千万亿点"
def ch2num(chstr):
    if chstr == '半':
        return 0.5
    if '点' not in chstr:
        return ch2round(chstr)
    splits = chstr.split("点")
    if len(splits) != 2:
        return splits
    rount = ch2round(splits[0])
    decimal = ch2decimal(splits[-1])
    if rount is not None and decimal is not None:
        return float(str(rount) + "." + str(decimal))
    else:
        return None

def ch2round(chstr):
    no_op = True
    if len(chstr) >= 2:
        for i in chstr:
            if i in not_in_decimal:
                no_op = False
    else:
        no_op = False
    if no_op:
        return ch2decimal(chstr)

    result = 0
    now_base = 1
    big_base = 1
    big_big_base = 1
    base_set = set()
    chstr = chstr[::-1]
    for i in chstr:
        if i not in chinese_number_dict:
            return None
        if chinese_number_dict[i] >= 10:
            if chinese_number_dict[i] > now_base:
                now_base = chinese_number_dict[i]
            elif chinese_number_dict["万"] <= now_base < chinese_number_dict["亿"] and chinese_number_dict[i] > big_base:
                now_base = chinese_number_dict[i] * chinese_number_dict["万"]
                big_base = chinese_number_dict[i]
            elif now_base >= chinese_number_dict["亿"] and chinese_number_dict[i] > big_big_base:
                now_base = chinese_number_dict[i] * chinese_number_dict["亿"]
                big_big_base = chinese_number_dict[i]
            else:
                return None
        else:
            if now_base in base_set and chinese_number_dict[i] != 0:
                return None
            result = result + now_base * chinese_number_dict[i]
            base_set.add(now_base)
    if now_base not in base_set:
        result = result + now_base * 1
    return result

def ch2decimal(chstr):
    result = ""
    for i in chstr:
        if i in not_in_decimal:
            return None
        if i not in chinese_number_dict:
            return None
        result = result + str(chinese_number_dict[i])
    return int(result)


if __name__ == "__main__":
    print(ch2num("一万三千零二十"))
    print(ch2num("一万三千两百二十"))
    print(ch2num("两百五十三"))
    print(ch2num("三十二"))
    print(ch2num("二"))
    print(ch2num("二二三五七"))
    print(ch2num("十"))
    print(ch2num("百"))
    print(ch2num("十二点五"))
    print(ch2num("三点一四一五九二六"))
    print(ch2num("三千五百亿一千三百二十五万四千五百六十九点五八三四三九二九一"))

