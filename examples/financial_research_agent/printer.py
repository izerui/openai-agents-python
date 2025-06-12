from typing import Any

from rich.console import Console, Group
from rich.live import Live
from rich.spinner import Spinner


class Printer:
    """
    简单的状态更新输出包装器。用于金融机器人管理器在协调规划、搜索和写作过程中显示进度。
    """

    def __init__(self, console: Console) -> None:
        self.live = Live(console=console)
        self.items: dict[str, tuple[str, bool]] = {}
        self.hide_done_ids: set[str] = set()
        self.live.start()

    def end(self) -> None:
        """结束实时更新"""
        self.live.stop()

    def hide_done_checkmark(self, item_id: str) -> None:
        """隐藏指定项目的完成标记"""
        self.hide_done_ids.add(item_id)

    def update_item(
        self, item_id: str, content: str, is_done: bool = False, hide_checkmark: bool = False
    ) -> None:
        """
        更新项目状态

        Args:
            item_id: 项目标识符
            content: 显示内容
            is_done: 是否完成
            hide_checkmark: 是否隐藏完成标记
        """
        self.items[item_id] = (content, is_done)
        if hide_checkmark:
            self.hide_done_ids.add(item_id)
        self.flush()

    def mark_item_done(self, item_id: str) -> None:
        """标记项目为完成状态"""
        self.items[item_id] = (self.items[item_id][0], True)
        self.flush()

    def flush(self) -> None:
        """刷新显示所有项目的当前状态"""
        renderables: list[Any] = []
        for item_id, (content, is_done) in self.items.items():
            if is_done:
                prefix = "✅ " if item_id not in self.hide_done_ids else ""
                renderables.append(prefix + content)
            else:
                renderables.append(Spinner("dots", text=content))
        self.live.update(Group(*renderables))
