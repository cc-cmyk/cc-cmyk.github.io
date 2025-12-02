// 确保地址正确
const jsonPath = 'https://cc-cmyk.github.io/static/scholar.json';

document.addEventListener("DOMContentLoaded", function() {
    console.log("Scholar script loaded...");
    
    // 1. 先去抓取数据
    fetch(jsonPath)
        .then(response => {
            if (!response.ok) throw new Error("Status: " + response.status);
            return response.json();
        })
        .then(data => {
            console.log("Data received:", data);
            
            // 2. 数据拿到后，开始“蹲守”网页元素出现
            // 因为您的网页是动态加载 Markdown 的，元素不会立刻出现
            
            // 等待论文列表容器出现
            waitForElement('papers-list', function(container) {
                renderPapers(data.papers, container);
            });
            
            // 等待统计数据容器出现
            waitForElement('stats-grid', function(container) {
                renderStats(data);
            });
        })
        .catch(error => {
            console.error('Fetch error:', error);
        });
});

/**
 * 核心辅助函数：轮询等待元素出现
 * @param {string} id - 元素的 ID
 * @param {function} callback - 找到元素后的回调函数
 */
function waitForElement(id, callback) {
    // 如果元素已经存在，直接执行
    const el = document.getElementById(id);
    if (el) {
        callback(el);
        return;
    }

    // 否则，每 500 毫秒检查一次，直到找到为止
    const interval = setInterval(() => {
        const el = document.getElementById(id);
        if (el) {
            console.log(`Element ${id} found! Rendering...`);
            clearInterval(interval); // 找到了，停止轮询
            callback(el);
        }
    }, 500);
}

// 渲染统计卡片
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

// 渲染论文列表
function renderPapers(papers, container) {
    container.innerHTML = ''; // 清空 Loading

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

        const titleHtml = `<a href="${paper.link}" target="_blank" style="font-weight:600; text-decoration:none; color:#2c3e50;">${paper.title}</a>`;
        const yearHtml = `<span style="color:#666; margin-left:5px;">(${paper.year})</span>`;
        const citeHtml = paper.citation > 0 ? `<span style="font-size:0.85em; color:#0056b3; margin-left:8px; background:#f0f7ff; padding:2px 6px; border-radius:4px;">Cited by ${paper.citation}</span>` : '';

        li.innerHTML = `${titleHtml}.${yearHtml}.${citeHtml}`;
        ul.appendChild(li);
    });

    container.appendChild(ul);
}
