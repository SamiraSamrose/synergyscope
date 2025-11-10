//# File: frontend/static/js/synergy_graph.js
//# Synergy network graph visualization

// Synergy Graph Visualization
// D3.js force-directed graph for player relationships

class SynergyGraph {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.width = options.width || this.container.clientWidth;
        this.height = options.height || 600;
        this.options = {
            nodeRadius: options.nodeRadius || 10,
            linkDistance: options.linkDistance || 100,
            chargeStrength: options.chargeStrength || -400,
            ...options
        };
        
        this.svg = null;
        this.simulation = null;
        this.initialize();
    }
    
    initialize() {
        // Clear existing
        d3.select(this.container).select('svg').remove();
        
        // Create SVG
        this.svg = d3.select(this.container)
            .append('svg')
            .attr('width', this.width)
            .attr('height', this.height)
            .attr('viewBox', [0, 0, this.width, this.height]);
        
        // Add arrow marker for directed edges
        this.svg.append('defs').selectAll('marker')
            .data(['synergy'])
            .join('marker')
            .attr('id', d => d)
            .attr('viewBox', '0 -5 10 10')
            .attr('refX', 20)
            .attr('refY', 0)
            .attr('markerWidth', 6)
            .attr('markerHeight', 6)
            .attr('orient', 'auto')
            .append('path')
            .attr('fill', '#2a3f5f')
            .attr('d', 'M0,-5L10,0L0,5');
        
        // Create groups
        this.linkGroup = this.svg.append('g').attr('class', 'links');
        this.nodeGroup = this.svg.append('g').attr('class', 'nodes');
        this.labelGroup = this.svg.append('g').attr('class', 'labels');
        
        // Initialize simulation
        this.simulation = d3.forceSimulation()
            .force('link', d3.forceLink().id(d => d.id).distance(this.options.linkDistance))
            .force('charge', d3.forceManyBody().strength(this.options.chargeStrength))
            .force('center', d3.forceCenter(this.width / 2, this.height / 2))
            .force('collision', d3.forceCollide().radius(this.options.nodeRadius * 2));
    }
    
    render(graphData) {
        // Store data
        this.graphData = graphData;
        
        // Render links
        this.renderLinks(graphData.links);
        
        // Render nodes
        this.renderNodes(graphData.nodes);
        
        // Render labels
        this.renderLabels(graphData.nodes);
        
        // Start simulation
        this.simulation
            .nodes(graphData.nodes)
            .on('tick', () => this.ticked());
        
        this.simulation.force('link')
            .links(graphData.links);
        
        this.simulation.alpha(1).restart();
    }
    
    renderLinks(links) {
        const link = this.linkGroup
            .selectAll('line')
            .data(links)
            .join('line')
            .attr('class', 'synergy-link')
            .attr('stroke', d => this.getLinkColor(d.value))
            .attr('stroke-width', d => this.getLinkWidth(d.value))
            .attr('stroke-opacity', 0.6);
        
        // Add link labels
        this.linkGroup
            .selectAll('text')
            .data(links)
            .join('text')
            .attr('class', 'link-label')
            .attr('text-anchor', 'middle')
            .attr('font-size', 10)
            .attr('fill', '#a8b2c1')
            .text(d => (d.value * 100).toFixed(0) + '%');
        
        this.linkElements = link;
    }
    
    renderNodes(nodes) {
        const node = this.nodeGroup
            .selectAll('circle')
            .data(nodes)
            .join('circle')
            .attr('class', 'synergy-node')
            .attr('r', d => d.radius || this.options.nodeRadius)
            .attr('fill', d => d.color || this.getNodeColor(d))
            .attr('stroke', '#ffffff')
            .attr('stroke-width', 2)
            .call(this.drag());
        
        // Add tooltip
        node.append('title')
            .text(d => `${d.name}\nWin Rate: ${(d.win_rate * 100).toFixed(1)}%\nGames: ${d.value || 0}`);
        
        // Add hover effects
        node.on('mouseenter', (event, d) => this.highlightNode(d))
            .on('mouseleave', () => this.resetHighlight());
        
        this.nodeElements = node;
    }
    
    renderLabels(nodes) {
        const labels = this.labelGroup
            .selectAll('text')
            .data(nodes)
            .join('text')
            .attr('class', 'node-label')
            .attr('text-anchor', 'middle')
            .attr('dy', -15)
            .attr('font-size', 12)
            .attr('font-weight', 'bold')
            .attr('fill', '#ffffff')
            .attr('stroke', '#1a1a2e')
            .attr('stroke-width', 3)
            .attr('paint-order', 'stroke')
            .text(d => d.name);
        
        this.labelElements = labels;
    }
    
    ticked() {
        if (this.linkElements) {
            this.linkElements
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);
            
            // Update link labels
            this.linkGroup.selectAll('text')
                .attr('x', d => (d.source.x + d.target.x) / 2)
                .attr('y', d => (d.source.y + d.target.y) / 2);
        }
        
        if (this.nodeElements) {
            this.nodeElements
                .attr('cx', d => d.x)
                .attr('cy', d => d.y);
        }
        
        if (this.labelElements) {
            this.labelElements
                .attr('x', d => d.x)
                .attr('y', d => d.y);
        }
    }
    
    drag() {
        function dragstarted(event, d) {
            if (!event.active) this.simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }
        
        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }
        
        function dragended(event, d) {
            if (!event.active) this.simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }
        
        return d3.drag()
            .on('start', dragstarted.bind(this))
            .on('drag', dragged.bind(this))
            .on('end', dragended.bind(this));
    }
    
    highlightNode(node) {
        // Fade non-connected nodes
        this.nodeElements
            .transition()
            .duration(200)
            .attr('opacity', d => {
                if (d === node) return 1;
                const connected = this.graphData.links.some(
                    l => (l.source === node && l.target === d) || 
                         (l.target === node && l.source === d)
                );
                return connected ? 1 : 0.2;
            });
        
        // Highlight connected links
        this.linkElements
            .transition()
            .duration(200)
            .attr('stroke-opacity', l => 
                (l.source === node || l.target === node) ? 1 : 0.1
            )
            .attr('stroke-width', l => 
                (l.source === node || l.target === node) ? 
                this.getLinkWidth(l.value) * 1.5 : this.getLinkWidth(l.value)
            );
    }
    
    resetHighlight() {
        this.nodeElements
            .transition()
            .duration(200)
            .attr('opacity', 1);
        
        this.linkElements
            .transition()
            .duration(200)
            .attr('stroke-opacity', 0.6)
            .attr('stroke-width', d => this.getLinkWidth(d.value));
    }
    
    getLinkColor(value) {
        if (value > 0.8) return '#00c896';
        if (value > 0.6) return '#0066cc';
        if (value > 0.4) return '#ffaa00';
        return '#ff6b35';
    }
    
    getLinkWidth(value) {
        return 1 + (value * 5);
    }
    
    getNodeColor(node) {
        if (node.win_rate > 0.6) return '#00c896';
        if (node.win_rate > 0.5) return '#0066cc';
        return '#ffaa00';
    }
    
    destroy() {
        if (this.simulation) {
            this.simulation.stop();
        }
        if (this.svg) {
            this.svg.remove();
        }
    }
}
