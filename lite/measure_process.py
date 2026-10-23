"""External process-tree measurements with native CPU times and cycles.

Fresh psutil objects provide a separate wrapper cross-check. Percent uses actual
monotonic elapsed time and logical CPU count; raw cumulative values are retained.
"""
import ctypes
from ctypes import wintypes as w
import os
import time
import psutil

kernel = ctypes.WinDLL('kernel32', use_last_error=True)
kernel.OpenProcess.argtypes = [w.DWORD, w.BOOL, w.DWORD]
kernel.OpenProcess.restype = w.HANDLE
kernel.CloseHandle.argtypes = [w.HANDLE]
kernel.GetProcessTimes.argtypes = [w.HANDLE, *([ctypes.POINTER(w.FILETIME)] * 4)]
kernel.GetProcessTimes.restype = w.BOOL
kernel.QueryProcessCycleTime.argtypes = [w.HANDLE, ctypes.POINTER(ctypes.c_ulonglong)]
kernel.QueryProcessCycleTime.restype = w.BOOL


def filetime_seconds(value):
    return ((value.dwHighDateTime << 32) | value.dwLowDateTime) / 10_000_000


def sample(pid):
    root = psutil.Process(pid)
    values = dict(monotonic=time.perf_counter(), native_cpu_s=0, psutil_cpu_s=0,
                  cycles=0, private_bytes=0, working_set=0, threads=0, handles=0,
                  read_bytes=0, write_bytes=0, processes=0, connections=0,
                  thread_cpu_s=0, voluntary_context_switches=0, involuntary_context_switches=0,
                  logical_cpus=os.cpu_count(), system_cpu_pct=psutil.cpu_percent())
    for proc in [root, *root.children(recursive=True)]:
        handle = None
        try:
            handle = kernel.OpenProcess(0x1000, False, proc.pid)
            if not handle:
                raise ctypes.WinError(ctypes.get_last_error())
            creation, exit_time, system, user = (w.FILETIME() for _ in range(4))
            if not kernel.GetProcessTimes(handle, ctypes.byref(creation), ctypes.byref(exit_time),
                                          ctypes.byref(system), ctypes.byref(user)):
                raise ctypes.WinError(ctypes.get_last_error())
            cycles = ctypes.c_ulonglong()
            if not kernel.QueryProcessCycleTime(handle, ctypes.byref(cycles)):
                raise ctypes.WinError(ctypes.get_last_error())
            values['native_cpu_s'] += filetime_seconds(system) + filetime_seconds(user)
            values['psutil_cpu_s'] += sum(proc.cpu_times()[:2])
            values['thread_cpu_s'] += sum(t.user_time+t.system_time for t in proc.threads())
            switches = proc.num_ctx_switches()
            values['voluntary_context_switches'] += switches.voluntary
            values['involuntary_context_switches'] += switches.involuntary
            values['cycles'] += cycles.value
            memory = proc.memory_info()
            values['private_bytes'] += memory.private
            values['working_set'] += memory.rss
            values['threads'] += proc.num_threads()
            values['handles'] += proc.num_handles()
            io = proc.io_counters()
            values['read_bytes'] += io.read_bytes
            values['write_bytes'] += io.write_bytes
            values['processes'] += 1
            values['connections'] += len(proc.net_connections())
        except psutil.NoSuchProcess:
            continue
        finally:
            if handle:
                kernel.CloseHandle(handle)
    return values


def delta(current, previous):
    dt = current['monotonic'] - previous['monotonic']
    return {'interval_s': dt,
            'native_cpu_machine_pct': (current['native_cpu_s']-previous['native_cpu_s'])/dt*100/current['logical_cpus'],
            'psutil_cpu_machine_pct': (current['psutil_cpu_s']-previous['psutil_cpu_s'])/dt*100/current['logical_cpus'],
            'cycles_per_s': (current['cycles']-previous['cycles'])/dt}
