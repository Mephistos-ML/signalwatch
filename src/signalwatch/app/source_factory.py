from signalwatch.config import SourceConfig
from signalwatch.sources.base import Source
from signalwatch.sources.fake import FakeSource
from signalwatch.sources.tkmaxx import TkMaxxSource


def create_source(source_config: SourceConfig) -> Source:
    if source_config.type == "fake":
        return FakeSource()

    if source_config.type == "tkmaxx":
        if source_config.url is None:
            raise ValueError("Missing URL for TK Maxx source")
        return TkMaxxSource(url=source_config.url)

    raise ValueError(f"Unsupported source type: {source_config.type}")