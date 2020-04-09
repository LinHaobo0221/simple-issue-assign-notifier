from github import Github
import requests
import time
from datetime import datetime
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

# github info
git_user = config['github']['git_user']
git_pwd = config['github']['git_pwd']
git_repos = config['github']['git_repos']
comment_match_str = config['github']['comment_match_str']

# line notify
notify_url = config['line']['notify_url']
notify_token = config['line']['notify_token']

# 上一次的issue
old_issue_list = []
old_comment_list = []

git = Github(git_user, git_pwd)
repo = git.get_repo(git_repos)

my = git.get_user()


def diff(new_item, old_list):
    inner_count = 0

    for item in old_list:
        if item.id == new_item.id:
            inner_count += 1
    return inner_count


while True:

    print(str(datetime.now().strftime('%Y/%m/%d %H:%M:%S')) + ' job start.')

    open_issues = repo.get_issues(state='open')

    # 从github上拿到最新的assign给我的issue
    new_issue_list = []
    new_comment_list = []
    for issue in open_issues:
        assignees = issue.assignees
        if assignees is None:
            continue

        for assignee in assignees:
            if assignee.login == my.login:
                new_issue_list.append(issue)

                # 遍历issue comment
                comments = issue.get_comments()
                for comment in comments:
                    if comment_match_str == '':
                        new_comment_list.append(comment)
                        continue

                    if comment_match_str in comment.body:
                        new_comment_list.append(comment)

    # 开始处理 如果issue不再数据库中，保存
    notify_issues = []
    for issue in new_issue_list:
        print(str(issue.number) + ' -> ' + issue.title)

        # 判断是不是之前的issue
        if diff(issue, old_issue_list) == 0:
            # 这个是新的issue, 添加到通知列表
            notify_issues.append(issue)

    for issue_comment in new_comment_list:
        print('comment -> ' + str(issue_comment.id))

        # 判断是不是之前的issue comment
        if diff(issue_comment, old_comment_list) == 0:
            # 这个是新的issue comment, 添加到通知列表
            notify_issues.append(issue_comment)

    # 重置
    old_issue_list = new_issue_list[:]

    old_comment_list = new_comment_list[:]

    # 发送消息通知
    headers = {'Authorization': 'Bearer ' + notify_token}

    for issue in notify_issues:
        payload = {'message': 'New Assign or Comment: ' + issue.html_url}
        requests.post(notify_url, headers=headers, params=payload, )
    print('job end.')
    time.sleep(20)
