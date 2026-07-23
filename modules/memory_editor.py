#!/usr/bin/env python3
"""Memory editor module for writing values to process memory"""

import os
import struct

class MemoryEditor:
    """Edit process memory values"""
    
    def __init__(self, proc_manager, pid):
        self.proc_manager = proc_manager
        self.pid = pid
        self.mem_fd = None
        
        if pid in proc_manager.attached_processes:
            self.mem_fd = proc_manager.attached_processes[pid]['mem_fd']
    
    def write_value(self, address, value, byte_size=4, value_type='int'):
        """Write a value to a specific memory address"""
        if not self.mem_fd:
            raise Exception("Not attached to process")
        
        try:
            if byte_size == 1:
                data = struct.pack('<B', int(value))
            elif byte_size == 2:
                if value_type == 'int':
                    data = struct.pack('<h', int(value))
                else:
                    data = struct.pack('<e', float(value))
            elif byte_size == 4:
                if value_type == 'int':
                    data = struct.pack('<i', int(value))
                else:
                    data = struct.pack('<f', float(value))
            elif byte_size == 8:
                if value_type == 'int':
                    data = struct.pack('<q', int(value))
                else:
                    data = struct.pack('<d', float(value))
            else:
                raise ValueError(f"Unsupported byte size: {byte_size}")
            
            os.lseek(self.mem_fd, address, os.SEEK_SET)
            bytes_written = os.write(self.mem_fd, data)
            
            return bytes_written == len(data)
            
        except PermissionError:
            raise Exception("Permission denied. Need root access.")
        except Exception as e:
            raise Exception(f"Write error at {hex(address)}: {e}")
    
    def write_bytes(self, address, data):
        """Write raw bytes to a memory address"""
        if not self.mem_fd:
            raise Exception("Not attached to process")
        
        try:
            os.lseek(self.mem_fd, address, os.SEEK_SET)
            os.write(self.mem_fd, data)
            return True
        except Exception as e:
            raise Exception(f"Failed to write bytes: {e}")
    
    def freeze_value(self, address, value, interval=1.0):
        """Keep writing a value to freeze it (anti-cheat bypass)"""
        import threading
        import time
        
        def _freeze_loop():
            while True:
                try:
                    self.write_value(address, value, 4)
                    time.sleep(interval)
                except:
                    break
        
        thread = threading.Thread(target=_freeze_loop, daemon=True)
        thread.start()
        return thread
    
    def nop_instruction(self, address, size=4):
        """Overwrite instructions with NOP (0x90) - for code patching"""
        nop_bytes = b'\x90' * size
        return self.write_bytes(address, nop_bytes)
    
    def patch_instruction(self, address, new_bytes):
        """Write custom bytes to patch instructions"""
        if isinstance(new_bytes, str):
            new_bytes = bytes.fromhex(new_bytes.replace(' ', ''))
        return self.write_bytes(address, new_bytes)
