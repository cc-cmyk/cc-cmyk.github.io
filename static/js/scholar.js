// 确保这里的地址是正确的
const jsonPath = 'https://cc-cmyk.github.io/static/scholar.json';

document.addEventListener("DOMContentLoaded", function() {
    fetch(jsonPath)
        .then(response => response.json())
        .then(data => {
            renderStats(data);
            renderPapers(data.papers);
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('papers-list').innerHTML = '<div class="loading-text">Loading failed.</div>';
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

// [核心修改]：修改列表样式，仿照您的第二张图
function renderPapers(papers) {
    const papersContainer = document.getElementById('papers-list');
    if (!papersContainer) return;

    papersContainer.innerHTML = '';

    if (!papers || papers.length === 0) {
        papersContainer.innerHTML = '<div>No recent papers found.</div>';
        return;
    }

    // 创建一个无序列表 (ul)
    const ul = document.createElement('ul');
    // 设置样式：黑色实心圆点，左侧缩进
    ul.style.listStyleType = 'disc'; 
    ul.style.paddingLeft = '20px';
    ul.style.margin = '0';

    papers.forEach(paper => {
        const li = document.createElement('li');
        li.style.marginBottom = '10px'; // 行间距
        li.style.color = '#212529';     // 字体颜色接近黑色
        li.style.fontSize = '1rem';     // 字体大小
        li.style.lineHeight = '1.5';

        // 构造内容：标题 (加粗/链接) + 年份 + 引用数
        // 注意：API 不提供作者和期刊名，所以我们只能显示 "Title. (Year)."
        li.innerHTML = `
            <a href="${paper.link}" target="_blank" style="text-decoration:none; color:#212529; font-weight:600;">
                ${paper.title}
            </a>. 
            <span style="color: #666;">(${paper.year})</span>.
            ${paper.citation > 0 ? `<span style="font-size:0.9em; color:#0056b3;">[Cited by ${paper.citation}]</span>` : ''}
        `;
        ul.appendChild(li);
    });

    papersContainer.appendChild(ul);
}
