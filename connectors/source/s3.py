import os
from typing import Optional

from mcp.server.fastmcp import Context
from unstructured_client.models.operations import (
    CreateSourceRequest,
    DeleteSourceRequest,
    GetSourceRequest,
    UpdateSourceRequest,
)
from unstructured_client.models.shared import (
    CreateSourceConnector,
    S3SourceConnectorConfigInput,
    UpdateSourceConnector,
)


def _prepare_s3_source_config(
    remote_url: Optional[str],
    recursive: Optional[bool],
) -> S3SourceConnectorConfigInput:
    """Prepare the Azure source connector configuration."""
    return S3SourceConnectorConfigInput(
        remote_url=remote_url,
        recursive=recursive,
        key=os.getenv("AWS_KEY"),
        secret=os.getenv("AWS_SECRET"),
    )


async def create_s3_source(
    ctx: Context,
    name: str,
    remote_url: str,
    recursive: bool = False,
) -> str:
    """Create an S3 source connector.

    Args:
        name: A unique name for this connector
        remote_url: The S3 URI to the bucket or folder (e.g., s3://my-bucket/)
        recursive: Whether to access subfolders within the bucket

    Returns:
        String containing the created source connector information
    """
    client = ctx.request_context.lifespan_context.client
    config = _prepare_s3_source_config(remote_url, recursive)
    source_connector = CreateSourceConnector(name=name, type="s3", config=config)

    try:
        response = await client.sources.create_source_async(
            request=CreateSourceRequest(create_source_connector=source_connector),
        )

        info = response.source_connector_information

        result = ["S3 Source Connector created:"]
        result.append(f"Name: {info.name}")
        result.append(f"ID: {info.id}")
        result.append("Configuration:")
        for key, value in info.config:
            # Don't print secrets in the output
            if key in ["secret", "token"] and value:
                value = "********"
            result.append(f"  {key}: {value}")

        return "\n".join(result)
    except Exception as e:
        return f"Error creating S3 source connector: {str(e)}"


async def update_s3_source(
    ctx: Context,
    source_id: str,
    remote_url: Optional[str] = None,
    recursive: Optional[bool] = None,
) -> str:
    """Update an S3 source connector.

    Args:
        source_id: ID of the source connector to update
        remote_url: The S3 URI to the bucket or folder
        recursive: Whether to access subfolders within the bucket

    Returns:
        String containing the updated source connector information
    """
    client = ctx.request_context.lifespan_context.client

    # Get the current source connector configuration
    try:
        get_response = await client.sources.get_source_async(
            request=GetSourceRequest(source_id=source_id),
        )
        current_config = get_response.source_connector_information.config
    except Exception as e:
        return f"Error retrieving source connector: {str(e)}"

    # Update configuration with new values
    config = dict(current_config)

    if remote_url is not None:
        config["remote_url"] = remote_url

    if recursive is not None:
        config["recursive"] = recursive

    source_connector = UpdateSourceConnector(config=config)

    try:
        response = await client.sources.update_source_async(
            request=UpdateSourceRequest(
                source_id=source_id,
                update_source_connector=source_connector,
            ),
        )

        info = response.source_connector_information

        result = ["S3 Source Connector updated:"]
        result.append(f"Name: {info.name}")
        result.append(f"ID: {info.id}")
        result.append("Configuration:")
        for key, value in info.config:
            # Don't print secrets in the output
            if key in ["secret", "token"] and value:
                value = "********"
            result.append(f"  {key}: {value}")

        return "\n".join(result)
    except Exception as e:
        return f"Error updating S3 source connector: {str(e)}"


async def delete_s3_source(ctx: Context, source_id: str) -> str:
    """Delete an S3 source connector.

    Args:
        source_id: ID of the source connector to delete

    Returns:
        String containing the result of the deletion
    """
    client = ctx.request_context.lifespan_context.client

    try:
        _ = await client.sources.delete_source_async(
            request=DeleteSourceRequest(source_id=source_id),
        )
        return f"S3 Source Connector with ID {source_id} deleted successfully"
    except Exception as e:
        return f"Error deleting S3 source connector: {str(e)}"
