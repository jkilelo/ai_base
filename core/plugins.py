"""
Core Plugin System for AI Base Platform

This module provides the foundation for creating extensible AI-powered applications.
Each app (Web Testing, Data Quality, etc.) is implemented as a plugin.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type
from dataclasses import dataclass
from enum import Enum
import importlib
import inspect
from pathlib import Path


class PluginStatus(Enum):
    """Plugin status enumeration"""

    INACTIVE = "inactive"
    ACTIVE = "active"
    ERROR = "error"
    LOADING = "loading"


@dataclass
class PluginMetadata:
    """Plugin metadata structure"""

    name: str
    version: str
    description: str
    author: str
    dependencies: List[str]
    api_version: str
    status: PluginStatus = PluginStatus.INACTIVE
    config_schema: Optional[Dict[str, Any]] = None


class BasePlugin(ABC):
    """Base plugin interface that all plugins must implement"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self._metadata: Optional[PluginMetadata] = None

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata"""
        pass

    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the plugin
        Returns True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def cleanup(self) -> bool:
        """
        Cleanup plugin resources
        Returns True if successful, False otherwise
        """
        pass

    @abstractmethod
    def get_api_routes(self) -> List[Dict[str, Any]]:
        """
        Return API routes for this plugin
        Format: [{"path": "/api/v1/plugin", "router": router_instance}]
        """
        pass

    @abstractmethod
    def get_frontend_routes(self) -> List[Dict[str, Any]]:
        """
        Return frontend routes for this plugin
        Format: [{"path": "/app/plugin", "component": "PluginComponent"}]
        """
        pass

    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate plugin configuration"""
        return True

    async def health_check(self) -> Dict[str, Any]:
        """Return plugin health status"""
        return {
            "status": "healthy",
            "message": f"Plugin {self.metadata.name} is operational",
            "details": {},
        }


class PluginManager:
    """Manages plugin lifecycle and registry"""

    def __init__(self):
        self._plugins: Dict[str, BasePlugin] = {}
        self._plugin_metadata: Dict[str, PluginMetadata] = {}

    async def register_plugin(
        self, plugin_class: Type[BasePlugin], config: Dict[str, Any] = None
    ) -> bool:
        """Register a new plugin"""
        try:
            plugin = plugin_class(config)
            metadata = plugin.metadata

            # Validate API version compatibility
            if not self._is_api_compatible(metadata.api_version):
                raise ValueError(
                    f"Plugin API version {metadata.api_version} is not compatible"
                )

            # Validate configuration
            if not await plugin.validate_config(config or {}):
                raise ValueError("Invalid plugin configuration")

            # Initialize plugin
            if not await plugin.initialize():
                raise RuntimeError("Plugin initialization failed")

            self._plugins[metadata.name] = plugin
            self._plugin_metadata[metadata.name] = metadata
            metadata.status = PluginStatus.ACTIVE

            return True

        except Exception as e:
            if metadata:
                metadata.status = PluginStatus.ERROR
            raise e

    async def unregister_plugin(self, plugin_name: str) -> bool:
        """Unregister a plugin"""
        if plugin_name not in self._plugins:
            return False

        plugin = self._plugins[plugin_name]
        try:
            await plugin.cleanup()
            del self._plugins[plugin_name]
            del self._plugin_metadata[plugin_name]
            return True
        except Exception:
            return False

    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """Get a registered plugin"""
        return self._plugins.get(plugin_name)

    def list_plugins(self) -> Dict[str, PluginMetadata]:
        """List all registered plugins"""
        return self._plugin_metadata.copy()

    def get_active_plugins(self) -> List[str]:
        """Get list of active plugin names"""
        return [
            name
            for name, metadata in self._plugin_metadata.items()
            if metadata.status == PluginStatus.ACTIVE
        ]

    async def discover_plugins(self, plugins_dir: Path) -> List[Type[BasePlugin]]:
        """Discover plugins in a directory"""
        discovered = []

        for plugin_file in plugins_dir.glob("**/plugin.py"):
            try:
                # Import the plugin module
                spec = importlib.util.spec_from_file_location(
                    f"plugin_{plugin_file.parent.name}", plugin_file
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Find plugin classes
                for name, obj in inspect.getmembers(module):
                    if (
                        inspect.isclass(obj)
                        and issubclass(obj, BasePlugin)
                        and obj != BasePlugin
                    ):
                        discovered.append(obj)

            except Exception as e:
                print(f"Failed to load plugin from {plugin_file}: {e}")

        return discovered

    async def get_all_api_routes(self) -> List[Dict[str, Any]]:
        """Get API routes from all active plugins"""
        routes = []
        for plugin in self._plugins.values():
            if (
                self._plugin_metadata[plugin.metadata.name].status
                == PluginStatus.ACTIVE
            ):
                routes.extend(plugin.get_api_routes())
        return routes

    async def get_all_frontend_routes(self) -> List[Dict[str, Any]]:
        """Get frontend routes from all active plugins"""
        routes = []
        for plugin in self._plugins.values():
            if (
                self._plugin_metadata[plugin.metadata.name].status
                == PluginStatus.ACTIVE
            ):
                routes.extend(plugin.get_frontend_routes())
        return routes

    async def health_check_all(self) -> Dict[str, Any]:
        """Run health checks on all plugins"""
        results = {}
        for name, plugin in self._plugins.items():
            try:
                results[name] = await plugin.health_check()
            except Exception as e:
                results[name] = {"status": "error", "message": str(e), "details": {}}
        return results

    def _is_api_compatible(self, plugin_api_version: str) -> bool:
        """Check if plugin API version is compatible"""
        # Simple version check - in production, use proper semantic versioning
        supported_versions = ["1.0", "1.1"]
        return plugin_api_version in supported_versions


# Global plugin manager instance
plugin_manager = PluginManager()
