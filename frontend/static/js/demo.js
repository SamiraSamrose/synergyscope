//# File: frontend/static/js/demo.js
//# Purpose: Demo interface interactivity and agent execution

// Demo Mode JavaScript
// Handles interactive demo execution and visualization

async function runAgent(agentType) {
    const agentMap = {
        'social_graph': 1,
        'chemistry': 2,
        'meta': 3,
        'adaptation': 4,
        'compatibility': 5,
        'storyteller': 6,
        'visualizer': 7
    };
    
    const agentNum = agentMap[agentType];
    const agentCard = document.getElementById(`agent${agentNum}`);
    const output = document.getElementById(`output${agentNum}`);
    
    // Highlight active agent
    agentCard.classList.add('active');
    
    // Reset steps
    const steps = agentCard.querySelectorAll('.step-status');
    steps.forEach(step => {
        step.textContent = 'Pending';
        step.className = 'step-status pending';
    });
    
    output.innerHTML = '<pre>Processing...</pre>';
    
    try {
        // Simulate agent execution with step-by-step updates
        for (let i = 0; i < steps.length; i++) {
            await sleep(800);
            steps[i].textContent = 'Running';
            steps[i].className = 'step-status running';
            
            await sleep(1200);
            steps[i].textContent = 'Complete';
            steps[i].className = 'step-status complete';
        }
        
        // Execute specific agent logic
        await executeAgent(agentType, agentNum, output);
        
    } catch (error) {
        output.innerHTML = `<pre style="color: #ff4444;">Error: ${error.message}</pre>`;
    } finally {
        setTimeout(() => agentCard.classList.remove('active'), 2000);
    }
}

async function executeAgent(agentType, agentNum, output) {
    const API_BASE = '/api/v1';
    
    switch(agentType) {
        case 'social_graph':
            const graphData = await mockGraphData();
            output.innerHTML = `<pre>${JSON.stringify(graphData, null, 2)}</pre>`;
            
            // Visualize graph
            createForceDirectedGraph('graphViz1', {
                nodes: graphData.nodes,
                links: graphData.edges
            });
            break;
            
        case 'chemistry':
            const chemistryData = await mockChemistryData();
            output.innerHTML = `<pre>${JSON.stringify(chemistryData, null, 2)}</pre>`;
            
            // Create chemistry chart
            createChemistryRadar(chemistryData);
            break;
            
        case 'meta':
            const patch = document.getElementById('patchSelect').value;
            const metaData = await mockMetaData(patch);
            output.innerHTML = `<pre>${JSON.stringify(metaData, null, 2)}</pre>`;
            break;
            
        case 'adaptation':
            const adaptationData = await mockAdaptationData();
            output.innerHTML = `<pre>${JSON.stringify(adaptationData, null, 2)}</pre>`;
            
            // Create adaptation chart
            createAdaptationLine(adaptationData);
            break;
            
        case 'compatibility':
            const compositionData = await mockCompositionData();
            output.innerHTML = `<pre>${JSON.stringify(compositionData, null, 2)}</pre>`;
            break;
            
        case 'storyteller':
            const insightType = document.getElementById('insightType').value;
            const narrative = await mockNarrative(insightType);
            output.innerHTML = `<pre style="color: #ffffff; line-height: 1.8;">${narrative}</pre>`;
            break;
            
        case 'visualizer':
            const vizType = document.getElementById('vizType').value;
            const vizData = await mockVizData(vizType);
            output.innerHTML = `<pre>${JSON.stringify(vizData, null, 2)}</pre>`;
            
            // Render visualization
            renderVisualization(vizType, vizData);
            break;
    }
}

function createChemistryRadar(data) {
    const canvas = document.getElementById('chemistryChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: data.pairs.map(p => `${p.player1} & ${p.player2}`),
            datasets: [{
                label: 'Synergy Score',
                data: data.pairs.map(p => p.score),
                backgroundColor: 'rgba(0, 200, 150, 0.2)',
                borderColor: 'rgba(0, 200, 150, 1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 1,
                    ticks: { color: '#a8b2c1' },
                    grid: { color: '#2a3f5f' },
                    pointLabels: { color: '#ffffff', font: { size: 10 } }
                }
            }
        }
    });
}

function createAdaptationLine(data) {
    const canvas = document.getElementById('adaptationChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.patches,
            datasets: [{
                label: 'Win Rate',
                data: data.win_rates,
                borderColor: 'rgba(0, 102, 204, 1)',
                backgroundColor: 'rgba(0, 102, 204, 0.1)',
                tension: 0.4,
                fill: true
            }, {
                label: 'Adaptation Speed',
                data: data.adaptation_speeds,
                borderColor: 'rgba(255, 107, 53, 1)',
                backgroundColor: 'rgba(255, 107, 53, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: { color: '#a8b2c1' },
                    grid: { color: '#2a3f5f' }
                },
                x: {
                    ticks: { color: '#a8b2c1' },
                    grid: { color: '#2a3f5f' }
                }
            }
        }
    });
}

function renderVisualization(vizType, data) {
    const container = 'vizCanvas';
    
    switch(vizType) {
        case 'synergy':
            createForceDirectedGraph(container, data);
            break;
        case 'heatmap':
            createHeatmap(container, data);
            break;
        case 'timeline':
            createTimeline(container, data);
            break;
        case 'composition':
            createCompositionBar(container, data);
            break;
    }
}

function createTimeline(containerId, data) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    d3.select(container).select('svg').remove();
    
    const margin = {top: 20, right: 30, bottom: 40, left: 60};
    const width = container.clientWidth - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;
    
    const svg = d3.select(`#${containerId}`)
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);
    
    const x = d3.scaleTime()
        .domain(d3.extent(data, d => new Date(d.date)))
        .range([0, width]);
    
    const y = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.value)])
        .range([height, 0]);
    
    const line = d3.line()
        .x(d => x(new Date(d.date)))
        .y(d => y(d.value));
    
    svg.append('path')
        .datum(data)
        .attr('fill', 'none')
        .attr('stroke', '#0066cc')
        .attr('stroke-width', 3)
        .attr('d', line);
    
    svg.append('g')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(x))
        .selectAll('text')
        .style('fill', '#ffffff');
    
    svg.append('g')
        .call(d3.axisLeft(y))
        .selectAll('text')
        .style('fill', '#ffffff');
}

function createCompositionBar(containerId, data) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    d3.select(container).select('svg').remove();
    
    const margin = {top: 20, right: 30, bottom: 60, left: 60};
    const width = container.clientWidth - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;
    
    const svg = d3.select(`#${containerId}`)
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);
    
    const x = d3.scaleBand()
        .range([0, width])
        .domain(data.map(d => d.name))
        .padding(0.2);
    
    const y = d3.scaleLinear()
        .domain([0, 1])
        .range([height, 0]);
    
    svg.selectAll('rect')
        .data(data)
        .enter()
        .append('rect')
        .attr('x', d => x(d.name))
        .attr('y', d => y(d.winRate))
        .attr('width', x.bandwidth())
        .attr('height', d => height - y(d.winRate))
        .attr('fill', '#00c896');
    
    svg.append('g')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(x))
        .selectAll('text')
        .attr('transform', 'rotate(-45)')
        .style('text-anchor', 'end')
        .style('fill', '#ffffff');
    
    svg.append('g')
        .call(d3.axisLeft(y))
        .selectAll('text')
        .style('fill', '#ffffff');
}

async function runFullPipeline() {
    const statusDiv = document.getElementById('pipelineStatus');
    statusDiv.innerHTML = '<pre style="color: #ffaa00;">Starting full pipeline execution...</pre>';
    
    const agents = ['social_graph', 'chemistry', 'meta', 'adaptation', 'compatibility', 'storyteller', 'visualizer'];
    
    for (const agent of agents) {
        statusDiv.innerHTML += `<pre style="color: #0066cc;">Executing ${agent.replace('_', ' ')} agent...</pre>`;
        await runAgent(agent);
        await sleep(2000);
    }
    
    statusDiv.innerHTML += '<pre style="color: #00c896;">Pipeline execution complete!</pre>';
}

function resetDemo() {
    const cards = document.querySelectorAll('.agent-demo-card');
    cards.forEach(card => {
        card.classList.remove('active');
        const steps = card.querySelectorAll('.step-status');
        steps.forEach(step => {
            step.textContent = 'Pending';
            step.className = 'step-status pending';
        });
        const output = card.querySelector('.demo-output');
        if (output) {
            output.innerHTML = '<pre>Output will appear here...</pre>';
        }
    });
    
    document.getElementById('pipelineStatus').innerHTML = '<pre>Ready to start demo. Click "Run Full Pipeline" to begin...</pre>';
}

// Mock data generators
async function mockGraphData() {
    await sleep(500);
    return {
        nodes: [
            {id: 'player1', name: 'You', radius: 12, color: '#0066cc'},
            {id: 'player2', name: 'Player A', radius: 10, color: '#00c896'},
            {id: 'player3', name: 'Player B', radius: 10, color: '#00c896'},
            {id: 'player4', name: 'Player C', radius: 10, color: '#00c896'},
            {id: 'player5', name: 'Player D', radius: 8, color: '#ffaa00'}
        ],
        edges: [
            {source: 'player1', target: 'player2', value: 0.87},
            {source: 'player1', target: 'player3', value: 0.72},
            {source: 'player1', target: 'player4', value: 0.91},
            {source: 'player2', target: 'player3', value: 0.68},
            {source: 'player3', target: 'player4', value: 0.75}
        ]
    };
}

async function mockChemistryData() {
    await sleep(500);
    return {
        pairs: [
            {player1: 'You', player2: 'Player A', score: 0.87},
            {player1: 'You', player2: 'Player B', score: 0.72},
            {player1: 'You', player2: 'Player C', score: 0.91},
            {player1: 'You', player2: 'Player D', score: 0.63}
        ],
        average_synergy: 0.78
    };
}

async function mockMetaData(patch) {
    await sleep(500);
    return {
        patch_version: patch,
        win_rate: 0.56,
        games_played: 45,
        meta_shifts: ['ADC buffs', 'Jungle nerfs'],
        impact_score: 0.72
    };
}

async function mockAdaptationData() {
    await sleep(500);
    return {
        patches: ['14.17', '14.18', '14.19', '14.20', '14.21'],
        win_rates: [0.52, 0.48, 0.55, 0.59, 0.57],
        adaptation_speeds: [0.8, 0.6, 0.9, 0.7, 0.85],
        latency: 1.8
    };
}

async function mockCompositionData() {
    await sleep(500);
    return {
        top_compositions: [
            {comp_id: 1, predicted_wr: 0.62, confidence: 0.85},
            {comp_id: 2, predicted_wr: 0.59, confidence: 0.79},
            {comp_id: 3, predicted_wr: 0.58, confidence: 0.82}
        ]
    };
}

async function mockNarrative(insightType) {
    await sleep(500);
    const narratives = {
        synergy: "Your synergy with Player C peaked in patch 14.20, driven by coordinated objective control and complementary champion pools. Your duo win rate increased by 15% after adopting scaling compositions, demonstrating strong adaptability to the mid-game meta shift.",
        adaptation: "You adapted to the latest ADC patch changes faster than 78% of players in your MMR bracket. Your adaptation speed improved from 2.3 patches to 1.8 patches, showing enhanced meta awareness and champion pool flexibility.",
        meta: "After patch 14.19 when assassins fell out of favor, your team successfully shifted toward objective-based compositions. This transition was 40% faster than similar MMR teams, resulting in a 12% win rate improvement over the following 30 games.",
        season: "This season, your squad evolved from struggling in early-mid meta transitions to mastering adaptive drafts by season's end. From your initial 48% win rate in patch 14.15 to your current 59% in patch 14.21, you demonstrated a 22% performance improvement driven by stronger synergy development and faster meta adaptation."
    };
    return narratives[insightType] || "Generating narrative insight...";
}

async function mockVizData(vizType) {
    await sleep(500);
    
    switch(vizType) {
        case 'synergy':
            return await mockGraphData();
        case 'heatmap':
            return [
                {patch: '14.17', win_rate: 0.52},
                {patch: '14.18', win_rate: 0.48},
                {patch: '14.19', win_rate: 0.55},
                {patch: '14.20', win_rate: 0.59},
                {patch: '14.21', win_rate: 0.57}
            ];
        case 'timeline':
            return [
                {date: '2024-09-01', value: 0.52},
                {date: '2024-09-15', value: 0.48},
                {date: '2024-10-01', value: 0.55},
                {date: '2024-10-15', value: 0.59},
                {date: '2024-11-01', value: 0.57}
            ];
        case 'composition':
            return [
                {name: 'Comp 1', winRate: 0.62},
                {name: 'Comp 2', winRate: 0.59},
                {name: 'Comp 3', winRate: 0.58},
                {name: 'Comp 4', winRate: 0.56},
                {name: 'Comp 5', winRate: 0.54}
            ];
    }
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
