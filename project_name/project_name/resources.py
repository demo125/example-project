from dagster import ConfigurableResource
from dvc.api import DVCFileSystem

class DVCFileSystemResource(ConfigurableResource):
    """Configurable resource providing connection to MSSQL and database list"""

    def get_dvc_fs(self) -> DVCFileSystem:
        """function providing database connection"""
        return DVCFileSystem(".")
