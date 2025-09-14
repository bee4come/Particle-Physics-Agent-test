#!/usr/bin/env python3
"""
Test script for tool metrics and dashboard
Generates sample tool activity for P1-14.2 demonstration
"""

import asyncio
import random
import time
import logging
import sys
from pathlib import Path

# Add the project root to Python path (one level up since we're in test/)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from feynmancraft_adk.tool_metrics import tool_measurement, get_dashboard_data

logging.basicConfig(level=logging.INFO)

# Sample tools with different characteristics
SAMPLE_TOOLS = [
    # MCP Tools
    ("search_particle_mcp", "mcp", (0.1, 0.5), 0.95),
    ("get_particle_properties_mcp", "mcp", (0.2, 0.8), 0.92),
    ("validate_quantum_numbers_mcp", "mcp", (0.3, 1.2), 0.88),
    
    # Search Tools  
    ("search_physics_rules", "search", (0.05, 0.3), 0.98),
    ("kb_retrieval", "search", (0.1, 0.6), 0.96),
    
    # Validation Tools
    ("validate_physics_process", "validation", (0.2, 1.0), 0.90),
    ("check_conservation_laws", "validation", (0.1, 0.7), 0.93),
    
    # Generation Tools
    ("generate_tikz_diagram", "generation", (1.0, 3.0), 0.85),
    ("create_feynman_code", "generation", (0.8, 2.5), 0.87),
    
    # Compilation Tools
    ("compile_latex", "compilation", (2.0, 5.0), 0.80),
    ("validate_tikz_syntax", "compilation", (0.5, 1.5), 0.92),
]

async def simulate_tool_activity(duration_minutes: int = 5):
    """Simulate tool activity for dashboard testing"""
    print(f"Simulating tool activity for {duration_minutes} minutes...")
    
    end_time = time.time() + (duration_minutes * 60)
    session_count = 0
    
    while time.time() < end_time:
        # Create a session with multiple tool calls
        session_count += 1
        session_id = f"test_session_{session_count}"
        trace_id = f"trace_{session_count}_{int(time.time())}"
        
        # Simulate a workflow with 3-8 tool calls
        workflow_size = random.randint(3, 8)
        
        for step in range(workflow_size):
            # Select a random tool
            tool_name, category, (min_dur, max_dur), success_rate = random.choice(SAMPLE_TOOLS)
            step_id = f"step_{step + 1}"
            
            # Simulate tool execution
            actual_duration = random.uniform(min_dur, max_dur)
            success = random.random() < success_rate
            
            params = {
                "query": f"test_query_{step}",
                "parameter": f"value_{step}",
                "workflow_id": session_id
            }
            
            with tool_measurement(tool_name, session_id, trace_id, step_id, params) as call_id:
                # Simulate work
                await asyncio.sleep(actual_duration)
                
                # Occasionally fail
                if not success:
                    raise Exception(f"Simulated {category} error in {tool_name}")
        
        print(f"Completed workflow {session_count} with {workflow_size} tools")
        
        # Wait between workflows
        await asyncio.sleep(random.uniform(0.5, 2.0))
    
    print("Simulation completed!")

async def generate_sample_data():
    """Generate rich sample data for dashboard testing"""
    print("Generating sample data...")
    
    # Simulate different time patterns
    tasks = []
    
    # Heavy usage burst
    tasks.append(simulate_burst_activity(30, 0.2))  # 30 calls in 0.2 minutes
    
    # Steady background activity  
    tasks.append(simulate_steady_activity(60, 2.0))  # 60 calls over 2 minutes
    
    # Error burst
    tasks.append(simulate_error_burst(10, 0.5))  # 10 failing calls in 0.5 minutes
    
    await asyncio.gather(*tasks)
    print("Sample data generation completed!")

async def simulate_burst_activity(call_count: int, duration_minutes: float):
    """Simulate burst of high activity"""
    interval = (duration_minutes * 60) / call_count
    
    for i in range(call_count):
        tool_name, _, (min_dur, max_dur), success_rate = random.choice(SAMPLE_TOOLS)
        session_id = f"burst_session_{i}"
        trace_id = f"burst_trace_{i}"
        
        with tool_measurement(tool_name, session_id, trace_id, f"burst_{i}"):
            await asyncio.sleep(random.uniform(min_dur * 0.1, max_dur * 0.1))  # Faster execution
        
        await asyncio.sleep(interval)

async def simulate_steady_activity(call_count: int, duration_minutes: float):
    """Simulate steady background activity"""
    interval = (duration_minutes * 60) / call_count
    
    for i in range(call_count):
        tool_name, _, (min_dur, max_dur), success_rate = random.choice(SAMPLE_TOOLS[:6])  # Use faster tools
        session_id = f"steady_session_{i}"
        trace_id = f"steady_trace_{i}"
        
        with tool_measurement(tool_name, session_id, trace_id, f"steady_{i}"):
            await asyncio.sleep(random.uniform(min_dur, max_dur))
        
        await asyncio.sleep(interval)

async def simulate_error_burst(call_count: int, duration_minutes: float):
    """Simulate burst of errors"""
    interval = (duration_minutes * 60) / call_count
    
    for i in range(call_count):
        tool_name, _, (min_dur, max_dur), _ = random.choice(SAMPLE_TOOLS[-4:])  # Use slower tools
        session_id = f"error_session_{i}"
        trace_id = f"error_trace_{i}"
        
        try:
            with tool_measurement(tool_name, session_id, trace_id, f"error_{i}"):
                await asyncio.sleep(random.uniform(min_dur, max_dur))
                # Force an error
                raise Exception(f"Simulated error in {tool_name}")
        except:
            pass  # Expected failure
        
        await asyncio.sleep(interval)

def print_dashboard_summary():
    """Print summary of dashboard data"""
    data = get_dashboard_data()
    
    print("\n=== Dashboard Data Summary ===")
    print(f"System Stats: {data['system_stats']}")
    print(f"Active Tools: {len(data['tool_metrics'])}")
    print(f"Activity Periods: {len(data['activity_heatmap'])}")
    
    print("\nTool Performance:")
    for tool_name, metrics in data['tool_metrics'].items():
        print(f"  {tool_name}: {metrics['total_calls']} calls, "
              f"{metrics['success_rate']:.1f}% success, "
              f"{metrics['avg_duration']:.2f}s avg")

if __name__ == "__main__":
    print("Starting tool metrics testing...")
    
    # Run simulation
    asyncio.run(generate_sample_data())
    
    # Print results
    print_dashboard_summary()
    
    print("\nTool metrics testing completed!")
    print("Check the dashboard at: http://localhost:5176/app/ -> Dashboard tab")
    print("API endpoint: http://localhost:8001/dashboard-data")