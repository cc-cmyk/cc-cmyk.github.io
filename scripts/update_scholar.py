import os
import json
import requests
import time

# === 配置区域 ===
SCHOLAR_ID = "_QJD5MgAAAAJ"
API_KEY = os.environ.get("SERP_API_KEY")

def fetch_data():
    if not API_KEY:
        print("Error: SERP_API_KEY not found.")
        return None

    # === 关键设置 ===
    params = {
        "engine": "google_scholar_author",
        "author_id": SCHOLAR_ID,
        "api_key": API_KEY,
        "hl": "en",      # 语言：英文
        "gl": "us",      # 地区：美国 (必须加这个，否则 SerpApi 经常抓不到引用表)
        "sort": "pubdate"
    }

    # 注意看这里的打印文字，我改成了 "US Mode"
    # 如果你在日志里看不到这句话，说明代码没更新成功！
    print(">>> STARTING FETCH: US Mode (gl=us) <<<")
    
    try:
        response = requests.get("https://serpapi.com/search", params=params, timeout=30)
        data = response.json()
    except Exception as e:
        print(f"Network Fail: {e}")
        return None

    if "error" in data:
        print(f"SerpApi Error: {data['error']}")
        return None

    # === 调试信息 ===
    author = data.get("author", {})
    # 如果这里依然没有 cited_by，我们在日志里能看到
    print(f"DEBUG keys available: {list(author.keys())}")
    
    # === 数据提取 ===
    stats = {"citations": 0, "h_index": 0, "i10_index": 0}

    cited_by_table = author.get("cited_by", {}).get("table", [])
    
    if cited_by_table:
        for row in cited_by_table:
            row_str = str(row).lower()
            val = row.get("citations", {}).get("all", 0)
            if "citation" in row_str: stats["citations"] = val
            if "h-index" in row_str: stats["h_index"] = val
            if "i10-index" in row_str: stats["i10_index"] = val
    else:
        print("!!! WARNING: Citation table is MISSING in the response !!!")

    print(f"✅ Extracted Stats: {stats}")

    # 处理论文
    papers = []
    for art in data.get("articles", [])[:10]:
        c_val = art.get("cited_by", {}).get("value")
        if c_val is None: c_val = 0
        papers.append({
            "title": art.get("title"),
            "link": art.get("link"),
            "citation": c_val,
            "year": art.get("year", "N/A")
        })

    # === 强制更新 ===
    output = {
        "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"), 
        "citations": stats["citations"],
        "h_index": stats["h_index"],
        "i10_index": stats["i10_index"],
        "papers": papers
    }

    return output

if __name__ == "__main__":
    data = fetch_data()
    if data:
        os.makedirs("static", exist_ok=True)
        with open("static/scholar.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Success: static/scholar.json updated.")
    else:
        exit(1)