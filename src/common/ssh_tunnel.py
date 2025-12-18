"""
SSH Tunnel abstraction using Fabric Connection.

This module provides a context manager for SSH tunnels that simplifies
the process of forwarding local ports to remote hosts through an SSH connection.
"""

from fabric import Connection
from typing import Optional


class SSHTunnel:
    """
    Context manager for SSH tunnels using fabric Connection.

    Usage:
        with SSHTunnel(ssh_host, ssh_port, ssh_user, local_port, remote_host, remote_port):
            # Your code that uses the tunnel
            pass
    """

    def __init__(
        self,
        ssh_host: str,
        ssh_port: int,
        ssh_user: str,
        local_port: int,
        remote_host: str,
        remote_port: int,
        local_host: str = "localhost",
    ):
        """
        Initialize SSH tunnel parameters.

        Args:
            ssh_host: SSH server hostname/IP
            ssh_port: SSH server port
            ssh_user: SSH username
            local_port: Local port to bind
            remote_host: Remote host to connect to through tunnel
            remote_port: Remote port to connect to
            local_host: Local host to bind to (default: localhost)
        """
        self.ssh_host = ssh_host
        self.ssh_port = ssh_port
        self.ssh_user = ssh_user
        self.local_port = local_port
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.local_host = local_host
        self._connection: Optional[Connection] = None
        self._tunnel = None

    def __enter__(self):
        """Establish the SSH tunnel."""
        self._connection = Connection(
            host=self.ssh_host, port=self.ssh_port, user=self.ssh_user
        )
        self._tunnel = self._connection.forward_local(
            local_port=self.local_port,
            remote_host=self.remote_host,
            remote_port=self.remote_port,
            local_host=self.local_host,
        )
        return self._tunnel.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close the SSH tunnel and the underlying SSH connection."""
        tunnel_exc = None
        if self._tunnel:
            try:
                self._tunnel.__exit__(exc_type, exc_val, exc_tb)
            except Exception as e:
                tunnel_exc = e
        if self._connection:
            try:
                self._connection.close()
            except Exception as e:
                if not tunnel_exc:
                    tunnel_exc = e
        if tunnel_exc:
            raise tunnel_exc
