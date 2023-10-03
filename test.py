import requests
import json
import datetime
import re
from flask import Flask, request, jsonify


app = Flask(__name__)

headers = {
    'authority': 'api.bgm.tv',
    'accept': 'application/json',
    'accept-language': 'zh-CN,zh;q=0.9',
    'origin': 'https://bangumi.github.io',
    'referer': 'https://bangumi.github.io/',
    'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
}

# 加载class匹配内容
# 加载match_content数据
with open("class_match_content.json", "r",encoding="UTF-8") as file:
    class_match_content = json.load(file)


@app.route('/')
def Error():
    return '404 Not Found'
    

@app.route('/v0/subjects/<subject_id>')
def get_subject(subject_id):
    callbackurl = request.url
    url = f'https://api.bgm.tv/v0/subjects/{subject_id}'
    proxy = {
        'http': 'http://127.0.0.1:10809',
        # 'https': 'https://127.0.0.1:0809'
    }
    response = requests.get(url, proxies=proxy,headers = headers)
    #print(f"响应内容: {response.text}\n")
    if response.status_code == 200:
        load_son_str = json.dumps(response.json())
        parsed_json = json.loads(load_son_str)
    
    #获取角色信息
    url = f'https://api.bgm.tv/v0/subjects/{subject_id}/characters'
    proxy = {
        'http': 'http://127.0.0.1:10809',
        # 'https': 'https://127.0.0.1:0809'
    }
    response = requests.get(url, proxies=proxy,headers = headers)
    #print(f"响应内容: {response.text}\n")
    if response.status_code == 200:
        load_son_str = json.dumps(response.json())
        characters_json = json.loads(load_son_str)

    return process_json(parsed_json,characters_json,callbackurl)

def check_date_format(year):
    try:
        datetime.datetime.strptime(year, "%Y-%m-%d")
        return True
    except ValueError:
        return False

# 处理json 数据
def process_json(parsed_json,characters_json,callbackurl):
    #赋空值防止报错
    formatted_data=''
    out_vod_director=''
    out_vod_writer=''

    for item in parsed_json["infobox"]:
        if item['key'] == '放送开始':
            year = item['value']
            #print(out_vod_pubdate)
        if item['key'] == '上映年度':
            year = item['value']
            #print(out_vod_pubdate)
        if item['key'] == '导演':
            out_vod_director = item['value']
            #print(out_vod_actor)
        if item['key'] == '系列构成':
            out_vod_writer = item['value']
            #print(out_vod_director)
        if item['key'] == '别名':
            out_vod_sub = item['value']
            # print(out_vod_sub)
            values = [] 
            try:
                v_list = out_vod_sub  # 获取json中"value"对应的列表
                for v_dict in v_list:
                    
                    if type(v_dict) is dict:
                        # print("是字典正常获取")
                        value = v_dict.get("v")  # 获取每个字典中"v"对应的值
                        if value:
                            values.append(value)  # 将值添加到新的列表中
                        else:
                            values.append("")  # 如果value为空，则添加空字符串到新的列表中
                    else:
                        formatted_data=out_vod_sub
                        # print("不是字典")
                        # print(out_vod_sub)
            except KeyError:
                print("v对应的值不存在")
            if type(v_dict) is dict:
                # print(values)  # 打印所有获取到的值
                formatted_data = " / ".join(values)
                # print(formatted_data)

    #日期转换
    if check_date_format(year):
        #print("日期格式为Y-M-D")
        date_obj =datetime.datetime.strptime(year, "%Y-%m-%d")
        out_vod_year = date_obj.strftime("%Y")
        new_date_format=year

    else:
        #print("日期格式不符合Y-M-D")      
        date_obj = datetime.datetime.strptime(year, "%Y年%m月%d日")
        new_date_format = date_obj.strftime("%Y-%m-%d")
        out_vod_year = date_obj.strftime("%Y")

    # 写入tags 和匹配的class
    tags_string=""
    class_string = ""
    for i in parsed_json["tags"]:
        tags_string  += f'{i.get("name")},'
        if i.get("name") in class_match_content:
            class_string += f'{i.get("name")},'
    # 去除最后一个逗号
    tags_string  = tags_string.rstrip(",")
    class_string = class_string.rstrip(",")

    #写入声优名字
    actors_string = ""
    for i in characters_json:
        for ii in i.get("actors"):
            actors_string+= f'{ii.get("name")},'
    # 去除最后一个逗号
    actors_string = actors_string.rstrip(",")

    if parsed_json["name_cn"] in [""]:
        out_vod_name=parsed_json["name"]
    else: 
        out_vod_name=parsed_json["name_cn"]

    # 使用正则表达式提取指定部分)
    pattern = r"callback=(.*?)&"
    match = re.search(pattern, callbackurl)
    if match:
        callback = match.group(1)
        # print(callback)
    else:
        print("未找到匹配的部分")
        callback=""

    output_json = {
        "code": 1,
        "data": {
            "vod_name": out_vod_name,
            "vod_sub": formatted_data,
            "vod_pic": parsed_json["images"]["large"],
            "vod_year": out_vod_year,
            "vod_lang": "日语",
            "vod_area": "日本",
            "vod_state": "",
            "vod_total": parsed_json["total_episodes"],
            "vod_serial": "",
            "vod_isend": 1,
            "vod_class": class_string,
            "vod_tag": tags_string,
            "vod_actor": actors_string,
            "vod_director": out_vod_director,
            "vod_pubdate": new_date_format,
            "vod_writer": out_vod_writer,
            "vod_score": parsed_json["rating"]["score"],
            "vod_score_num": "",
            "vod_douban_score": "",
            "vod_duration": "",
            "vod_reurl": "",
            "vod_author": "",
            "vod_content": parsed_json["summary"]
        }
    }
    output_json_string = callback + '(' + str(output_json) + ');'
    #print(output_json_string)
    return (output_json_string)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)