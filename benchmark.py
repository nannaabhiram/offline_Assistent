#!/usr/bin/env python3
"""
Performance comparison: Enhanced vs Optimized System Control
"""

import time
import sys
import os

# Add backend path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def benchmark_function(func, name, runs=3):
    """Benchmark a function multiple times"""
    times = []
    results = []
    
    for i in range(runs):
        start = time.perf_counter()
        try:
            result = func()
            times.append((time.perf_counter() - start) * 1000)  # Convert to ms
            results.append(str(result)[:100])  # First 100 chars
        except Exception as e:
            times.append(float('inf'))
            results.append(f"Error: {e}")
    
    avg_time = sum(t for t in times if t != float('inf')) / len([t for t in times if t != float('inf')])
    return avg_time, results[0]

def main():
    print("⚡ Performance Comparison: System Control Functions")
    print("=" * 60)
    
    # Test optimized functions
    try:
        from system.optimized_control import system_status, performance_status, quick_volume_control
        
        print("\n🚀 OPTIMIZED VERSION:")
        
        # Test system status
        avg_time, result = benchmark_function(system_status, "System Status")
        print(f"System Status:     {avg_time:6.1f}ms - {result}")
        
        # Test performance status  
        avg_time, result = benchmark_function(performance_status, "Performance Status")
        print(f"Performance:       {avg_time:6.1f}ms - {result}")
        
        # Test volume control
        avg_time, result = benchmark_function(lambda: quick_volume_control("get"), "Volume Control")
        print(f"Volume Control:    {avg_time:6.1f}ms - {result}")
        
        optimized_total = avg_time  # Use last measurement as representative
        
    except ImportError as e:
        print(f"❌ Optimized functions not available: {e}")
        optimized_total = float('inf')
    
    # Test enhanced functions (if available)
    try:
        from system.enhanced_control import get_system_info, get_quick_performance, control_volume
        
        print(f"\n🐌 ENHANCED VERSION (for comparison):")
        
        # Test system info
        avg_time, result = benchmark_function(lambda: str(get_system_info())[:100], "System Info")
        print(f"System Info:       {avg_time:6.1f}ms - {result}")
        
        # Test performance
        avg_time, result = benchmark_function(get_quick_performance, "Performance")
        print(f"Performance:       {avg_time:6.1f}ms - {result}")
        
        # Test volume
        avg_time, result = benchmark_function(lambda: control_volume("get"), "Volume")
        print(f"Volume Control:    {avg_time:6.1f}ms - {result}")
        
        enhanced_total = avg_time
        
    except ImportError:
        print(f"\n🐌 ENHANCED VERSION: Not available (normal - using optimized version)")
        enhanced_total = float('inf')
    
    # Summary
    print(f"\n" + "=" * 60)
    print("📊 PERFORMANCE SUMMARY:")
    
    if optimized_total != float('inf'):
        print(f"✅ Optimized functions: ~{optimized_total:.1f}ms average")
        
        if enhanced_total != float('inf'):
            improvement = enhanced_total / optimized_total
            print(f"🐌 Enhanced functions:  ~{enhanced_total:.1f}ms average")
            print(f"🚀 Performance gain:    {improvement:.1f}x faster!")
        
        if optimized_total < 100:
            print("🎉 EXCELLENT - Ultra-fast response time!")
        elif optimized_total < 500:
            print("✅ GOOD - Fast response time")
        else:
            print("⚠️ SLOW - May need further optimization")
    
    print(f"\n💡 The optimized version uses:")
    print("   • Cached results for expensive operations")
    print("   • Direct Windows API calls where possible") 
    print("   • Minimal subprocess usage with timeouts")
    print("   • Threading locks for thread safety")

if __name__ == "__main__":
    main()