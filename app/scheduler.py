# app/scheduler.py
"""
后台刷新调度器（支持配置热重载）
"""
import time
import datetime

from app.config import CONFIG
from app.refresh_impl import run_refresh_async
from app.state_file import (  # ← 全部改成从这里导入
    get_next_refresh_time,
    update_next_refresh_time,
    get_config_changed,
    set_config_changed,
)


def _is_night(now: datetime.datetime) -> bool:
    if not CONFIG.skip_night:
        return False

    if CONFIG.night_start < CONFIG.night_end:
        return CONFIG.night_start <= now.hour < CONFIG.night_end
    else:
        return now.hour >= CONFIG.night_start or now.hour < CONFIG.night_end


def _calc_next_time(now: datetime.datetime) -> datetime.datetime:
    """
    计算下一次刷新时间：从每个整点开始
    例如当前 13:27，间隔 60 分钟 → 下次 14:00
    当前 13:27，间隔 30 分钟 → 下次 14:00（而不是 13:57）
    """
    interval_minutes = CONFIG.refresh_interval_minutes
    
    # 先取当前时间的整点
    current_hour_start = now.replace(minute=0, second=0, microsecond=0)
    
    # 计算从当前整点开始，已经过了多少个 interval 的倍数
    minutes_since_hour_start = now.minute
    intervals_passed = minutes_since_hour_start // interval_minutes
    
    # 下一个整点 = 当前整点 + (intervals_passed + 1) * interval
    next_time = current_hour_start + datetime.timedelta(minutes=(intervals_passed + 1) * interval_minutes)
    
    # 如果计算出来的时间已经过去（极小概率），再加一个 interval
    if next_time <= now:
        next_time += datetime.timedelta(minutes=interval_minutes)
    
    return next_time


def start_scheduler():
    """
    后台调度线程（常驻）
    支持配置热重载
    """
    last_force_refresh_date = None

    # 启动时先主动刷新一次（用户要求：每次打开 app 刷新）
    now = datetime.datetime.now()
    print("[Scheduler] 启动即刷新一次")
    run_refresh_async()

    # 然后计算并记录下一次刷新时间
    next_time = _calc_next_time(now)
    update_next_refresh_time(next_time)
    print(f"[Scheduler] 启动初始化: {next_time}")

    while True:
        now = datetime.datetime.now()

        # 检查配置变更
        if get_config_changed():
            print("[Scheduler] 配置变更，重新加载并重新计算")
            CONFIG.reload()
            set_config_changed(False)

            if CONFIG.refresh_immediately_on_config_change and not _is_night(now):
                print("[Scheduler] 配置变更后立即刷新一次")
                run_refresh_async()
                
            next_time = _calc_next_time(now)
            update_next_refresh_time(next_time)

        # 0 点强制刷新（每天一次）
        if CONFIG.force_refresh_at_midnight:
            if now.hour == 0:
                today = now.date()
                if last_force_refresh_date != today:
                    print("[Scheduler] 执行 0 点强制刷新")
                    run_refresh_async()
                    last_force_refresh_date = today

        # 正常刷新逻辑
        if not _is_night(now):
            next_time = get_next_refresh_time()
            if next_time is None or now >= next_time:
                print(f"[Scheduler] 执行刷新: {now}")
                run_refresh_async()
                next_time = _calc_next_time(now)
                update_next_refresh_time(next_time)
                print(f"[Scheduler] 更新下次时间: {next_time}")

        time.sleep(30)