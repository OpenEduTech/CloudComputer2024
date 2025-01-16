import requests
import time
from requests.exceptions import RequestException


def safe_request(method, url, params=None, headers=None, data=None, json=None, retries=3, timeout=10):
    for attempt in range(retries):
        try:
            response = requests.request(
                method=method,
                url=url,
                params=params,
                headers=headers,
                data=data,
                json=json,
                timeout=timeout
            )
            response.raise_for_status()  # 如果响应状态码不是 200-299，抛出异常
            return response
        except RequestException as e:
            print(f"Request failed (attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # 指数退避等待
            else:
                print("Max retries reached. Request failed.")
                return None


def get_request(url, params=None, headers=None, retries=3, timeout=10):
    return safe_request('GET', url, params=params, headers=headers, retries=retries, timeout=timeout)


def post_request(url, data=None, json=None, headers=None, retries=3, timeout=10):
    return safe_request('POST', url, data=data, json=json, headers=headers, retries=retries, timeout=timeout)