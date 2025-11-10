//# File: frontend/static/js/adaptation_heatmap.js
//# Adaptation performance heatmap visualization

// Adaptation Heatmap Visualization
// Shows win rate changes across patches

class AdaptationHeatmap {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            margin: { top: 50, right: 30, bottom: 100, left: 100 },
            cellHeight: 40,
            cellPadding: 2,
            ...options
        };
        
        this.width = (options.width || this.container.clientWidth) - this.options.margin.left - this.options.margin.right;
        this.height = null; // Will be calculated based on data
        
        this.svg = null;
        this.colorScale = null;
        this.initialize();
    }
    
    initialize() {
        // Clear existing
        d3.select(this.container).select('svg').remove();
        
        // Create color scale
        this.colorScale = d3.scaleSequential()
            .interpolator(d3.interpolateRdYlGn)
            .domain([0.3, 0.7]); // Win rate range
    }
    
    render(data) {
        // Calculate dimensions
        const patches = [...new Set(data.map(d => d.patch))];
        const metrics = [...new Set(data.map(d => d.metric))];
        
        this.height = metrics.length * this.options.cellHeight;
        
        // Create SVG
        this.svg = d3.select(this.container)
            .append('svg')
            .attr('width', this.width + this.options.margin.left + this.options.margin.right)
            .attr('height', this.height + this.options.margin.top + this.options.margin.bottom)
            .append('g')
            .attr('transform', `translate(${this.options.margin.left},${this.options.margin.top})`);
        
        // Scales
        const x = d3.scaleBand()
            .range([0, this.width])
            .domain(patches)
            .padding(0.05);
        
        const y = d3.scaleBand()
            .range([0, this.height])
            .domain(metrics)
            .padding(0.05);
        
        // X axis
        this.svg.append('g')
            .attr('class', 'x-axis')
            .attr('transform', `translate(0,${this.height})`)
            .call(d3.axisBottom(x))
            .selectAll('text')
            .attr('transform', 'rotate(-45)')
            .style('text-anchor', 'end')
            .style('fill', '#ffffff')
            .style('font-size', '12px');
        
        // Y axis
        this.svg.append('g')
            .attr('class', 'y-axis')
            .call(d3.axisLeft(y))
            .selectAll('text')
            .style('fill', '#ffffff')
            .style('font-size', '12px');
        
        // Cells
        const cells = this.svg.selectAll('.cell')
            .data(data)
            .join('rect')
            .attr('class', 'cell')
            .attr('x', d => x(d.patch))
            .attr('y', d => y(d.metric))
            .attr('width', x.bandwidth())
            .attr('height', y.bandwidth())
            .attr('fill', d => this.colorScale(d.value))
            .attr('stroke', '#1a1a2e')
            .attr('stroke-width', 1)
            .style('cursor', 'pointer');
        
        // Add cell values
        this.svg.selectAll('.cell-text')
            .data(data)
            .join('text')
            .attr('class', 'cell-text')
            .attr('x', d => x(d.patch) + x.bandwidth() / 2)
            .attr('y', d => y(d.metric) + y.bandwidth() / 2)
            .attr('text-anchor', 'middle')
            .attr('dominant-baseline', 'middle')
            .attr('fill', d => d.value > 0.5 ? '#1a1a2e' : '#ffffff')
            .attr('font-size', '12px')
            .attr('font-weight', 'bold')
            .text(d => (d.value * 100).toFixed(0) + '%');
        
        // Tooltips
        cells.append('title')
            .text(d => `${d.patch} - ${d.metric}: ${(d.value * 100).toFixed(1)}%`);
        
        // Add color legend
        this.addLegend();
        
        // Hover effects
        cells.on('mouseenter', function(event, d) {
            d3.select(this)
                .transition()
                .duration(200)
                .attr('stroke-width', 3)
                .attr('stroke', '#ffffff');
        })
        .on('mouseleave', function() {
            d3.select(this)
                .transition()
                .duration(200)
                .attr('stroke-width', 1)
                .attr('stroke', '#1a1a2e');
        });
    }
    
    addLegend() {
        const legendWidth = 200;
        const legendHeight = 20;
        
        const legendSvg = this.svg.append('g')
            .attr('class', 'legend')
            .attr('transform', `translate(${this.width - legendWidth}, -40)`);
        
        // Create gradient
        const defs = legendSvg.append('defs');
        const gradient = defs.append('linearGradient')
            .attr('id', 'legend-gradient')
            .attr('x1', '0%')
            .attr('x2', '100%');
        
        gradient.selectAll('stop')
            .data([
                { offset: '0%', color: this.colorScale(0.3) },
                { offset: '50%', color: this.colorScale(0.5) },
                { offset: '100%', color: this.colorScale(0.7) }
            ])
            .join('stop')
            .attr('offset', d => d.offset)
            .attr('stop-color', d => d.color);
        
        // Legend rectangle
        legendSvg.append('rect')
            .attr('width', legendWidth)
            .attr('height', legendHeight)
            .style('fill', 'url(#legend-gradient)')
            .attr('stroke', '#ffffff')
            .attr('stroke-width', 1);
        
        // Legend labels
        legendSvg.append('text')
            .attr('x', 0)
            .attr('y', legendHeight + 15)
            .attr('fill', '#ffffff')
            .attr('font-size', '10px')
            .text('30%');
        
        legendSvg.append('text')
            .attr('x', legendWidth)
            .attr('y', legendHeight + 15)
            .attr('fill', '#ffffff')
            .attr('font-size', '10px')
            .attr('text-anchor', 'end')
            .text('70%');
    }
}
