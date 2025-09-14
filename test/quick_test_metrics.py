#!/usr/bin/env python3
import asyncio
from feynmancraft_adk.tool_metrics import tool_measurement, get_dashboard_data
import time
import random

async def quick_test():
    tools = ['search_particle_mcp', 'validate_physics', 'generate_tikz', 'compile_latex']
    
    print("Generating test tool activity...")
    
    # Generate some quick test data
    for i in range(30):
        tool = random.choice(tools)
        session_id = f'session_{i % 5}'  # 5 different sessions
        trace_id = f'trace_{i}'
        step_id = f'step_{i}'
        
        try:
            with tool_measurement(tool, session_id, trace_id, step_id):
                await asyncio.sleep(random.uniform(0.01, 0.2))  # Fast execution
                # Simulate occasional failures
                if random.random() < 0.15:  # 15% failure rate
                    raise Exception(f'Simulated error in {tool}')
        except Exception:
            pass  # Expected failures
    
    # Get dashboard data
    data = get_dashboard_data()
    
    print(f'\nGenerated dashboard data:')
    print(f'- Active tools: {len(data["tool_metrics"])}')
    print(f'- Total calls: {data["system_stats"]["total_calls"]}')
    print(f'- Success rate: {data["system_stats"]["overall_success_rate"]:.1f}%')
    print(f'- Avg duration: {data["system_stats"]["avg_duration"]:.3f}s')
    
    print('\nTool breakdown:')
    for tool_name, metrics in data['tool_metrics'].items():
        print(f'  {tool_name}: {metrics["total_calls"]} calls, '
              f'{metrics["success_rate"]:.1f}% success, '
              f'{metrics["avg_duration"]:.3f}s avg')

if __name__ == "__main__":
    asyncio.run(quick_test())
    print('\nQuick test completed! Check the dashboard tab in the frontend.')