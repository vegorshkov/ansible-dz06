#!/usr/bin/python

# Copyright: (c) 2025, Your Name <your.email@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import pwd
import grp
import time

DOCUMENTATION = r'''
---
module: my_own_module

short_description: Creates a file on a remote host with specified content

version_added: "1.0.0"

description:
    - This module creates a text file on the remote host at the specified path with the given content.
    - If the file already exists and content differs, it will be overwritten (changed=True).
    - If the file already exists and content matches, no changes are made (changed=False).
    - After creating/updating the file, returns detailed listing of the target directory.

options:
    path:
        description:
            - The full path of the file to create on the remote host.
        required: true
        type: str
    content:
        description:
            - The content to write into the file.
        required: true
        type: str

author:
    - Your Name (@yourGitHubHandle)
'''

EXAMPLES = r'''
- name: Create a file with some content
  my_own_module:
    path: /tmp/testfile.txt
    content: "Hello, world!"

- name: Create another file and see directory listing
  my_own_module:
    path: /home/user/config.cfg
    content: |
      setting1=value1
      setting2=value2
'''

RETURN = r'''
original_path:
    description: The original path that was passed in.
    type: str
    returned: always
    sample: "/tmp/testfile.txt"
original_content:
    description: The original content that was passed in.
    type: str
    returned: always
    sample: "Hello, world!"
message:
    description: Status message indicating what was done.
    type: str
    returned: always
    sample: "File created successfully"
directory_listing:
    description: Detailed listing of the target directory after operation.
    type: list
    returned: when directory exists and is accessible
    contains:
        name:
            description: Name of the file or directory.
            type: str
            sample: "testfile.txt"
        type:
            description: Type of filesystem object (file/dir/link).
            type: str
            sample: "file"
        size:
            description: Size in bytes.
            type: int
            sample: 1234
        permissions:
            description: Unix permissions in octal format (e.g., 644).
            type: str
            sample: "644"
        owner:
            description: Owner username.
            type: str
            sample: "root"
        group:
            description: Group name.
            type: str
            sample: "root"
        modified:
            description: Last modification time in human readable format.
            type: str
            sample: "2025-03-05 15:30:45"
        modified_timestamp:
            description: Last modification time as Unix timestamp.
            type: float
            sample: 1741195845.0
    sample: [
        {
            "name": "testfile.txt",
            "type": "file",
            "size": 1234,
            "permissions": "644",
            "owner": "user",
            "group": "user",
            "modified": "2025-03-05 15:30:45",
            "modified_timestamp": 1741195845.0
        },
        {
            "name": "other_file.log",
            "type": "file",
            "size": 5678,
            "permissions": "640",
            "owner": "root",
            "group": "adm",
            "modified": "2025-03-04 09:15:22",
            "modified_timestamp": 1741108522.0
        }
    ]
directory_path:
    description: The path of the directory that was listed.
    type: str
    returned: when directory exists and is accessible
    sample: "/tmp"
'''

from ansible.module_utils.basic import AnsibleModule


def get_directory_listing(directory_path):
    """
    Get detailed listing of a directory similar to 'ls -la'.
    
    Args:
        directory_path (str): Path to the directory to list
        
    Returns:
        list: List of dictionaries with file/directory details
    """
    listing = []
    
    try:
        # Get all items in the directory
        for item in sorted(os.listdir(directory_path)):
            item_path = os.path.join(directory_path, item)
            
            try:
                # Get file stats
                stat = os.stat(item_path)
                
                # Determine file type
                if os.path.islink(item_path):
                    file_type = 'link'
                elif os.path.isdir(item_path):
                    file_type = 'directory'
                elif os.path.isfile(item_path):
                    file_type = 'file'
                else:
                    file_type = 'other'
                
                # Get owner and group names
                try:
                    owner = pwd.getpwuid(stat.st_uid).pw_name
                except:
                    owner = str(stat.st_uid)
                    
                try:
                    group = grp.getgrgid(stat.st_gid).gr_name
                except:
                    group = str(stat.st_gid)
                
                # Format modification time
                mod_time = time.localtime(stat.st_mtime)
                mod_time_str = time.strftime('%Y-%m-%d %H:%M:%S', mod_time)
                
                # Build item info
                item_info = {
                    'name': item,
                    'type': file_type,
                    'size': stat.st_size,
                    'permissions': oct(stat.st_mode)[-3:],
                    'owner': owner,
                    'group': group,
                    'modified': mod_time_str,
                    'modified_timestamp': stat.st_mtime
                }
                
                # Add symlink target if it's a link
                if file_type == 'link':
                    try:
                        item_info['link_target'] = os.readlink(item_path)
                    except:
                        pass
                
                listing.append(item_info)
                
            except (OSError, IOError) as e:
                # If we can't stat a specific file, add error info
                listing.append({
                    'name': item,
                    'error': str(e),
                    'type': 'unknown'
                })
                
    except (OSError, IOError) as e:
        # If we can't list the directory at all, return error
        return {'error': str(e)}
    
    return listing


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        path=dict(type='str', required=True),
        content=dict(type='str', required=True)
    )

    # seed the result dict in the object
    result = dict(
        changed=False,
        original_path='',
        original_content='',
        message=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # Store original parameters
    result['original_path'] = module.params['path']
    result['original_content'] = module.params['content']

    # Check if file already exists and read its content
    file_exists = os.path.isfile(module.params['path'])
    current_content = None

    if file_exists:
        try:
            with open(module.params['path'], 'r') as f:
                current_content = f.read()
        except Exception as e:
            module.fail_json(msg=f"Failed to read existing file: {str(e)}", **result)

    # Determine if changes are needed
    if not file_exists or current_content != module.params['content']:
        result['changed'] = True

    # If in check mode, exit early
    if module.check_mode:
        module.exit_json(**result)

    # Perform actual file write if changes are needed
    if result['changed']:
        try:
            # Ensure directory exists
            directory = os.path.dirname(module.params['path'])
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            # Write content to file
            with open(module.params['path'], 'w') as f:
                f.write(module.params['content'])

            result['message'] = "File created/updated successfully"
            
        except Exception as e:
            module.fail_json(msg=f"Failed to write file: {str(e)}", **result)
    else:
        result['message'] = "File already exists with the same content, no changes made"
    
    # --- ADDED: Get directory listing after operation ---
    directory = os.path.dirname(module.params['path'])
    if directory and os.path.exists(directory):
        try:
            listing = get_directory_listing(directory)
            # If listing is a list (success), add it to result
            if isinstance(listing, list):
                result['directory_listing'] = listing
                result['directory_path'] = directory
            else:
                # If there was an error, add it
                result['directory_listing_error'] = listing.get('error', 'Unknown error')
        except Exception as e:
            result['directory_listing_error'] = str(e)
    # --- END ADDED ---

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
