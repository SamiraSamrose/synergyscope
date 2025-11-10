//# File: frontend/static/js/visualizations.js
//# Purpose: D3.js and Chart.js visualization implementations

// Visualization Functions for SynergyScope
// Implements all chart and graph visualizations

// Create Synergy Network Preview
function createSynergyNetworkPreview() {
    const canvas = document.getElementById('synergyNetworkPreview');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Sample data
    const sampleData = {
        labels: ['You', 'Player A', 'Player B', 'Player C', 'Player D'],
        datasets: [{
            label: 'Synergy Strength',
            data: [0.85, 0.72, 0.68, 0.91, 0.63],
            backgroundColor: [
                'rgba(0, 102, 204, 0.6)',
                'rgba(0, 200, 150, 0.6)',
                'rgba(255, 170, 0, 0.6)',
                'rgba(0, 200, 150, 0.8)',
                'rgba(255, 107, 53, 0.6)'
            ],
            borderColor: [
                'rgba(0, 102, 204, 1)',
                'rgba(0, 200, 150, 1)',
                'rgba(255, 170, 0, 1)',
                'rgba(0, 200, 150, 1)',
                'rgba(255, 107, 53, 1)'
            ],
            borderWidth: 2
        }]
    };
    
    new Chart(ctx, {
        type: 'radar',
        data: sampleData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 1,
                    ticks: {
                        stepSize: 0.2,
                        color: '#a8b2c1'
                    },
                    grid: {
                        color: '#2a3f5f'
                    },
                    pointLabels: {
                        color: '#ffffff',
                        font: {
                            size: 12
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// Create Adaptation Curve Preview
function createAdaptationCurvePreview() {
    const canvas = document.getElementById('adaptationCurvePreview');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    const patchData = {
        labels: ['14.15', '14.16', '14.17', '14.18', '14.19', '14.20', '14.21'],
        datasets: [{
            label: 'Win Rate',
            data: [0.52, 0.48, 0.51, 0.55, 0.58, 0.62, 0.59],
            borderColor: 'rgba(0, 200, 150, 1)',
            backgroundColor: 'rgba(0, 200, 150, 0.1)',
            borderWidth: 3,
            tension: 0.4,
            fill: true,
            pointRadius: 5,
            pointBackgroundColor: 'rgba(0, 200, 150, 1)',
            pointBorderColor: '#1a1a2e',
            pointBorderWidth: 2
        }]
    };
    
    new Chart(ctx, {
        type: 'line',
        data: patchData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false,
                    min: 0.4,
                    max: 0.7,
                    ticks: {
                        callback: function(value) {
                            return (value * 100).toFixed(0) + '%';
                        },
                        color: '#a8b2c1'
                    },
                    grid: {
                        color: '#2a3f5f'
                    }
                },
                x: {
                    ticks: {
                        color: '#a8b2c1'
                    },
                    grid: {
                        color: '#2a3f5f'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: '#16213e',
                    titleColor: '#ffffff',
                    bodyColor: '#a8b2c1',
                    borderColor: '#0066cc',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            return 'Win Rate: ' + (context.parsed.y * 100).toFixed(1) + '%';
                        }
                    }
                }
            }
        }
    });
}

// Create Meta Timeline Preview
function createMetaTimelinePreview() {
    const canvas = document.getElementById('metaTimelinePreview');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    const metaData = {
        labels: ['W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7', 'W8'],
        datasets: [
            {
                label: 'Games Played',
                data: [25, 32, 28, 35, 40, 38, 42, 36],
                backgroundColor: 'rgba(0, 102, 204, 0.6)',
                borderColor: 'rgba(0, 102, 204, 1)',
                borderWidth: 2
            },
            {
                label: 'Wins',
                data: [13, 18, 15, 20, 25, 23, 26, 22],
                backgroundColor: 'rgba(0, 200, 150, 0.6)',
                borderColor: 'rgba(0, 200, 150, 1)',
                borderWidth: 2
            }
        ]
    };
    
    new Chart(ctx, {
        type: 'bar',
        data: metaData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#a8b2c1'
                    },
                    grid: {
                        color: '#2a3f5f'
                    }
                },
                x: {
                    ticks: {
                        color: '#a8b2c1'
                    },
                    grid: {
                        color: '#2a3f5f'
                    }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color: '#ffffff'
                    }
                }
            }
        }
    });
}

// D3.js Force-Directed Graph
function createForceDirectedGraph(containerId, graphData) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const width = container.clientWidth;
    const height = container.clientHeight || 600;
    
    // Clear existing SVG
    d3.select(container).select('svg').remove();
    
    const svg = d3.select(container)
        .append('svg')
        .attr('width', width)
        .attr('height', height);
    
    const simulation = d3.forceSimulation(graphData.nodes)
        .force('link', d3.forceLink(graphData.links).id(d => d.id).distance(100))
        .force('charge', d3.forceManyBody().strength(-400))
        .force('center', d3.forceCenter(width / 2, height / 2));
    
    // Create links
    const link = svg.append('g')
        .selectAll('line')
        .data(graphData.links)
        .enter()
        .append('line')
        .attr('stroke', '#2a3f5f')
        .attr('stroke-width', d => Math.sqrt(d.value) * 2);
    
    // Create nodes
    const node = svg.append('g')
        .selectAll('circle')
        .data(graphData.nodes)
        .enter()
        .append('circle')
        .attr('r', d => d.radius || 8)
        .attr('fill', d => d.color || '#0066cc')
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));
    
    // Add labels
    const labels = svg.append('g')
        .selectAll('text')
        .data(graphData.nodes)
        .enter()
        .append('text')
        .text(d => d.name)
        .attr('font-size', 10)
        .attr('fill', '#ffffff')
        .attr('dx', 12)
        .attr('dy', 4);
    
    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        node
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);
        
        labels
            .attr('x', d => d.x)
            .attr('y', d => d.y);
    });
    
    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }
    
    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }
    
    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
}

// Heatmap Visualization
function createHeatmap(containerId, heatmapData) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const margin = {top: 30, right: 30, bottom: 50, left: 100};
    const width = container.clientWidth - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;
    
    // Clear existing
    d3.select(container).select('svg').remove();
    
    const svg = d3.select(container)
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);
    
    // Build X scales and axis
    const x = d3.scaleBand()
        .range([0, width])
        .domain(heatmapData.map(d => d.patch))
        .padding(0.05);
    
    svg.append('g')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(x))
        .selectAll('text')
        .style('fill', '#ffffff');
    
    // Build Y scales and axis
    const y = d3.scaleBand()
        .range([height, 0])
        .domain(['Win Rate', 'Games', 'Adaptation'])
        .padding(0.05);
    
    svg.append('g')
        .call(d3.axisLeft(y))
        .selectAll('text')
        .style('fill', '#ffffff');
    
    // Build color scale
    const colorScale = d3.scaleLinear()
        .range(['#ff4444', '#ffaa00', '#00c896'])
        .domain([0, 0.5, 1]);
    
    // Add rectangles
    svg.selectAll()
        .data(heatmapData)
        .enter()
        .append('rect')
        .attr('x', d => x(d.patch))
        .attr('y', () => y('Win Rate'))
        .attr('width', x.bandwidth())
        .attr('height', y.bandwidth())
        .style('fill', d => colorScale(d.win_rate));
}
