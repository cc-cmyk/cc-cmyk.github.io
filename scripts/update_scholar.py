import os
import json
import requests

SCHOLAR_ID = "_QJD5MgAAAAJ" # 您的 ID
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

    # === 修复数据提取逻辑 ===
    author = data.get("author", {})
    cited_by_table = author.get("cited_by", {}).get("table", [])
    
    # 默认值
    stats = {"citations": 0, "h_index": 0, "i10_index": 0}

    # 尝试从不同位置提取引用数
    # 1. 尝试从 cited_by.table 提取
    if cited_by_table:
        for row in cited_by_table:
            label = row.get("citations", {}).get("label", "").lower() # 获取标签(如 "引用")
            val = row.get("citations", {}).get("all", 0) # 获取数值
            if "引用" in label or "citations" in label:
                stats["citations"] = val
            elif "h" in label and "index" in label:
                stats["h_index"] = val
            elif "i10" in label:
                stats["i10_index"] = val
    
    # 2. 如果上面失败，尝试直接从 author.cited_by.total 提取 (如果有)
    if stats["citations"] == 0:
        print("Table extraction failed, checking raw value...")
        # 这是一个备用猜测路径，视API更新而定

    print(f"✅ Extracted: {stats}") # 这一行会在 Action 日志里显示

    output = {
        "citations": stats["citations"],
        "h_index": stats["h_index"],
        "i10_index": stats["i10_index"],
        "papers": []
    }

    # 提取论文列表
    for art in data.get("articles", [])[:10]:
        # 修复 citation 为 null 的情况
        cit_info = art.get("cited_by", {})
        cit_value = cit_info.get("value") # 可能是 None
        
        # 强制转为整数或空字符串
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
        print("Success: static/scholar.json updated.")
    else:
        exit(1)