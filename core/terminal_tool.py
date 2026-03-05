"""DEPRECATED: use tools.terminal_tool.TerminalTool instead.
This compatibility stub exists to avoid legacy import breakage.
"""

from tools.terminal_tool import TerminalTool  # re-export


def deprecated_notice() -> str:
    return "DEPRECATED: import TerminalTool from tools.terminal_tool"
