#!/usr/bin/env python3
"""Update checksums for all build artifacts"""

import hashlib
import os
from pathlib import Path
from datetime import datetime

def main():
    dist_dir = Path('dist')
    checksums = {}
    
    print("Calculating checksums for all build artifacts...")
    
    for file_path in dist_dir.iterdir():
        if file_path.is_file() and not file_path.name.startswith('checksums') and not file_path.name.startswith('SHA256'):
            print(f"Processing: {file_path.name}")
            with open(file_path, 'rb') as f:
                content = f.read()
            
            checksums[file_path.name] = {
                'size': len(content),
                'sha256': hashlib.sha256(content).hexdigest(),
                'md5': hashlib.md5(content).hexdigest(),
                'sha1': hashlib.sha1(content).hexdigest()
            }
    
    # Write comprehensive checksum file
    with open('dist/checksums.txt', 'w', encoding='utf-8') as f:
        f.write('# AugmentCode-Free v1.0.0 File Checksums\n')
        f.write(f'# Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
        f.write('# Author: BasicProtein\n\n')
        
        for filename, hashes in checksums.items():
            f.write(f'File: {filename}\n')
            f.write(f'Size: {hashes["size"]:,} bytes\n')
            f.write(f'SHA256: {hashes["sha256"]}\n')
            f.write(f'SHA1:   {hashes["sha1"]}\n')
            f.write(f'MD5:    {hashes["md5"]}\n')
            f.write('-' * 80 + '\n\n')
    
    # Write SHA256SUMS file
    with open('dist/SHA256SUMS', 'w', encoding='utf-8') as f:
        for filename, hashes in checksums.items():
            f.write(f'{hashes["sha256"]}  {filename}\n')
    
    print(f'Updated checksums for {len(checksums)} files')
    
    # Display summary
    total_size = sum(h['size'] for h in checksums.values())
    print(f'Total artifacts size: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)')

if __name__ == "__main__":
    main()
