import re
import time
import requests

access_token = "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"
request_times = 0

headers = {
    'Authorization': f'Bearer {access_token}'
}


def get_remaining_requests():
    limit_url = "https://api.github.com/rate_limit"
    response = requests.get(limit_url, headers=headers)
    if response.status_code == 200:
        limit_data = response.json()['resources']['core']
        print("Github API limit:" + str(limit_data['remaining']))
        return limit_data['remaining'], limit_data['reset']
    else:
        print(f"Error getting rate limit: {response.status_code}")
        return None


def dynamic_sleep():
    remaining, reset_time = get_remaining_requests()
    if remaining is not None:
        if remaining < 100:
            current_time = int(time.time())
            sleep_time_seconds = reset_time - current_time + 10
            sleep_time_minutes = sleep_time_seconds / 60
            print(f"Sleeping for {sleep_time_minutes:.2f} minutes")
            time.sleep(sleep_time_seconds)


def get_request_data(url, params):
    global request_times
    request_times += 1
    if request_times > 50:
        request_times = 0
        dynamic_sleep()

    retries = 20
    retry_delay = 10

    for _ in range(retries):
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            print(f"Retrying after {retry_delay} seconds...")
            time.sleep(retry_delay)

    print("Maximum retries reached. Request unsuccessful.")
    return None


def get_commit_request_data(url, params):
    global request_times
    request_times += 1
    if request_times > 50:
        request_times = 0
        dynamic_sleep()

    retries = 3
    retry_delay = 5

    for _ in range(retries):
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            print(f"Retrying after {retry_delay} seconds...")
            time.sleep(retry_delay)

    print("Maximum retries reached. Request unsuccessful.")
    return None


def get_previous_file(repo_name, sha, file_name):
    url = f"https://api.github.com/repos/{repo_name}/commits"

    params = {
        'sha': sha,
        'path': file_name,
        "per_page": 2
    }
    previous_commit_sha_response = get_request_data(url, params)
    if previous_commit_sha_response is None:
        return "", ""
    previous_commit_sha_json = previous_commit_sha_response.json()
    if len(previous_commit_sha_json) < 2:
        return "", ""
    previous_commit_sha = previous_commit_sha_json[1]['sha']
    raw_url = "https://github.com/" + repo_name + "/raw/" + previous_commit_sha + "/" + file_name
    previous_file = get_request_data(raw_url, {})
    if previous_file is not None:
        return previous_commit_sha, previous_file.text
    else:
        return "", ""


def get_change_commit(repo_name, sha, file_name):
    url = f"https://api.github.com/repos/{repo_name}/commits"

    params = {
        'sha': sha,
        'path': file_name,
        "per_page": 1
    }
    previous_commit_sha_response = get_request_data(url, params)
    if previous_commit_sha_response is None:
        return ""
    previous_commit_sha = previous_commit_sha_response.json()
    if len(previous_commit_sha) != 0:
        return previous_commit_sha[0]['sha']
    else:
        return sha


def get_all_datas(url):
    all_datas = []
    while True:
        try:
            response = get_request_data(url, {'per_page': 100})
            if response is None:
                print("Failed to get data from the API. Exiting.")
                break
            all_datas.extend(response.json())
            if 'next' in response.links.keys():
                url = response.links['next']['url']
            else:
                break
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            print("Retrying after 30 seconds...")
            time.sleep(30)
    return all_datas


def convert_cn_punctuation_to_en(text):
    cn_to_en_punctuation = {
        "，": ",", "。": ".", "！": "!", "？": "?",
        "：": ":", "；": ";", "“": "\"", "”": "\"",
        "‘": "'", "’": "'", "（": "(", "）": ")",
        "【": "[", "】": "]", "——": "-", "《": "<",
        "》": ">", "、": ",", "…": " ", "–": "-", "˜": ""
    }
    return ''.join(cn_to_en_punctuation.get(char, char) for char in text)


def remove_emojis(text):
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub(' ', text)


def remove_chinese_and_japanese_characters(text):
    pattern = re.compile("[\u4e00-\u9fff\u3040-\u30ff\uff66-\uff9f]+")
    return pattern.sub('', text)


def remove_zwsp(text):
    return text.replace('\u200b', '')


def comment_clean(body):
    body = remove_zwsp(body)
    sub_body = re.sub(r'\s+', ' ', body)
    clean_body = sub_body.strip()
    clean_body = convert_cn_punctuation_to_en(clean_body)
    clean_body = remove_chinese_and_japanese_characters(clean_body)
    clean_body = remove_emojis(clean_body)

    return clean_body


if __name__ == "__main__":
    print()
