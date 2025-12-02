import os
import json
import requests

# === 配置区域 ===
# 建议使用环境变量，或者暂时填入您的 ID
SCHOLAR_ID = "_QJD5MgAAAAJ"  # 请替换为唐枫枭教授的真实ID
API_KEY = os.environ.get("SERP_API_KEY")


def fetch_data():
    if not API_KEY:
        print("Error: SERP_API_KEY not found.")
        return None

    params = {
        "engine": "google_scholar_author",
        "author_id": SCHOLAR_ID,
        "api_key": API_KEY,
        "hl": "zh-CN",
        "sort": "pubdate"
    }

    print("Fetching Google Scholar data...")
    try:
        response = requests.get("https://serpapi.com/search", params=params, timeout=30)
        data = response.json()
    except Exception as e:
        print(f"Request failed: {e}")
        return None

    if "error" in data:
        print(f"SerpApi Error: {data['error']}")
        return None

    # 解析数据
    author = data.get("author", {})
    cited_by = author.get("cited_by", {}).get("table", [])

    output = {
        "citations": cited_by[0].get("citations", {}).get("all", 0) if len(cited_by) > 0 else 0,
        "h_index": cited_by[1].get("h_index", {}).get("all", 0) if len(cited_by) > 1 else 0,
        "papers": []
    }

    for art in data.get("articles", [])[:10]:  # 取最新10篇
        output["papers"].append({
            "title": art.get("title"),
            "link": art.get("link"),
            "citation": art.get("cited_by", {}).get("value", ""),
            "year": art.get("year", "")
        })

    return output


if __name__ == "__main__":
    data = fetch_data()
    if data:
        # === 关键修改：直接存入 static 文件夹 ===
        # 确保 static 文件夹存在
        os.makedirs("static", exist_ok=True)
        with open("static/scholar.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Success: static/scholar.json updated.")
    else:
        exit(1)