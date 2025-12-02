import os
import json
import requests

# === 配置区域 ===
SCHOLAR_ID = "_QJD5MgAAAAJ"
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

    print(f"Fetching data for Scholar ID: {SCHOLAR_ID}...")
    try:
        response = requests.get("https://serpapi.com/search", params=params, timeout=30)
        data = response.json()
    except Exception as e:
        print(f"Request failed: {e}")
        return None

    if "error" in data:
        print(f"SerpApi Error: {data['error']}")
        return None

    # === 关键修改：增强数据提取逻辑 ===
    author = data.get("author", {})
    cited_by_table = author.get("cited_by", {}).get("table", [])
    
    # 初始化统计数据
    stats = {
        "citations": 0,
        "h_index": 0,
        "i10_index": 0
    }

    # 尝试提取统计数据 (更加鲁棒的写法)
    if cited_by_table:
        try:
            # table[0] 通常是 "引用", table[1] 是 "h指数", table[2] 是 "i10指数"
            stats["citations"] = cited_by_table[0].get("citations", {}).get("all", 0)
            stats["h_index"] = cited_by_table[1].get("h_index", {}).get("all", 0)
            stats["i10_index"] = cited_by_table[2].get("i10_index", {}).get("all", 0)
        except (IndexError, AttributeError) as e:
            print(f"Warning: Failed to parse citation table: {e}")

    print(f"Extracted Stats: {stats}") # 打印日志以便调试

    output = {
        "citations": stats["citations"],
        "h_index": stats["h_index"],
        "i10_index": stats["i10_index"],
        "papers": []
    }

    # 提取论文列表
    for art in data.get("articles", [])[:10]:
        # 处理引用数可能是 None 的情况
        cit_value = art.get("cited_by", {}).get("value", 0)
        if cit_value is None: 
            cit_value = 0
            
        output["papers"].append({
            "title": art.get("title"),
            "link": art.get("link"),
            "citation": cit_value,
            "year": art.get("year", "N/A")
        })

    return output

if __name__ == "__main__":
    data = fetch_data()
    if data:
        os.makedirs("static", exist_ok=True)
        with open("static/scholar.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Success: static/scholar.json updated with correct values.")
    else:
        exit(1)