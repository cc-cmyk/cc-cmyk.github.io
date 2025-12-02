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
        "hl": "zh-CN",
        "sort": "pubdate"
    }

    print("Requesting SerpApi...")
    try:
        response = requests.get("https://serpapi.com/search", params=params, timeout=30)
        data = response.json()
    except Exception as e:
        print(f"Network Fail: {e}")
        return None

    if "error" in data:
        print(f"SerpApi Error: {data['error']}")
        return None

    # === DEBUG: 打印现有字段，方便调试 ===
    author = data.get("author", {})
    print(f"DEBUG keys in author: {author.keys()}")
    
    # === 数据提取逻辑 ===
    stats = {"citations": 0, "h_index": 0, "i10_index": 0}

    # 方法 1: 尝试从表格中模糊搜索 (更强壮的查找方式)
    cited_by_table = author.get("cited_by", {}).get("table", [])
    if cited_by_table:
        for row in cited_by_table:
            # 把整行转为小写字符串进行搜索，防止大小写或字段名变化
            row_str = str(row).lower()
            val = row.get("citations", {}).get("all", 0)
            
            if "引用" in row_str or "citation" in row_str:
                stats["citations"] = val
            if "h" in row_str and "index" in row_str:
                stats["h_index"] = val
            if "i10" in row_str:
                stats["i10_index"] = val

    print(f"✅ Extracted Data: {stats}")

    # 处理论文列表
    papers = []
    for art in data.get("articles", [])[:10]:
        c_val = art.get("cited_by", {}).get("value")
        # 修复 null 问题
        if c_val is None:
            c_val = 0
        
        papers.append({
            "title": art.get("title"),
            "link": art.get("link"),
            "citation": c_val,
            "year": art.get("year", "N/A")
        })

    # === 关键：强制更新时间戳 ===
    # 只要有这个字段，Git 就一定会提交更新
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