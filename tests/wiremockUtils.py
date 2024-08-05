from pathlib import Path

import pytest
from wiremock.client import (
    HttpMethods,
    Mapping,
    MappingRequest,
    MappingResponse,
    Mappings,
)
from wiremock.constants import Config
from wiremock.testing.testcontainer import WireMockContainer, wiremock_container


class WireMockManager:
    """Manage mocking of URL."""

    __mock_container: WireMockContainer

    def __init__(self, mock_container: WireMockContainer):
        self.__mock_container = mock_container
        Config.base_url = self.__mock_container.get_url("__admin")

    def __del__(self):
        Mappings.delete_all_mappings()

    def get_url(self) -> str:
        return self.__mock_container.get_url("/")

    def add_string_mapping(
        self,
        url: str,
        body: str,
        *,
        pattern: bool = False,
        priority: int | None = None,
    ) -> None:
        request = MappingRequest(
            method=HttpMethods.GET,
        )

        if pattern:
            request.url_pattern = url
        else:
            request.url = url

        mapping = Mapping(
            request=request,
            response=MappingResponse(status=200, body=body),
            persistent=False,
        )

        if priority:
            mapping.priority = priority

        Mappings.create_mapping(mapping)

    def add_file_mapping(
        self,
        url: str,
        host_path: str,
    ) -> None:
        """Copy file to container and add WireMock mapping for it."""

        container_dir_path = Path("/home/wiremock/__files")

        with open(host_path, "rb") as f:
            self.__mock_container.copy_files_to_container(
                {host_path: f.read()}, container_dir_path, "wb"
            )

        Mappings.create_mapping(
            Mapping(
                request=MappingRequest(
                    method=HttpMethods.GET,
                    url=url,
                ),
                response=MappingResponse(
                    status=200, body_file_name=Path(host_path).name
                ),
                persistent=False,
            )
        )


@pytest.fixture(scope="session", autouse=False)
def wiremock_manager():
    with wiremock_container(secure=False) as mock_container:
        yield WireMockManager(mock_container)
