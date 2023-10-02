import datetime


# 示例用法
date_str = "2022年3月11日"
date_obj = datetime.datetime.strptime(date_str, "%Y年%m月%d日")
new_date_format = date_obj.strftime("%Y-%m-%d")
new_date_format2 = date_obj.strftime("%Y")
print(new_date_format2)
print(new_date_format)