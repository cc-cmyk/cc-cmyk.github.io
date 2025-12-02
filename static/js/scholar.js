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

function renderPapers(papers) {
    const papersContainer = document.getElementById('papers-list');
    if (!papersContainer) return;

    papersContainer.innerHTML = '';

    if (!papers || papers.length === 0) {
        papersContainer.innerHTML = '<div class="loading-text">No recent papers found.</div>';
        return;
    }

    papers.forEach(paper => {
        const div = document.createElement('div');
        div.className = 'paper-item';
        
        div.innerHTML = `
            <div class="paper-content">
                <a href="${paper.link}" class="paper-title" target="_blank">${paper.title}</a>
                <div class="paper-meta">${paper.year}</div>
            </div>
            ${paper.citation ? `<span class="citation-badge" title="Cited by">${paper.citation}</span>` : ''}
        `;
        papersContainer.appendChild(div);
    });
}
