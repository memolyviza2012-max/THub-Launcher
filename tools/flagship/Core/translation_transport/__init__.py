"""Translation-only routing. Importing this package never changes API configuration."""
from .gateway import TranslationGateway, snapshot_config, is_web
from .contracts import WebTransportError, RowTarget

