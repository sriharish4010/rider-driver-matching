"""
Simple Spark UI Simulator
Creates a local web server that mimics the Spark UI interface
"""

from flask import Flask, render_template_string, jsonify
import json
from datetime import datetime
import threading
import time
import webbrowser

app = Flask(__name__)

# Mock Spark job data
spark_jobs = [
    {
        "jobId": "0",
        "name": "Load Drivers Dataset", 
        "status": "SUCCEEDED",
        "stages": 1,
        "tasks": 4,
        "duration": "2.3s",
        "startTime": "2024-11-29 15:30:01"
    },
    {
        "jobId": "1", 
        "name": "Load Riders Dataset",
        "status": "SUCCEEDED", 
        "stages": 1,
        "tasks": 4,
        "duration": "1.8s",
        "startTime": "2024-11-29 15:30:04"
    },
    {
        "jobId": "2",
        "name": "Cross Join Riders × Drivers",
        "status": "SUCCEEDED",
        "stages": 2,
        "tasks": 8,
        "duration": "5.7s", 
        "startTime": "2024-11-29 15:30:06"
    },
    {
        "jobId": "3",
        "name": "Calculate Haversine Distances", 
        "status": "SUCCEEDED",
        "stages": 3,
        "tasks": 12,
        "duration": "8.4s",
        "startTime": "2024-11-29 15:30:12"
    },
    {
        "jobId": "4",
        "name": "Compute Match Scores",
        "status": "SUCCEEDED",
        "stages": 2, 
        "tasks": 8,
        "duration": "6.1s",
        "startTime": "2024-11-29 15:30:21"
    },
    {
        "jobId": "5",
        "name": "Rank Top Matches Per Rider",
        "status": "SUCCEEDED",
        "stages": 4,
        "tasks": 16, 
        "duration": "12.3s",
        "startTime": "2024-11-29 15:30:27"
    },
    {
        "jobId": "6",
        "name": "Vehicle Type Analytics",
        "status": "SUCCEEDED",
        "stages": 1,
        "tasks": 4,
        "duration": "3.2s",
        "startTime": "2024-11-29 15:30:40"
    },
    {
        "jobId": "7",
        "name": "Traffic Zone Analytics", 
        "status": "SUCCEEDED",
        "stages": 1,
        "tasks": 4,
        "duration": "2.9s",
        "startTime": "2024-11-29 15:30:43"
    },
    {
        "jobId": "8",
        "name": "Save Results to CSV",
        "status": "SUCCEEDED",
        "stages": 1,
        "tasks": 2,
        "duration": "4.1s",
        "startTime": "2024-11-29 15:30:46"
    }
]

# Mock SQL operations
sql_operations = [
    {
        "id": "0",
        "description": "scan json drivers.json",
        "duration": "2.1s",
        "status": "COMPLETED"
    },
    {
        "id": "1", 
        "description": "scan json riders.json",
        "duration": "1.6s",
        "status": "COMPLETED"
    },
    {
        "id": "2",
        "description": "CartesianProduct",
        "duration": "5.4s", 
        "status": "COMPLETED"
    },
    {
        "id": "3",
        "description": "Project [UDF(haversine)]",
        "duration": "8.1s",
        "status": "COMPLETED"
    },
    {
        "id": "4",
        "description": "Project [match_score calculation]", 
        "duration": "5.8s",
        "status": "COMPLETED"
    },
    {
        "id": "5",
        "description": "Window [rank()]",
        "duration": "11.9s",
        "status": "COMPLETED"
    }
]

# HTML template for Spark UI
spark_ui_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spark UI - Ride-Sharing Matchmaking</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f8f9fa;
        }
        .header {
            background: linear-gradient(135deg, #ff6b35, #f7931e);
            color: white;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header h1 {
            margin: 0;
            font-size: 28px;
            font-weight: 300;
        }
        .subheader {
            font-size: 16px;
            opacity: 0.9;
            margin-top: 5px;
        }
        .nav-tabs {
            background: white;
            border-bottom: 3px solid #ff6b35;
            padding: 0 20px;
            display: flex;
            gap: 30px;
        }
        .tab {
            padding: 15px 0;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            font-weight: 500;
            color: #666;
            transition: all 0.3s;
        }
        .tab:hover, .tab.active {
            color: #ff6b35;
            border-bottom-color: #ff6b35;
        }
        .content {
            padding: 30px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-left: 4px solid #ff6b35;
        }
        .stat-value {
            font-size: 32px;
            font-weight: bold;
            color: #ff6b35;
            margin-bottom: 5px;
        }
        .stat-label {
            color: #666;
            font-size: 14px;
        }
        .jobs-table, .sql-table {
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .table-header {
            background: #ff6b35;
            color: white;
            padding: 15px 20px;
            font-weight: 500;
            font-size: 18px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 12px 20px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        th {
            background: #f8f9fa;
            font-weight: 600;
            color: #333;
        }
        .status {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }
        .succeeded {
            background: #d4edda;
            color: #155724;
        }
        .completed {
            background: #cce7ff;
            color: #004085;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .dag-container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .dag-flow {
            display: flex;
            justify-content: center;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
            margin: 20px 0;
        }
        .dag-node {
            background: #ff6b35;
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            min-width: 120px;
            text-align: center;
            font-size: 14px;
            font-weight: 500;
        }
        .dag-arrow {
            font-size: 24px;
            color: #ff6b35;
        }
        .job-assignment-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }
        .assignment-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-left: 4px solid #ff6b35;
        }
        .assignment-card h3 {
            margin: 0 0 15px 0;
            color: #ff6b35;
        }
        .executor {
            background: #e8f4fd;
            color: #1a73e8;
            padding: 8px 12px;
            border-radius: 4px;
            margin: 5px 0;
            font-weight: 500;
        }
        .executor-driver {
            background: #fff3cd;
            color: #856404;
            padding: 8px 12px;
            border-radius: 4px;
            margin: 5px 0;
            font-weight: 500;
        }
        .parallel-info .parallel-level {
            background: #f8f9fa;
            padding: 8px 12px;
            border-radius: 4px;
            margin: 5px 0;
            border-left: 3px solid #ff6b35;
        }
        .stage-flow-container {
            margin: 30px 0;
        }
        .stage-section {
            margin: 25px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 5px solid #ff6b35;
        }
        .stage-header {
            font-weight: 600;
            font-size: 16px;
            color: #ff6b35;
            margin-bottom: 15px;
            text-align: center;
        }
        .job-node {
            background: linear-gradient(135deg, #ff6b35, #f7931e);
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            min-width: 160px;
            text-align: center;
            font-size: 13px;
            font-weight: 500;
            box-shadow: 0 4px 8px rgba(255, 107, 53, 0.3);
            transition: transform 0.3s;
            cursor: pointer;
        }
        .job-node:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(255, 107, 53, 0.4);
        }
        .job-node.wide-node {
            min-width: 200px;
        }
        .task-distribution {
            font-size: 11px;
            background: rgba(255,255,255,0.2);
            padding: 3px 6px;
            border-radius: 3px;
            margin-top: 5px;
            display: inline-block;
        }
        .shuffle-indicator, .udf-indicator, .calc-indicator, .window-indicator, .output-indicator {
            font-size: 11px;
            background: rgba(255,255,255,0.2);
            padding: 3px 6px;
            border-radius: 3px;
            margin-top: 5px;
            display: block;
        }
        .timeline-container {
            margin: 30px 0;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .timeline {
            height: 60px;
            background: #f1f3f4;
            border-radius: 4px;
            position: relative;
            margin: 20px 0;
            border: 1px solid #dadce0;
        }
        .timeline-item {
            position: absolute;
            top: 10px;
            height: 40px;
            background: linear-gradient(135deg, #ff6b35, #f7931e);
            color: white;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 12px;
            box-shadow: 0 2px 4px rgba(255, 107, 53, 0.3);
            cursor: pointer;
            transition: all 0.3s;
        }
        .timeline-item:hover {
            transform: scale(1.05);
            z-index: 10;
        }
        .timeline-final {
            background: linear-gradient(135deg, #34a853, #2d8e3f) !important;
        }
        .timeline-labels {
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            color: #666;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Apache Spark™ UI</h1>
        <div class="subheader">Ride-Sharing Matchmaking System - Application ID: app-20241129153000</div>
    </div>

    <div class="nav-tabs">
        <div class="tab active" onclick="showTab('jobs')">Jobs</div>
        <div class="tab" onclick="showTab('stages')">Stages</div>
        <div class="tab" onclick="showTab('sql')">SQL / DataFrame</div>
        <div class="tab" onclick="showTab('dag')">DAG Visualization</div>
        <div class="tab" onclick="showTab('environment')">Environment</div>
    </div>

    <div class="content">
        <!-- Jobs Tab -->
        <div id="jobs" class="tab-content active">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">9</div>
                    <div class="stat-label">Total Jobs</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">40</div>
                    <div class="stat-label">Total Stages</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">76</div>
                    <div class="stat-label">Total Tasks</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">46.2s</div>
                    <div class="stat-label">Total Duration</div>
                </div>
            </div>

            <div class="jobs-table">
                <div class="table-header">📊 Spark Jobs - Ride Matching Pipeline</div>
                <table>
                    <thead>
                        <tr>
                            <th>Job ID</th>
                            <th>Description</th>
                            <th>Status</th>
                            <th>Stages</th>
                            <th>Tasks</th>
                            <th>Duration</th>
                            <th>Started</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for job in jobs %}
                        <tr>
                            <td>{{ job.jobId }}</td>
                            <td>{{ job.name }}</td>
                            <td><span class="status succeeded">{{ job.status }}</span></td>
                            <td>{{ job.stages }}</td>
                            <td>{{ job.tasks }}</td>
                            <td>{{ job.duration }}</td>
                            <td>{{ job.startTime }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- SQL Tab -->
        <div id="sql" class="tab-content">
            <div class="sql-table">
                <div class="table-header">🔍 SQL / DataFrame Operations</div>
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Description</th>
                            <th>Duration</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for sql in sql_ops %}
                        <tr>
                            <td>{{ sql.id }}</td>
                            <td>{{ sql.description }}</td>
                            <td>{{ sql.duration }}</td>
                            <td><span class="status completed">{{ sql.status }}</span></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- DAG Tab -->
        <div id="dag" class="tab-content">
            <div class="dag-container">
                <h2>🔄 Job Assignment & Execution DAG</h2>
                <p>Directed Acyclic Graph showing job distribution, task assignment, and execution flow</p>
                
                <!-- Job Assignment Overview -->
                <div class="job-assignment-grid">
                    <div class="assignment-card">
                        <h3>📊 Job Assignment</h3>
                        <div class="executor-info">
                            <div class="executor">Executor 0: 38 tasks</div>
                            <div class="executor">Executor 1: 38 tasks</div>
                            <div class="executor-driver">Driver: 4 coordination tasks</div>
                        </div>
                    </div>
                    <div class="assignment-card">
                        <h3>⚡ Parallelization</h3>
                        <div class="parallel-info">
                            <div class="parallel-level">Max Parallel Tasks: 8</div>
                            <div class="parallel-level">Shuffle Partitions: 8</div>
                            <div class="parallel-level">CPU Cores Used: 2</div>
                        </div>
                    </div>
                </div>

                <!-- Stage-by-Stage Job Flow -->
                <div class="stage-flow-container">
                    <h3>📈 Stage-by-Stage Job Execution Flow</h3>
                    
                    <!-- Stage 0-1: Data Loading -->
                    <div class="stage-section">
                        <div class="stage-header">Stage 0-1: Data Ingestion (Jobs 0-1)</div>
                        <div class="dag-flow">
                            <div class="job-node" data-job="0">
                                Job 0<br/>
                                <strong>Load Drivers</strong><br/>
                                <small>4 tasks | 2.3s</small><br/>
                                <span class="task-distribution">Tasks: E0[2] E1[2]</span>
                            </div>
                            <div class="dag-arrow">||</div>
                            <div class="job-node" data-job="1">
                                Job 1<br/>
                                <strong>Load Riders</strong><br/>
                                <small>4 tasks | 1.8s</small><br/>
                                <span class="task-distribution">Tasks: E0[2] E1[2]</span>
                            </div>
                        </div>
                    </div>

                    <!-- Stage 2: Cross Join -->
                    <div class="stage-section">
                        <div class="stage-header">Stage 2: Cartesian Product (Job 2)</div>
                        <div class="dag-flow">
                            <div class="job-node wide-node" data-job="2">
                                Job 2<br/>
                                <strong>Cross Join Riders × Drivers</strong><br/>
                                <small>8 tasks | 5.7s</small><br/>
                                <span class="task-distribution">Tasks: E0[4] E1[4]</span><br/>
                                <div class="shuffle-indicator">🔄 Shuffle: 188 → 6,900 rows</div>
                            </div>
                        </div>
                    </div>

                    <!-- Stage 3-4: Distance & Filtering -->
                    <div class="stage-section">
                        <div class="stage-header">Stage 3-4: Distance Calculation (Job 3)</div>
                        <div class="dag-flow">
                            <div class="job-node wide-node" data-job="3">
                                Job 3<br/>
                                <strong>Calculate Haversine Distances</strong><br/>
                                <small>12 tasks | 8.4s</small><br/>
                                <span class="task-distribution">Tasks: E0[6] E1[6]</span><br/>
                                <div class="udf-indicator">🔧 UDF: Haversine formula</div>
                            </div>
                        </div>
                    </div>

                    <!-- Stage 5: Scoring -->
                    <div class="stage-section">
                        <div class="stage-header">Stage 5: Match Scoring (Job 4)</div>
                        <div class="dag-flow">
                            <div class="job-node" data-job="4">
                                Job 4<br/>
                                <strong>Compute Match Scores</strong><br/>
                                <small>8 tasks | 6.1s</small><br/>
                                <span class="task-distribution">Tasks: E0[4] E1[4]</span><br/>
                                <div class="calc-indicator">🧮 Multi-factor scoring</div>
                            </div>
                        </div>
                    </div>

                    <!-- Stage 6-9: Window & Analytics -->
                    <div class="stage-section">
                        <div class="stage-header">Stage 6-9: Ranking & Analytics (Jobs 5-8)</div>
                        <div class="dag-flow">
                            <div class="job-node" data-job="5">
                                Job 5<br/>
                                <strong>Window Ranking</strong><br/>
                                <small>16 tasks | 12.3s</small><br/>
                                <span class="task-distribution">Tasks: E0[8] E1[8]</span><br/>
                                <div class="window-indicator">🪟 Window: RANK()</div>
                            </div>
                            <div class="dag-arrow">→</div>
                            <div class="job-node" data-job="6">
                                Job 6<br/>
                                <strong>Vehicle Analytics</strong><br/>
                                <small>4 tasks | 3.2s</small><br/>
                                <span class="task-distribution">Tasks: E0[2] E1[2]</span>
                            </div>
                        </div>
                        
                        <div class="dag-flow">
                            <div class="job-node" data-job="7">
                                Job 7<br/>
                                <strong>Traffic Zone Analytics</strong><br/>
                                <small>4 tasks | 2.9s</small><br/>
                                <span class="task-distribution">Tasks: E0[2] E1[2]</span>
                            </div>
                            <div class="dag-arrow">→</div>
                            <div class="job-node" data-job="8">
                                Job 8<br/>
                                <strong>Save to CSV</strong><br/>
                                <small>2 tasks | 4.1s</small><br/>
                                <span class="task-distribution">Tasks: E0[1] E1[1]</span><br/>
                                <div class="output-indicator">💾 Output: spark_output/</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Task Timeline Visualization -->
                <div class="timeline-container">
                    <h3>⏱️ Job Execution Timeline</h3>
                    <div class="timeline">
                        <div class="timeline-item" style="left: 0%; width: 5%;" data-job="0">J0</div>
                        <div class="timeline-item" style="left: 6%; width: 4%;" data-job="1">J1</div>
                        <div class="timeline-item" style="left: 11%; width: 12%;" data-job="2">J2</div>
                        <div class="timeline-item" style="left: 24%; width: 18%;" data-job="3">J3</div>
                        <div class="timeline-item" style="left: 43%; width: 13%;" data-job="4">J4</div>
                        <div class="timeline-item" style="left: 57%; width: 27%;" data-job="5">J5</div>
                        <div class="timeline-item" style="left: 85%; width: 7%;" data-job="6">J6</div>
                        <div class="timeline-item" style="left: 93%; width: 6%;" data-job="7">J7</div>
                        <div class="timeline-item timeline-final" style="left: 100%; width: 9%;" data-job="8">J8</div>
                    </div>
                    <div class="timeline-labels">
                        <span>0s</span>
                        <span>10s</span>
                        <span>20s</span>
                        <span>30s</span>
                        <span>40s</span>
                        <span>46.2s</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Stages Tab -->
        <div id="stages" class="tab-content">
            <div class="jobs-table">
                <div class="table-header">📈 Stage Details</div>
                <table>
                    <thead>
                        <tr>
                            <th>Stage ID</th>
                            <th>Description</th>
                            <th>Tasks</th>
                            <th>Duration</th>
                            <th>Input Size</th>
                            <th>Output Size</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td>0</td><td>json at drivers.json</td><td>4</td><td>2.1s</td><td>15.2 KB</td><td>138 rows</td></tr>
                        <tr><td>1</td><td>json at riders.json</td><td>4</td><td>1.6s</td><td>8.1 KB</td><td>50 rows</td></tr>
                        <tr><td>2</td><td>CartesianRDD</td><td>8</td><td>5.4s</td><td>188 rows</td><td>6,900 rows</td></tr>
                        <tr><td>3</td><td>Project [haversine UDF]</td><td>12</td><td>8.1s</td><td>6,900 rows</td><td>6,900 rows</td></tr>
                        <tr><td>4</td><td>Filter [distance <= 50km]</td><td>8</td><td>3.2s</td><td>6,900 rows</td><td>4,234 rows</td></tr>
                        <tr><td>5</td><td>Project [score calculation]</td><td>8</td><td>5.8s</td><td>4,234 rows</td><td>4,234 rows</td></tr>
                        <tr><td>6</td><td>Window [row_number()]</td><td>16</td><td>11.9s</td><td>4,234 rows</td><td>4,234 rows</td></tr>
                        <tr><td>7</td><td>Filter [rank <= 3]</td><td>4</td><td>2.3s</td><td>4,234 rows</td><td>150 rows</td></tr>
                        <tr><td>8</td><td>csv at spark_output</td><td>2</td><td>4.1s</td><td>150 rows</td><td>150 rows</td></tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Environment Tab -->
        <div id="environment" class="tab-content">
            <div class="jobs-table">
                <div class="table-header">🔧 Spark Configuration</div>
                <table>
                    <thead>
                        <tr>
                            <th>Property</th>
                            <th>Value</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td>spark.app.name</td><td>RideMatchingSystem</td></tr>
                        <tr><td>spark.driver.memory</td><td>1g</td></tr>
                        <tr><td>spark.executor.memory</td><td>1g</td></tr>
                        <tr><td>spark.sql.shuffle.partitions</td><td>8</td></tr>
                        <tr><td>spark.ui.port</td><td>4040</td></tr>
                        <tr><td>spark.master</td><td>local[*]</td></tr>
                        <tr><td>spark.sql.adaptive.enabled</td><td>true</td></tr>
                        <tr><td>spark.sql.adaptive.coalescePartitions.enabled</td><td>true</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        function showTab(tabName) {
            // Hide all tab contents
            const contents = document.querySelectorAll('.tab-content');
            contents.forEach(content => content.classList.remove('active'));
            
            // Remove active class from all tabs
            const tabs = document.querySelectorAll('.tab');
            tabs.forEach(tab => tab.classList.remove('active'));
            
            // Show selected tab content
            document.getElementById(tabName).classList.add('active');
            
            // Add active class to clicked tab
            event.target.classList.add('active');
        }

        // Job details for tooltips
        const jobDetails = {
            "0": {
                name: "Load Drivers Dataset",
                tasks: "4 tasks across 2 executors",
                details: "JSON scan of drivers.json - 138 driver records loaded",
                time: "2.3s execution time"
            },
            "1": {
                name: "Load Riders Dataset", 
                tasks: "4 tasks across 2 executors",
                details: "JSON scan of riders.json - 50 rider requests loaded",
                time: "1.8s execution time"
            },
            "2": {
                name: "Cross Join Riders × Drivers",
                tasks: "8 tasks with data shuffling",
                details: "Cartesian product: 188 → 6,900 combinations",
                time: "5.7s with network shuffle"
            },
            "3": {
                name: "Calculate Haversine Distances",
                tasks: "12 tasks with UDF execution", 
                details: "Geospatial distance calculation using custom UDF",
                time: "8.4s - most compute intensive stage"
            },
            "4": {
                name: "Compute Match Scores",
                tasks: "8 tasks with complex expressions",
                details: "Multi-factor scoring: distance + vehicle + rating + weights",
                time: "6.1s computation time"
            },
            "5": {
                name: "Rank Top Matches Per Rider",
                tasks: "16 tasks with window functions",
                details: "Window partitioning by rider_id with RANK() function",
                time: "12.3s - largest stage"
            },
            "6": {
                name: "Vehicle Type Analytics",
                tasks: "4 tasks for aggregation",
                details: "GROUP BY vehicle_type with COUNT aggregation",
                time: "3.2s group by operation"
            },
            "7": {
                name: "Traffic Zone Analytics",
                tasks: "4 tasks for zone analysis", 
                details: "GROUP BY traffic_zone with COUNT aggregation",
                time: "2.9s aggregation time"
            },
            "8": {
                name: "Save Results to CSV",
                tasks: "2 tasks for file output",
                details: "Coalesce to single partition and write CSV with headers",
                time: "4.1s file I/O operation"
            }
        };

        // Add hover tooltips to job nodes
        document.addEventListener('DOMContentLoaded', function() {
            const jobNodes = document.querySelectorAll('[data-job]');
            
            jobNodes.forEach(node => {
                node.addEventListener('mouseenter', function(e) {
                    const jobId = this.getAttribute('data-job');
                    const job = jobDetails[jobId];
                    
                    if (job) {
                        const tooltip = document.createElement('div');
                        tooltip.id = 'job-tooltip';
                        tooltip.innerHTML = `
                            <div style="background: rgba(0,0,0,0.9); color: white; padding: 12px; border-radius: 6px; font-size: 12px; max-width: 250px; position: fixed; z-index: 1000; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
                                <div style="font-weight: bold; margin-bottom: 8px; color: #ff6b35;">Job ${jobId}: ${job.name}</div>
                                <div style="margin: 4px 0;">📊 ${job.tasks}</div>
                                <div style="margin: 4px 0;">🔧 ${job.details}</div>
                                <div style="margin: 4px 0;">⏱️ ${job.time}</div>
                            </div>
                        `;
                        
                        tooltip.style.left = (e.pageX + 10) + 'px';
                        tooltip.style.top = (e.pageY - 10) + 'px';
                        
                        document.body.appendChild(tooltip);
                    }
                });
                
                node.addEventListener('mouseleave', function() {
                    const tooltip = document.getElementById('job-tooltip');
                    if (tooltip) {
                        tooltip.remove();
                    }
                });
            });
        });
    </script>
</body>
</html>
'''

@app.route('/')
def spark_ui():
    """Main Spark UI interface"""
    return render_template_string(spark_ui_template, jobs=spark_jobs, sql_ops=sql_operations)

@app.route('/api/jobs')
def api_jobs():
    """API endpoint for job data"""
    return jsonify(spark_jobs)

@app.route('/api/sql')  
def api_sql():
    """API endpoint for SQL operations"""
    return jsonify(sql_operations)

def open_browser():
    """Open browser after a short delay"""
    time.sleep(1.5)
    webbrowser.open('http://localhost:4040')

def main():
    print("\n" + "="*70)
    print("🚀 SPARK UI SIMULATOR - RIDE-SHARING MATCHMAKING")  
    print("="*70)
    print("\n✅ Starting Spark UI simulator...")
    print("🌐 Spark UI will be available at: http://localhost:4040")
    print("📊 Simulates real Spark UI with ride-matching jobs")
    print("\n💡 Features included:")
    print("   • Jobs tab - 9 completed Spark jobs")
    print("   • Stages tab - Detailed execution stages") 
    print("   • SQL tab - DataFrame operations")
    print("   • DAG tab - Query execution visualization")
    print("   • Environment tab - Spark configuration")
    print("\n🚀 Opening browser automatically...")
    print("🛑 Press Ctrl+C to stop\n")
    
    # Start browser in background
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start Flask server
    try:
        app.run(host='0.0.0.0', port=4040, debug=False)
    except KeyboardInterrupt:
        print("\n\n🛑 Spark UI simulator stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()