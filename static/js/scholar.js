// 请确保这个路径是正确的，建议用绝对路径
const jsonPath = 'https://cc-cmyk.github.io/static/scholar.json'; 

document.addEventListener("DOMContentLoaded", function() {
    console.log("Scholar script loaded, fetching from:", jsonPath);
    
    // 找到挂载点
    const papersContainer = document.getElementById('papers-list');
    
    fetch(jsonPath)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("Data received:", data);
            
            // 1. 渲染统计卡片 (如果有的话)
            renderStats(data);
            
            // 2. 渲染论文列表
            if (data.papers && data.papers.length > 0) {
                renderPapers(data.papers, papersContainer);
            } else {
                if(papersContainer) papersContainer.innerHTML = '<div>No recent papers found in data.</div>';
            }
        })
        .catch(error => {
            console.error('Error loading scholar data:', error);
            if(papersContainer) papersContainer.innerHTML = `<div class="loading-text" style="color:red;">Error loading data: ${error.message}</div>`;
        });
});

function renderStats(data) {
    const statsContainer = document.getElementById('stats-grid');
    if (!statsContainer) return;

    statsContainer.innerHTML = ''; 

    const items = [
        { label: 'Citations', value: data.citations },
        { label: 'h-index', value: data.h_index },
        { label: 'i10-index', value: data.i10_index }
    ];

    items.forEach(item => {
        if (item.value !== undefined) {
            const card = document.createElement('div');
            card.className = 'stat-card';
            card.innerHTML = `<span class="stat-number">${item.value}</span><span class="stat-label">${item.label}</span>`;
            statsContainer.appendChild(card);
        }
    });
}

// [核心修复]：渲染论文列表
function renderPapers(papers, container) {
    if (!container) return;
    
    container.innerHTML = ''; // 清空 Loading 文字

    // 创建无序列表
    const ul = document.createElement('ul');
    ul.style.listStyleType = 'disc';
    ul.style.paddingLeft = '20px';
    ul.style.marginTop = '10px';

    papers.forEach(paper => {
        const li = document.createElement('li');
        li.style.marginBottom = '12px';
        li.style.lineHeight = '1.6';
        li.style.color = '#333';

        // 构造简单的显示格式: Title. (Year). [Cited by X]
        // 既然 API 没有作者和期刊，我们就只显示这些核心信息
        const titleHtml = `<a href="${paper.link}" target="_blank" style="font-weight:600; text-decoration:none; color:#2c3e50;">${paper.title}</a>`;
        const yearHtml = `<span style="color:#666; margin-left:5px;">(${paper.year})</span>`;
        const citeHtml = paper.citation > 0 ? `<span style="font-size:0.85em; color:#0056b3; margin-left:8px; background:#f0f7ff; padding:2px 6px; border-radius:4px;">Cited by ${paper.citation}</span>` : '';

        li.innerHTML = `${titleHtml}.${yearHtml}.${citeHtml}`;
        ul.appendChild(li);
    });

    container.appendChild(ul);
}
