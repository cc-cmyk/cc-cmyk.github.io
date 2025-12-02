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

    params = {
        "engine": "google_scholar_author",
        "author_id": SCHOLAR_ID,
        "api_key": API_KEY,
        "hl": "en",      # 强制英文
        "gl": "us",      # 关键修改：强制美国地区 (解决排版解析失败的核心)
        "sort": "pubdate"
    }

    print("Requesting SerpApi (US/English Mode)...")
    try:
        response = requests.get("https://serpapi.com/search", params=params, timeout=30)
        data = response.json()
    except Exception as e:
        print(f"Network Fail: {e}")
        return None

    if "error" in data:
        print(f"SerpApi Error: {data['error']}")
        return None

    # === DEBUG: 打印更多信息以便排查 ===
    author = data.get("author", {})
    print(f"DEBUG: Author Name: {author.get('name')}")
    print(f"DEBUG: Author Keys: {list(author.keys())}")
    
    # === 数据提取逻辑 (增强版) ===
    stats = {"citations": 0, "h_index": 0, "i10_index": 0}

    # 1. 优先从 author.cited_by.table 提取
    cited_by_table = author.get("cited_by", {}).get("table", [])
    
    # 2. 如果 table 为空，尝试打印警告
    if not cited_by_table:
        print("WARNING: 'cited_by' table not found in author data.")
    
    for row in cited_by_table:
        row_str = str(row).lower()
        val = row.get("citations", {}).get("all", 0)
        
        if "citation" in row_str:
            stats["citations"] = val
        if "h-index" in row_str:
            stats["h_index"] = val
        if "i10-index" in row_str:
            stats["i10_index"] = val

    print(f"✅ Extracted Data: {stats}")

    # 处理论文列表
    papers = []
    for art in data.get("articles", [])[:10]:
        c_val = art.get("cited_by", {}).get("value")
        if c_val is None:
            c_val = 0
        
        papers.append({
            "title": art.get("title"),
            "link": art.get("link"),
            "citation": c_val,
            "year": art.get("year", "N/A")
        })

    # === 强制更新时间戳 ===
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