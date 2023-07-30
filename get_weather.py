from datetime import datetime

import requests
import json


def get_weather_data():
    # 设置 API 请求的参数
    params = {
        "api_key": "ZqalRw2aaBAmBc9gRgwFSoEKvWnIT8wI",
        "district_id": 330100,

    }

    # 发送请求并获取结果
    response = requests.get(
        "https://api.map.baidu.com/weather/v1/?district_id=330100&data_type=all&ak=ZqalRw2aaBAmBc9gRgwFSoEKvWnIT8wI",
        params=params)
    data = json.loads(response.text)
    now_weather = data["result"]["now"]["text"]
    now_temp = data["result"]["now"]["temp"]

    # 提取位置信息
    country = data["result"]["location"]["country"]
    province = data["result"]["location"]["province"]
    city = data["result"]["location"]["city"]

    # 提取未来几天的天气预报

    forecasts = data["result"]["forecasts"]
    daily_forecasts = []
    # 遍历每个预测
    for day_forecast in forecasts:
        # 提取需要的信息
        text_day = day_forecast["text_day"]
        text_night = day_forecast["text_night"]
        high = day_forecast["high"]
        low = day_forecast["low"]
        date = day_forecast["date"]
        week = day_forecast["week"]

        # 将信息存储在一个新的字典中
        daily_weather = {
            "text_day": text_day,
            "text_night": text_night,
            "high": high,
            "low": low,
            "date": date,
            "week": week,
        }
        daily_forecasts.append(daily_weather)
    second_day_week = daily_forecasts[1]['week']
    second_day_text_day= daily_forecasts[0]['text_day']
    second_day_high=daily_forecasts[0]['high']
    second_day_low = daily_forecasts[0]['low']
    # 处理结果
    current_time = datetime.now()
    month = str(current_time.month)
    day = str(current_time.day)
    weather_date ="今天是"+month+"月"+day+"日。"+ city + "当前气温" + str(now_temp) + "度" + now_weather + ",明天" + second_day_week + second_day_text_day + ",最高温度" + str(
        second_day_high) + "最低温度" + str(second_day_low)


    return weather_date



