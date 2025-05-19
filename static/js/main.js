// Theme management functions
function setTheme(themeName) {
    document.documentElement.setAttribute('data-theme', themeName);
    localStorage.setItem('theme', themeName);
    updateThemeToggleIcon(themeName);
}

function toggleTheme() {
    const currentTheme = localStorage.getItem('theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    updateCharts();
}

function updateThemeToggleIcon(themeName) {
    const themeToggleIcon = document.querySelector('#theme-toggle i');
    if (themeName === 'dark') {
        themeToggleIcon.classList.remove('fa-moon');
        themeToggleIcon.classList.add('fa-sun');
    } else {
        themeToggleIcon.classList.remove('fa-sun');
        themeToggleIcon.classList.add('fa-moon');
    }
}

function updateCharts() {
    // If charts are already rendered, update them with new theme colors
    const matchChart = document.getElementById('match-chart');
    const skillsChart = document.getElementById('skills-chart');
    
    if (matchChart && matchChart._fullLayout) {
        const currentTheme = localStorage.getItem('theme') || 'light';
        const bgColor = currentTheme === 'dark' ? '#1e1e1e' : 'white';
        const fontColor = currentTheme === 'dark' ? '#e5e7eb' : 'rgba(0, 0, 0, 0.8)';
        
        Plotly.relayout('match-chart', {
            paper_bgcolor: bgColor,
            font: { color: fontColor }
        });
    }
    
    if (skillsChart && skillsChart._fullLayout) {
        const currentTheme = localStorage.getItem('theme') || 'light';
        const bgColor = currentTheme === 'dark' ? '#1e1e1e' : 'white';
        const fontColor = currentTheme === 'dark' ? '#e5e7eb' : 'rgba(0, 0, 0, 0.8)';
        
        Plotly.relayout('skills-chart', {
            paper_bgcolor: bgColor,
            plot_bgcolor: currentTheme === 'dark' ? 'rgba(30, 30, 30, 0.8)' : 'rgba(240, 242, 246, 0.8)',
            font: { color: fontColor }
        });
    }
}

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize theme from localStorage or default to light
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
    
    // Add event listener for theme toggle button
    document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
    // Get form element
    const resumeForm = document.getElementById('resume-form');
    
    // Add submit event listener
    resumeForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Show loading spinner
        document.getElementById('loading').classList.remove('d-none');
        document.getElementById('results-section').classList.add('d-none');
        
        // Create FormData object
        const formData = new FormData(resumeForm);
        
        // Send AJAX request
        fetch('/analyze', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Something went wrong');
                });
            }
            return response.json();
        })
        .then(data => {
            // Hide loading spinner
            document.getElementById('loading').classList.add('d-none');
            
            // Debug: Log the data received from the server
            console.log('Data received from server:', data);
            console.log('Skills found:', data.skills_found);
            console.log('Skills missing:', data.skills_missing);
            console.log('Suggestions:', data.suggestions);
            
            // Display results
            displayResults(data);
            
            // Show results section
            document.getElementById('results-section').classList.remove('d-none');
            
            // Scroll to results
            document.getElementById('results-section').scrollIntoView({
                behavior: 'smooth'
            });
        })
        .catch(error => {
            // Hide loading spinner
            document.getElementById('loading').classList.add('d-none');
            
            // Show error alert
            alert('Error: ' + error.message);
        });
    });
});

/**
 * Display analysis results
 * @param {Object} data - Analysis results from the server
 */
function displayResults(data) {
    // Display match score
    document.getElementById('match-score').textContent = data.match_percentage + '%';
    console.log('Match percentage:', data.match_percentage);
    
    // Display skills found
    const skillsFoundElement = document.getElementById('skills-found');
    skillsFoundElement.innerHTML = '';
    
    // Check if skills_found exists and is an array
    if (data.skills_found && Array.isArray(data.skills_found) && data.skills_found.length > 0) {
        data.skills_found.forEach(skill => {
            const skillTag = document.createElement('span');
            skillTag.className = 'skill-tag found';
            skillTag.textContent = skill;
            skillsFoundElement.appendChild(skillTag);
        });
    } else {
        skillsFoundElement.innerHTML = '<p class="text-muted">No matching skills found</p>';
    }
    
    // Display skills missing
    const skillsMissingElement = document.getElementById('skills-missing');
    skillsMissingElement.innerHTML = '';
    
    // Check if skills_missing exists and is an array
    if (data.skills_missing && Array.isArray(data.skills_missing) && data.skills_missing.length > 0) {
        data.skills_missing.forEach(skill => {
            const skillTag = document.createElement('span');
            skillTag.className = 'skill-tag missing';
            skillTag.textContent = skill;
            skillsMissingElement.appendChild(skillTag);
        });
    } else {
        skillsMissingElement.innerHTML = '<p class="text-muted">No missing skills!</p>';
    }
    
    // Display suggestions
    const suggestionsElement = document.getElementById('suggestions');
    suggestionsElement.innerHTML = '';
    
    // Check if suggestions exists and is an array
    if (data.suggestions && Array.isArray(data.suggestions) && data.suggestions.length > 0) {
        data.suggestions.forEach(suggestion => {
            const li = document.createElement('li');
            li.textContent = suggestion;
            suggestionsElement.appendChild(li);
        });
    } else {
        suggestionsElement.innerHTML = '<p class="text-muted">No suggestions available</p>';
    }
    
    // Create match chart
    createMatchChart(data.match_chart);
    
    // Create skills chart
    createSkillsChart(data.skills_chart);
}

/**
 * Create match score chart
 * @param {Object} chartData - Match chart data
 */
function createMatchChart(chartData) {
    const currentTheme = localStorage.getItem('theme') || 'light';
    const isDarkMode = currentTheme === 'dark';
    
    const score = chartData.overall_match;
    
    const data = [
        {
            type: "indicator",
            mode: "gauge+number",
            value: score,
            title: {
                text: "Match Score",
                font: {
                    family: 'Inter, Arial, sans-serif',
                    size: 20,
                    color: isDarkMode ? '#e5e7eb' : '#2d3748'
                }
            },
            gauge: {
                axis: {
                    range: [0, 100],
                    tickwidth: 1,
                    tickcolor: isDarkMode ? '#a0aec0' : '#4b5563',
                    tickfont: {
                        family: 'Inter, Arial, sans-serif',
                        size: 12,
                        color: isDarkMode ? '#a0aec0' : '#4b5563'
                    }
                },
                bar: { color: '#4361ee' },
                bgcolor: isDarkMode ? '#2d3748' : '#f3f4f6',
                borderwidth: 0,
                bordercolor: isDarkMode ? '#4a5568' : '#e2e8f0',
                steps: [
                    { range: [0, 30], color: isDarkMode ? "#7f1d1d" : "#fecaca" },
                    { range: [30, 70], color: isDarkMode ? "#92400e" : "#fed7aa" },
                    { range: [70, 100], color: isDarkMode ? "#064e3b" : "#d1fae5" }
                ],
                threshold: {
                    line: { color: isDarkMode ? "white" : "black", width: 2 },
                    thickness: 0.75,
                    value: score
                }
            },
            number: {
                font: {
                    family: 'Inter, Arial, sans-serif',
                    size: 36,
                    color: isDarkMode ? '#e5e7eb' : '#2d3748',
                    weight: 'bold'
                },
                suffix: '%'
            },
            domain: { x: [0, 1], y: [0, 1] }
        }
    ];

    const layout = {
        width: 320,
        height: 280,
        margin: { t: 40, r: 25, l: 25, b: 25 },
        paper_bgcolor: isDarkMode ? '#1e1e1e' : 'white',
        font: {
            family: 'Inter, Arial, sans-serif',
            color: isDarkMode ? '#e5e7eb' : '#2d3748'
        },
        annotations: [
            {
                text: 'Overall Match',
                showarrow: false,
                font: {
                    family: 'Inter, Arial, sans-serif',
                    size: 14,
                    color: isDarkMode ? '#a0aec0' : '#4b5563'
                },
                x: 0.5,
                y: 0.85,
                xref: 'paper',
                yref: 'paper'
            }
        ]
    };

    const config = {
        responsive: true,
        displayModeBar: false
    };

    Plotly.newPlot('match-chart', data, layout, config);
}

/**
 * Create skills chart
 * @param {Object} chartData - Skills chart data
 */
function createSkillsChart(chartData) {
    const currentTheme = localStorage.getItem('theme') || 'light';
    const isDarkMode = currentTheme === 'dark';
    
    // Prepare data for chart
    const skillsData = chartData.skills_data;
    
    // Count skills by status
    const inBoth = skillsData.filter(s => s.in_resume && s.in_job).length;
    const inResumeOnly = skillsData.filter(s => s.in_resume && !s.in_job).length;
    const inJobOnly = skillsData.filter(s => !s.in_resume && s.in_job).length;

    const data = [{
        values: [inBoth, inResumeOnly, inJobOnly],
        labels: ['Matching Skills', 'Extra Skills in Resume', 'Missing Skills'],
        type: 'pie',
        textinfo: 'label+percent',
        insidetextorientation: 'horizontal',
        textposition: 'inside',
        hole: 0.35,
        pull: [0.05, 0, 0],
        marker: {
            colors: isDarkMode ? 
                ['#065f46', '#1e40af', '#991b1b'] : 
                ['#10b981', '#3b82f6', '#ef4444'],
            line: {
                color: isDarkMode ? '#1e1e1e' : 'white',
                width: 2
            }
        },
        textfont: {
            family: 'Inter, Arial, sans-serif',
            size: 13,
            color: 'white',
            weight: 'bold'
        },
        hoverinfo: 'label+percent+value',
        shadow: true,
        hovertemplate: '<b>%{label}</b><br>%{percent}<br>Count: %{value}<extra></extra>'
    }];

    const layout = {
        title: {
            text: 'Skills Analysis',
            font: {
                family: 'Inter, Arial, sans-serif',
                size: 18,
                color: isDarkMode ? '#e5e7eb' : '#2d3748'
            }
        },
        height: 400,
        showlegend: true,
        legend: {
            orientation: 'h',
            y: -0.15,
            x: 0.5,
            xanchor: 'center',
            font: {
                family: 'Inter, Arial, sans-serif',
                size: 13,
                color: isDarkMode ? '#e5e7eb' : '#4b5563'
            },
            bgcolor: isDarkMode ? 'rgba(30, 30, 30, 0.8)' : 'rgba(255, 255, 255, 0.8)',
            bordercolor: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
            borderwidth: 1
        },
        paper_bgcolor: isDarkMode ? '#1e1e1e' : 'white',
        plot_bgcolor: isDarkMode ? 'rgba(30, 30, 30, 0.8)' : 'rgba(240, 242, 246, 0.8)',
        font: {
            family: 'Inter, Arial, sans-serif',
            color: isDarkMode ? '#e5e7eb' : '#2d3748'
        }
    };

    Plotly.newPlot('skills-chart', data, layout, {responsive: true});
}
