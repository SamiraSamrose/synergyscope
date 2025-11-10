//# File: frontend/static/js/patch_timeline.js
// Patch Timeline Visualization
class PatchTimeline {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.margin = {top: 20, right: 30, bottom: 40, left: 60};
        this.width = this.container.clientWidth - this.margin.left - this.margin.right;
        this.height = 400 - this.margin.top - this.margin.bottom;
    }
    
    render(data) {
        d3.select(this.container).select('svg').remove();
        
        const svg = d3.select(this.container)
            .append('svg')
            .attr('width', this.width + this.margin.left + this.margin.right)
            .attr('height', this.height + this.margin.top + this.margin.bottom)
            .append('g')
            .attr('transform', `translate(${this.margin.left},${this.margin.top})`);
        
        const x = d3.scaleTime()
            .domain(d3.extent(data, d => new Date(d.date)))
            .range([0, this.width]);
        
        const y = d3.scaleLinear()
            .domain([0, d3.max(data, d => d.value)])
            .nice()
            .range([this.height, 0]);
        
        const line = d3.line()
            .x(d => x(new Date(d.date)))
            .y(d => y(d.value))
            .curve(d3.curveMonotoneX);
        
        svg.append('path')
            .datum(data)
            .attr('fill', 'none')
            .attr('stroke', '#0066cc')
            .attr('stroke-width', 3)
            .attr('d', line);
        
        svg.selectAll('circle')
            .data(data)
            .join('circle')
            .attr('cx', d => x(new Date(d.date)))
            .attr('cy', d => y(d.value))
            .attr('r', 5)
            .attr('fill', '#00c896')
            .attr('stroke', '#ffffff')
            .attr('stroke-width', 2);
        
        svg.append('g')
            .attr('transform', `translate(0,${this.height})`)
            .call(d3.axisBottom(x))
            .selectAll('text')
            .style('fill', '#ffffff');
        
        svg.append('g')
            .call(d3.axisLeft(y))
            .selectAll('text')
            .style('fill', '#ffffff');
    }
}