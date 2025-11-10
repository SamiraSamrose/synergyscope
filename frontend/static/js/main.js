//# File: frontend/static/js/main.js

// SynergyScope Main JavaScript
// Core dashboard functionality and API communication

const API_BASE_URL = '/api/v1';

// Initialize Dashboard
function initializeDashboard() {
    console.log('SynergyScope Dashboard Initialized');
    checkSystemHealth();
    loadLatestInsights();
}

// Check System Health
async function checkSystemHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        
        console.log('System Health:', data);
        updateAgentStatus(data.services);
    } catch (error) {
        console.error('Health check failed:', error);
    }
}

// Update Agent Status Indicators
function updateAgentStatus(services) {
    const agentMapping = {
        'api': 'social-graph',
        'neptune': 'chemistry',
        'sagemaker': 'adaptation',
        'bedrock': 'storyteller'
    };
    
    for (const [service, status] of Object.entries(services)) {
        const agentCard = document.querySelector(`[data-agent="${agentMapping[service]}"]`);
        if (agentCard) {
            const indicator = agentCard.querySelector('.status-dot');
            if (indicator) {
                indicator.className = status === 'operational' ? 
                    'status-dot status-active' : 
                    'status-dot status-inactive';
            }
        }
    }
}

// Analyze Summoner
async function analyzeSummoner() {
    const summonerName = document.getElementById('summonerName').value;
    const region = document.getElementById('region').value;
    const statusDiv = document.getElementById('analysisStatus');
    
    if (!summonerName) {
        statusDiv.innerHTML = '<p style="color: var(--error);">Please enter a summoner name</p>';
        return;
    }
    
    statusDiv.innerHTML = '<p style="color: var(--warning);">Analyzing... This may take 2-5 minutes</p>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/summoner/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                summoner_name: summonerName,
                region: region,
                match_count: 100,
                include_ranked_only: true
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            statusDiv.innerHTML = `
                <p style="color: var(--success);">Analysis Started!</p>
                <p>Analysis ID: ${data.analysis_id}</p>
                <p>Estimated time: ${data.estimated_time}</p>
            `;
            
            pollAnalysisStatus(data.analysis_id);
        } else {
            statusDiv.innerHTML = `<p style="color: var(--error);">Analysis failed: ${data.detail}</p>`;
        }
    } catch (error) {
        statusDiv.innerHTML = `<p style="color: var(--error);">Error: ${error.message}</p>`;
    }
}

// Poll Analysis Status
async function pollAnalysisStatus(analysisId) {
    console.log('Polling analysis status:', analysisId);
}

// Load Latest Insights
async function loadLatestInsights() {
    const insightsContainer = document.getElementById('latestInsights');
    console.log('Loading latest insights...');
}

// Send Chat Message
async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const messagesDiv = document.getElementById('chatMessages');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message
    const userMessage = document.createElement('div');
    userMessage.className = 'chat-message user';
    userMessage.innerHTML = `<p>${message}</p>`;
    messagesDiv.appendChild(userMessage);
    
    input.value = '';
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    
    try {
        const response = await fetch(`${API_BASE_URL}/meta/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                summoner_id: 'current_user',
                question: message
            })
        });
        
        const data = await response.json();
        
        // Add bot response
        const botMessage = document.createElement('div');
        botMessage.className = 'chat-message bot';
        botMessage.innerHTML = `<p>${data.response}</p>`;
        messagesDiv.appendChild(botMessage);
        
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    } catch (error) {
        console.error('Chat error:', error);
        
        const errorMessage = document.createElement('div');
        errorMessage.className = 'chat-message bot';
        errorMessage.innerHTML = '<p>Sorry, I encountered an error. Please try again.</p>';
        messagesDiv.appendChild(errorMessage);
    }
}

// Load Preview Visualizations
function loadPreviewVisualizations() {
    createSynergyNetworkPreview();
    createAdaptationCurvePreview();
    createMetaTimelinePreview();
}

// Create Synergy Network Preview
function createSynergyNetworkPreview() {
    const canvas = document.getElementById('synergyNetworkPreview');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
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

// Event Listeners
document.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        if (document.activeElement.id === 'summonerName' || 
            document.activeElement.id === 'region') {
            analyzeSummoner();
        } else if (document.activeElement.id === 'chatInput') {
            sendChatMessage();
        }
    }
});
