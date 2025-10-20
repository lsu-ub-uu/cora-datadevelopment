from unittest.mock import Mock, patch
from common.ssh_tunnel import SSHTunnel


ssh_host = "test.example.com"
ssh_port = 22
ssh_user = "testuser"
local_port = 8080
remote_host = "remote.example.com"
remote_port = 8088


@patch("common.ssh_tunnel.Connection")
def test_ssh_tunnel_context_manager(mock_connection_class):
    """Test that SSHTunnel properly manages the connection lifecycle."""
    # Setup mocks
    mock_connection = Mock()
    mock_tunnel = Mock()
    mock_tunnel.__enter__ = Mock(return_value=mock_tunnel)
    mock_tunnel.__exit__ = Mock(return_value=None)
    mock_connection.forward_local.return_value = mock_tunnel
    mock_connection_class.return_value = mock_connection

    # Use the SSHTunnel context manager
    with SSHTunnel(
        ssh_host,
        ssh_port,
        ssh_user,
        local_port,
        remote_host,
        remote_port,
    ):
        # Verify the connection was created with correct parameters
        mock_connection_class.assert_called_once_with(
            host=ssh_host, port=ssh_port, user=ssh_user
        )

        # Verify forward_local was called with correct parameters
        mock_connection.forward_local.assert_called_once_with(
            local_port=local_port,
            remote_host=remote_host,
            remote_port=remote_port,
            local_host="localhost",
        )

        # Verify tunnel enter was called
        mock_tunnel.__enter__.assert_called_once()

    # Verify tunnel exit was called
    mock_tunnel.__exit__.assert_called_once()
