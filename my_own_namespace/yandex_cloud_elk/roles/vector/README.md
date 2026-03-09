Vector role

This role installs and configures Vector.

Role Variables

| Variable | Description |
|----------|-------------|
| vector_version_rpm | Version for RPM systems |
| vector_version_deb | Version for DEB systems |

Example Playbook

- hosts: vector
  roles:
    - vector

