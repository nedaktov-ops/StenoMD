#!/usr/bin/env python3
"""
StenoMD RAM Optimization Utilities

Provides memory monitoring and batch size management for 8GB RAM systems.
"""
import os
import sys
import gc
from pathlib import Path
from typing import Optional

def get_available_ram() -> float:
    """Get available RAM in GB (approximate)."""
    try:
        if sys.platform == 'win32':
            return _get_windows_ram()
        else:
            return _get_linux_ram()
    except Exception:
        return 8.0

def _get_linux_ram() -> float:
    """Get available RAM on Linux from /proc/meminfo."""
    try:
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                if line.startswith('MemAvailable:'):
                    kb = int(line.split()[1])
                    return kb / (1024 * 1024)
    except Exception:
        pass
    
    try:
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                if line.startswith('MemTotal:'):
                    kb = int(line.split()[1])
                    return kb / (1024 * 1024) * 0.9
    except Exception:
        pass
    
    return 8.0

def _get_windows_ram() -> float:
    """Get available RAM on Windows."""
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        ctypes.c_ulong()
        kernel32.GetPerformanceInfo
        
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ('dwLength', ctypes.c_ulong),
                ('dwMemoryLoad', ctypes.c_ulong),
                ('ullTotalPhys', ctypes.c_ulonglong),
                ('ullAvailPhys', ctypes.c_ulonglong),
                ('ullTotalPageFile', ctypes.c_ulonglong),
                ('ullAvailPageFile', ctypes.c_ulonglong),
                ('ullTotalVirtual', ctypes.c_ulonglong),
                ('ullAvailVirtual', ctypes.c_ulonglong),
            ]
        
        stat = MEMORYSTATUSEX()
        stat.dwLength = ctypes.sizeof(stat)
        kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
        
        return stat.ullAvailPhys / (1024 * 1024 * 1024)
    except Exception:
        return 8.0

def suggest_batch_size() -> int:
    """Suggest batch size based on available RAM."""
    ram = get_available_ram()
    
    if ram >= 16:
        return 50
    elif ram >= 12:
        return 30
    elif ram >= 8:
        return 15
    elif ram >= 4:
        return 5
    else:
        return 1

def suggest_model() -> str:
    """Suggest best model based on available RAM."""
    ram = get_available_ram()
    
    if ram >= 16:
        return 'qwen2.5-coder:7b'
    elif ram >= 12:
        return 'qwen2.5-coder:3b'
    elif ram >= 8:
        return 'phi3:3.5b'
    else:
        return 'phi3:3.5b'

def check_memory_threshold(threshold_gb: float = 1.0) -> bool:
    """Check if available memory is above threshold."""
    available = get_available_ram()
    return available >= threshold_gb

def force_gc():
    """Force garbage collection to free memory."""
    gc.collect()
    if sys.platform != 'win32':
        try:
            os.system('sync')
        except Exception:
            pass

def memory_report() -> dict:
    """Get memory report."""
    return {
        'available_gb': get_available_ram(),
        'suggested_model': suggest_model(),
        'suggested_batch': suggest_batch_size(),
        'platform': sys.platform,
    }

if __name__ == "__main__":
    report = memory_report()
    print(f"Available RAM: {report['available_gb']:.1f} GB")
    print(f"Suggested Model: {report['suggested_model']}")
    print(f"Suggested Batch: {report['suggested_batch']}")
    print(f"Platform: {report['platform']}")