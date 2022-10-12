# -*- coding: utf-8 -*-
"""
:author @wangwangit
cron: 10 10 * * *
new Env('LeetCode 每日一题');
"""

import json

import requests

from notify_mtr import send
from utils import get_data


class LeetCode:
    @staticmethod
    def main():
        base_url = "https://leetcode-cn.com"
        # 获取今日每日一题的题名(英文)
        response = requests.post(
            f"{base_url}/graphql",
            json={
                "operationName": "questionOfToday",
                "variables": {},
                "query": "query questionOfToday { todayRecord { "
                "question { questionFrontendId questionTitleSlug __typename } "
                "lastSubmission { id __typename } "
                "date userStatus __typename } }",
            },
        )

        leetcode_title = (
            json.loads(response.text)
            .get("data")
            .get("todayRecord")[0]
            .get("question")
            .get("questionTitleSlug")
        )

        # 获取今日每日一题的所有信息
        url = f"{base_url}/problems/{leetcode_title}"
        response = requests.post(
            f"{base_url}/graphql",
            json={
                "operationName": "questionData",
                "variables": {"titleSlug": leetcode_title},
                "query": "query questionData($titleSlug: String!) "
                "{ question(titleSlug: $titleSlug) { questionId questionFrontendId "
                "boundTopicId title titleSlug content translatedTitle translatedContent"
                " isPaidOnly difficulty likes dislikes isLiked similarQuestions "
                "contributors { username profileUrl avatarUrl __typename } "
                "langToValidPlayground topicTags "
                "{ name slug translatedName __typename } "
                "companyTagStats codeSnippets { lang langSlug code __typename } "
                "stats hints solution { id canSeeDetail  __typename } "
                "status sampleTestCase metaData judgerAvailable judgeType "
                "mysqlSchemas enableRunCode envInfo book "
                "{ id bookName pressName source shortDescription fullDescription"
                " bookImgUrl pressImgUrl productUrl __typename } "
                "isSubscribed isDailyQuestion dailyRecordStatus "
                "editorType ugcQuestionId style __typename } }",
            },
        )

        # 转化成 json 格式
        json_text = json.loads(response.text).get("data").get("question")
        # 题目题号
        num = json_text.get("questionFrontendId")
        # 题名（中文）
        leetcode_title = json_text.get("translatedTitle")
        return f'<a href="{url}">{num}. {leetcode_title}</a>'


if __name__ == "__main__":
    _data = get_data()
    leetcode = _data.get("LEETCODE")
    if leetcode:
        result = LeetCode().main()
        send("LeetCode 每日一题", result)
