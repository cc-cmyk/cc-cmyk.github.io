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

    # === 关键修改：换一个引擎 ===
    # 不用 "google_scholar_author" 了，改用 "google_scholar_profiles"
    # 这个接口是专门搜人的，通常会直接把引用数暴露在最外层
    params = {
        "engine": "google_scholar_profiles",
        "mauthors": SCHOLAR_ID,  # 注意参数名变成了 mauthors
        "api_key": API_KEY,
        "hl": "en",
        "gl": "us"
    }

    print(">>> STARTING FETCH: Profile Engine Mode <<<")
    
    try:
        response = requests.get("https://serpapi.com/search", params=params, timeout=30)
        data = response.json()
    except Exception as e:
        print(f"Network Fail: {e}")
        return None

    if "error" in data:
        print(f"SerpApi Error: {data['error']}")
        # 如果新引擎失败，尝试回退到旧引擎（双保险）
        return fetch_data_fallback()

    # === 数据提取 (新结构) ===
    stats = {"citations": 0, "h_index": 0, "i10_index": 0}
    
    profiles = data.get("profiles", [])
    if not profiles:
        print("WARNING: No profile found with this ID.")
        # 回退
        return fetch_data_fallback()
        
    # 找到我们的主角
    target_profile = profiles[0] # 通常第一个就是
    
    # 提取引用数 (Profile 接口通常只给总引用数)
    cited_by_count = target_profile.get("cited_by", 0)
    stats["citations"] = cited_by_count
    
    # 注意：Profile 接口可能不给 h-index，我们先只保住总引用数
    print(f"✅ Extracted from Profile: {stats}")

    # === 为了获取论文，我们还得调一次旧接口，或者由前端只显示引用数 ===
    # 鉴于旧接口死活不给 stats，但能给论文，我们做一个混合
    # 先把这个引用数存下来
    
    # ... 这里为了稳妥，我直接让它去调旧接口拿论文，把引用数塞进去
    fallback_data = fetch_data_fallback()
    if fallback_data:
        # 用新接口抓到的 9515 覆盖旧接口的 0
        if stats["citations"] > 0:
            fallback_data["citations"] = stats["citations"]
            # h-index 没法从 profile 拿，暂时只能是 0 或者手动填一个兜底
            # 比如: fallback_data["h_index"] = 41 (硬编码兜底，如果实在抓不到)
        
        # 强制更新时间
        fallback_data["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
        return fallback_data
    
    return None

def fetch_data_fallback():
    # 这是原来的逻辑，专门用来拿论文列表 (因为 Profile 接口不给论文详情)
    print("... Fetching papers from Author Engine ...")
    params = {
        "engine": "google_scholar_author",
        "author_id": SCHOLAR_ID,
        "api_key": API_KEY,
        "hl": "en",
        "gl": "us",
        "sort": "pubdate"
    }
    try:
        data = requests.get("https://serpapi.com/search", params=params, timeout=30).json()
    except:
        return None
        
    stats = {"citations": 0, "h_index": 0, "i10_index": 0}
    
    # 还是尝试抓一下，万一这次有了呢
    author = data.get("author", {})
    cited_by_table = author.get("cited_by", {}).get("table", [])
    if cited_by_table:
        for row in cited_by_table:
            row_str = str(row).lower()
            val = row.get("citations", {}).get("all", 0)
            if "citation" in row_str: stats["citations"] = val
            if "h-index" in row_str: stats["h_index"] = val
            if "i10-index" in row_str: stats["i10_index"] = val
            
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
        
    return {
        "citations": stats["citations"],
        "h_index": stats["h_index"],
        "i10_index": stats["i10_index"],
        "papers": papers
    }

if __name__ == "__main__":
    data = fetch_data()
    if data:
        os.makedirs("static", exist_ok=True)
        with open("static/scholar.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Success: static/scholar.json updated.")
    else:
        exit(1)