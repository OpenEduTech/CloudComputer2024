import requests
import json
from pprint import pprint
import time


class SemanticScholarScraper:
    """从 Semantic Scholar API 抓取相关论文的类"""
    @staticmethod
    def get_semanticscholar_response(
        keywords: list[str], min_year: int, max_year: int
    ) -> requests.Response:
        """从 Semantic Scholar API 获取响应"""
        headers = {
            "Connection": "keep-alive",
            "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
            "Cache-Control": "no-cache,no-store,must-revalidate,max-age=-1",
            "Content-Type": "application/json",
            "sec-ch-ua-mobile": "?1",
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Mobile Safari/537.36",
            "X-S2-UI-Version": "20166f1745c44b856b4f85865c96d8406e69e24f",
            "sec-ch-ua-platform": '"Android"',
            "Accept": "*/*",
            "Origin": "https://www.semanticscholar.org",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://www.semanticscholar.org/search?year%5B0%5D=2018&year%5B1%5D=2022&q=multi%20label%20text%20classification&sort=relevance",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        }

        joined_keywords = " ".join([str(elem).lower() for elem in keywords])

        data = json.dumps(
            {
                "queryString": f"{joined_keywords}",
                "page": 1,
                "pageSize": 10,
                "sort": "relevance",
                "authors": [],
                "coAuthors": [],
                "venues": [],
                "yearFilter": {"min": min_year, "max": max_year},
                "requireViewablePdf": False,
                "fieldsOfStudy": [],
                "hydrateWithDdb": True,
                "includeTldrs": True,
                "performTitleMatch": True,
                "includeBadges": True,
                "getQuerySuggestions": False,
            }
        )

        response = requests.post(
            "https://www.semanticscholar.org/api/1/search", headers=headers, data=data
        )
        if response.status_code != 200:
            raise Exception(f"API 请求失败，状态码 {response.status_code}: {response.text}")
        return response

    def parse_html_response(self, response: requests.Response) -> list[dict[str, str]]:
        """解析 Semantic Scholar API 的响应"""
        try:
            response_json = response.json()
        except json.JSONDecodeError as e:
            print(f"JSON 解析失败: {e}")
            print(f"原始响应内容: {response.text}")
            return []

        if "results" not in response_json:
            print(f"响应格式不符合预期: {response_json}")
            return []

        final_result = []
        response = response_json["results"]

        for result in response:
            publication = {"title": result["title"]["text"], "link": [],
                           "authors": self.get_authors(result), "publication_date": None}

            if result.get("pubDate"):
                publication["publication_date"] = result["pubDate"]
            else:
                publication["publication_date"] = result.get('year').get("text")

            if "primaryPaperLink" in result:
                publication["link"] = result["primaryPaperLink"]["url"]
            elif result["alternatePaperLinks"]:
                publication["link"] = result["alternatePaperLinks"][0]["url"]
            else:
                publication["link"] = "no_link_found"

            final_result.append(publication)
        return final_result

    def get_related_publications(
        self, keywords: list[str], min_year: int = 2015, max_year: int = 2024
    ):
        """从 Semantic Scholar API 获取相关论文"""
        semanticscholar_response = self.get_semanticscholar_response(
            keywords, min_year=min_year, max_year=max_year
        )
        parsed_response = self.parse_html_response(semanticscholar_response)
        return parsed_response

    @staticmethod
    def get_authors(result):
        """提取作者信息"""
        authors_list = []
        if isinstance(result, dict):
            for key, value in result.items():
                if key == 'authors':
                    for author in value:
                        authors_list.append(author[1]['text'])
        return authors_list


if __name__ == "__main__":
    # 示例用法
    keywords = ["零样本学习", "自然语言处理", "机器学习"]
    scraper = SemanticScholarScraper()
    publications = scraper.get_related_publications(keywords)
    pprint(publications)