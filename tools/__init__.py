from __future__ import annotations

from .tool_guard import ToolMetadata, ToolRegistry

PYTHON_CMD = "/home/adem/.openclaw/workspace/.venv/bin/python"

TOOL_REGISTRY = ToolRegistry()

TOOL_REGISTRY.register(
    ToolMetadata(
        name="terminal",
        module="tools.terminal_tool",
        description="Terminal komutlarını güvenli şekilde çalıştıran araç",
        smoke_test=f"{PYTHON_CMD} -m tools.terminal_tool --cmd 'echo GrayWolf terminal smoke test'",
        tags=("cli", "shell"),
    )
)

TOOL_REGISTRY.register(
    ToolMetadata(
        name="file",
        module="tools.file_tool",
        description="Dosya okuma/yazma işlemleri için yardımcı",
        smoke_test=f"{PYTHON_CMD} -m tools.file_tool",
        tags=("file", "helper"),
    )
)

TOOL_REGISTRY.register(
    ToolMetadata(
        name="excel",
        module="tools.excel_tool",
        description="Excel tablolarını okuyup yazan araç",
        tags=("excel", "office"),
    )
)

TOOL_REGISTRY.register(
    ToolMetadata(
        name="analysis",
        module="tools.analysis_tool",
        description="LLM tabanlı veri analiz aracı",
    )
)

TOOL_REGISTRY.register(
    ToolMetadata(
        name="code",
        module="tools.code_tool",
        description="Kod üretim ve analiz aracı",
    )
)

__all__ = ["TOOL_REGISTRY", "PYTHON_CMD"]
