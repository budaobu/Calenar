# calendar_generator.py

from datetime import datetime, timedelta, date
from icalendar import Calendar, Event
import pytz
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def get_first_monday(year):
    """
    获取指定年份第一个周一的日期
    """
    first_day = date(year, 1, 1)
    # weekday() 返回 0-6，其中 0 是周一
    days_ahead = 0 - first_day.weekday()  # 负数表示上周，正数表示本周或下周
    if days_ahead <= 0:  # 如果1月1日不是周一，获取下一个周一
        days_ahead += 7
    return first_day + timedelta(days=days_ahead)

def get_week_number(target_date, year_first_monday):
    """
    计算给定日期是第几周
    从年份第一个周一开始计算
    """
    if target_date < year_first_monday:
        return 0  # 表示在第一周开始之前
    days_diff = (target_date - year_first_monday).days
    return days_diff // 7 + 1

def is_small_week(target_date, year_first_monday, first_week_is_small):
    """
    判断给定日期是否为小周
    target_date: 需要判断的日期
    year_first_monday: 年份第一个周一的日期
    first_week_is_small: 第一周是否为小周
    """
    # 如果日期在第一个周一之前，根据去年最后一周的状态来判断
    if target_date < year_first_monday:
        # 计算去年最后一周的状态
        last_year_monday = get_first_monday(target_date.year)
        week_number = get_week_number(target_date, last_year_monday)
        total_weeks_last_year = get_week_number(date(target_date.year, 12, 31), last_year_monday)
        # 根据去年总周数和第一周状态来判断当前周的状态
        last_week_is_small = (total_weeks_last_year % 2 == 1) == first_week_is_small
        return last_week_is_small
    
    # 计算当前是第几周
    week_number = get_week_number(target_date, year_first_monday)
    # 根据周数判断是否为小周
    return (week_number % 2 == 1) == first_week_is_small

def generate_calendar(year):
    # 创建日历
    cal = Calendar()
    cal.add('version', '2.0')
    cal.add('prodid', '-//Big Small Week Calendar//CN')
    
    # 设置时区
    beijing_tz = pytz.timezone('Asia/Shanghai')
    
    # 从环境变量获取第一周类型
    first_week_is_small = os.getenv('IS_FIRST_WEEK_SMALL', 'true').lower() == 'true'
    
    # 获取目标年份第一个周一
    year_first_monday = get_first_monday(year)
    
    # 生成目标年份的所有周六日期
    # 从上一年最后一周开始，确保完整处理跨年的情况
    start_date = date(year, 1, 1)
    end_date = date(year + 1, 1, 1)
    
    while start_date < end_date:
        # 如果当前日期是周六
        if start_date.weekday() == 5:
            # 判断是否为小周
            if is_small_week(start_date, year_first_monday, first_week_is_small):
                # 创建工作日事件
                event = Event()
                event.add('summary', '小周(班)')
                
                # 设置为全天事件
                event.add('dtstart', start_date)  # 使用日期而不是时间
                event.add('dtend', start_date + timedelta(days=1))  # 结束日期为下一天
                
                # 标记为全天事件
                event.add('transp', 'TRANSPARENT')  # 在日历中显示为"空闲"
                event.add('X-MICROSOFT-CDO-ALLDAYEVENT', 'TRUE')  # 兼容 Microsoft Outlook
                
                # 添加时间戳
                event.add('dtstamp', beijing_tz.localize(datetime.now()))
                
                # 添加事件到日历
                cal.add_component(event)
        
        start_date += timedelta(days=1)
    
    # 生成文件名
    filename = f'big_small_week_{year}.ics'
    
    # 保存日历文件
    with open(filename, 'wb') as f:
        f.write(cal.to_ical())
    
    return filename

if __name__ == '__main__':
    current_year = datetime.now().year
    generate_calendar(current_year)
