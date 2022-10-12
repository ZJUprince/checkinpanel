# -*- coding: utf-8 -*-
"""
:refer @jing5460
cron: 21 21 * * *
new Env("无忧行");
"""

import requests

from notify_mtr import send
from utils import get_data


class JegoTrip:
    def __init__(self, check_items):
        self.check_items = check_items

    @staticmethod
    def task(user_id):
        res = requests.get(
            f"http://task.jegotrip.com.cn:8080/app/tasks?userid={user_id}"
        ).json()
        return res["rtn"]["tasks"]

    @staticmethod
    def sign(user_id, task_id) -> bool:
        res = requests.post(
            "http://task.jegotrip.com.cn:8080/app/sign",
            json={"userid": user_id, "taskId": task_id},  # 此处`I`要大写
            headers={
                "Accept-Encoding": "gzip, deflate",
                "Origin": "http://task.jegotrip.com.cn:8080",
                "Accept": "application/json, text/plain, */*",
                "Content-Type": "application/json;charset=utf-8",
                "Connection": "close",
                "Host": "task.jegotrip.com.cn:8080",
                "Content-Length": "89",
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_6 like Mac OS X) \
                                                AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 source/jegotrip",
                "Accept-Language": "en-us",
                "Referer": "http://task.jegotrip.com.cn:8080/task/index.html",
            },
        ).json()
        return res["result"]

    def verify_result(self, user_id):
        tasks = self.task(user_id)
        for task in tasks.get("日常任务", []):
            if task.get("name") == "每日签到奖励":
                return task.get("triggerAction") == "已签到"

    def main(self):
        msg = ""
        msg_all = ""
        for check_item in self.check_items:
            user_id = check_item.get("user_id")
            task_list = self.task(user_id=user_id)
            for task in task_list.get("日常任务", []):
                if task.get("name") == "每日签到奖励":
                    if task.get("triggerAction") == "签到":
                        res = self.sign(user_id=user_id, task_id=task["id"])
                        if res:
                            msg = (
                                "签到成功"
                                if self.verify_result(user_id=user_id)
                                else "签到失败：未知"
                            )
                    elif task.get("triggerAction") == "已签到":
                        msg = "签到失败：今日已签到！"
            msg_all += msg + "\n\n"
        return msg_all


if __name__ == "__main__":
    _data = get_data()
    _check_items = _data.get("JEGOTRIP", [])
    result = JegoTrip(check_items=_check_items).main()
    send("无忧行", result)
