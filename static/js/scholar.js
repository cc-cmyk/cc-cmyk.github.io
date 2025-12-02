// 使用绝对路径，确保 100% 能找到数据文件
const jsonPath = 'https://cc-cmyk.github.io/static/scholar.json';

document.addEventListener("DOMContentLoaded", function() {
    console.log("Scholar script loaded, fetching:", jsonPath);
    fetch(jsonPath)
        .then(response => {
            if (!response.ok) throw new Error("Data file not found");
            return response.json();
        })
        .then(data => {
            console.log("Data received:", data);
            // 1. 渲染统计卡片
            renderStats(data);
            // 2. 渲染论文列表
            renderPapers(data.papers);
        })
        .catch(error => {
            console.error('Error loading scholar data:', error);
            const container = document.getElementById('papers-list');
            if (container) container.innerHTML = '<div class="loading-text">Data pending update...</div>';
        });
});

function renderStats(data) {
    const statsContainer = document.getElementById('stats-grid');
    if (!statsContainer) return;

    statsContainer.innerHTML = ''; // 清空 Loading

    const items = [
        { label: 'Citations', value: data.citations },
        { label: 'h-index', value: data.h_index },
        { label: 'i10-index', value: data.i10_index }
    ];

    items.forEach(item => {
        if (item.value !== undefined) {
            const card = document.createElement('div');
            card.className = 'stat-card';
            card.innerHTML = `
                <span class="stat-number">${item.value}</span>
                <span class="stat-label">${item.label}</span>
            `;
            statsContainer.appendChild(card);
        }
    });
}

// ...前面的代码保持不变...

function renderPapers(papers) {
    const papersContainer = document.getElementById('papers-list');
    if (!papersContainer) return;

    papersContainer.innerHTML = '';

    if (!papers || papers.length === 0) {
        papersContainer.innerHTML = '<div class="loading-text">No recent papers found.</div>';
        return;
    }

    // 创建一个无序列表 ul
    const ul = document.createElement('ul');
    ul.style.listStyleType = 'disc'; // 实心圆点
    ul.style.paddingLeft = '20px';

    papers.forEach(paper => {
        const li = document.createElement('li');
        li.style.marginBottom = '15px'; //每项之间的间距
        
        // 构建类似图2的格式: 作者(这里没有作者信息，只能模拟). 标题. 期刊(没有期刊信息). 年份.
        // 因为SerpApi简版数据只有标题、链接、引用数、年份。
        // 我们做成：Title. (Year). [Cited by X]
        
        li.innerHTML = `
            <span style="font-size: 1rem; color: #333;">
                <a href="${paper.link}" target="_blank" style="text-decoration:none; color:#000; font-weight:normal;">
                    ${paper.title}
                </a>. 
                <span style="color: #666;">(${paper.year})</span>.
                ${paper.citation > 0 ? `<span style="font-size:0.85rem; color:#0056b3;">[Cited by ${paper.citation}]</span>` : ''}
            </span>
        `;
        ul.appendChild(li);
    });

    papersContainer.appendChild(ul);
}
