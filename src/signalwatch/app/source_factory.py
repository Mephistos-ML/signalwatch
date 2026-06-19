from signalwatch.config import SourceConfig
from signalwatch.sources.base import Source
from signalwatch.sources.fake import FakeSource


def create_source(source_config: SourceConfig) -> Source:
    if source_config.type == "fake":
        return FakeSource()

    raise ValueError(f"Unsupported source type: {source_config.type}")