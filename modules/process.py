#!/usr/bin/env python3
"""Process management module"""

import os
import re
import sys
import struct

class ProcessManager:
    """Manage target processes for memory manipulation"""
    
    def __init__(self):
        self.attached_processes = {}
        
    def get_all_processes(self):
        """Get list of all running processes"""
        processes = []
        
        for pid_dir in os.listdir('/proc'):
            if not pid_dir.isdigit():
                continue
            
            pid = int(pid_dir)
            try:
                with open(f'/proc/{pid}/cmdline', 'rb') as f:
                    cmdline = f.read().decode('utf-8', errors='replace').replace('\x00', ' ')
                
                with open(f'/proc/{pid}/status', 'r') as f:
                    status = f.read()
                
                name_match = re.search(r'Name:\s+(.+)', status)
                name = name_match.group(1).strip() if name_match else "unknown"
                
                # Get process state
                state_match = re.search(r'State:\s+(.+)', status)
                state = state_match.group(1).strip() if state_match else "unknown"
                
                # Check if we can access memory
                mem_path = f'/proc/{pid}/mem'
                accessible = os.access(mem_path, os.R_OK | os.W_OK) if os.path.exists(mem_path) else False
                
                uids = re.search(r'Uid:\s+(\d+)', status)
                uid = uids.group(1) if uids else "?"
                
                processes.append({
                    'pid': pid,
                    'name': name,
                    'cmdline': cmdline.strip(),
                    'state': state,
                    'uid': uid,
                    'accessible': accessible
                })
                
            except (IOError, OSError, PermissionError):
                continue
        
        # Sort by PID
        processes.sort(key=lambda x: x['pid'])
        return processes
    
    def find_pid_by_name(self, name):
        """Find PID by process name"""
        for proc in self.get_all_processes():
            if name.lower() in proc['name'].lower():
                return proc['pid']
        return None
    
    def attach(self, pid):
        """Attach to a process for memory access"""
        mem_path = f'/proc/{pid}/mem'
        maps_path = f'/proc/{pid}/maps'
        
        if not os.path.exists(mem_path) or not os.path.exists(maps_path):
            print(f"[✗] Process {pid} does not exist or no access")
            return False
        
        try:
            # Open handle to process memory
            mem_fd = os.open(mem_path, os.O_RDWR)
            self.attached_processes[pid] = {
                'mem_fd': mem_fd,
                'maps_path': maps_path,
                'mem_path': mem_path
            }
            return True
        except PermissionError:
            print(f"[✗] Permission denied. Run as root: sudo python3 memory_forge.py")
            return False
        except Exception as e:
            print(f"[✗] Failed to attach: {e}")
            return False
    
    def detach(self, pid):
        """Detach from a process"""
        if pid in self.attached_processes:
            try:
                os.close(self.attached_processes[pid]['mem_fd'])
            except:
                pass
            del self.attached_processes[pid]
            return True
        return False
    
    def get_process_info(self, pid):
        """Get detailed info about a process"""
        info = {'pid': pid}
        
        try:
            with open(f'/proc/{pid}/status', 'r') as f:
                content = f.read()
                
            for line in content.split('\n'):
                if ':' in line:
                    key, val = line.split(':', 1)
                    info[key.strip().lower()] = val.strip()
                    
            with open(f'/proc/{pid}/cmdline', 'rb') as f:
                cmdline = f.read().decode('utf-8', errors='replace').replace('\x00', ' ')
                info['cmdline'] = cmdline.strip()
                
        except:
            info['name'] = 'unknown'
            
        return info
    
    def get_memory_regions(self, pid):
        """Get readable/writable memory regions"""
        regions = []
        
        if pid not in self.attached_processes:
            return regions
        
        maps_path = self.attached_processes[pid]['maps_path']
        
        try:
            with open(maps_path, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) < 5:
                        continue
                    
                    addr_range, perms, offset, dev, inode = parts[:5]
                    pathname = parts[-1] if len(parts) > 5 else ''
                    
                    # Parse address range
                    start_str, end_str = addr_range.split('-')
                    start = int(start_str, 16)
                    end = int(end_str, 16)
                    size = end - start
                    
                    # Only include writable regions for editing
                    is_writable = 'w' in perms
                    is_readable = 'r' in perms
                    
                    regions.append({
                        'start': start,
                        'end': end,
                        'size': size,
                        'perms': perms,
                        'offset': offset,
                        'inode': inode,
                        'pathname': pathname,
                        'writable': is_writable,
                        'readable': is_readable
                    })
        except:
            pass
            
        return regions
