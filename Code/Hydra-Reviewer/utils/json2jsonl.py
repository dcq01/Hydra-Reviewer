import json

# 读取 JSON 文件
with open(r'D:\咳咳\智能软工\Code Review\CodeReviewData\code_review_file_tmp_latest.json', 'r', encoding='utf-8') as json_file:
    datas = json.load(json_file)

# 转换为 JSONL 并写入新文件
with open(r'D:\咳咳\智能软工\Code Review\CodeReviewData\code_review_file_tmp_latest2.jsonl', 'w',
          encoding='utf-8') as jsonl_file:
    for data in datas:
        json_string = json.dumps(data, ensure_ascii=False)
        jsonl_file.write(json_string + '\n')
