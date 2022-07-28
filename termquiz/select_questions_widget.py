from rich.padding import Padding
from rich.table import Table
from rich import box
from textual.widget import Widget


class SelectQuestionTable(Widget):
    def __init__(
        self,
        all_topics,
    ):
        super().__init__()
        self.all_topics = all_topics
        self.current_topic = None
        self.key_topic_map = {
            str(key): topic for key, topic in enumerate(self.all_topics, 1)
        }

    def render(self):
        topics_table = Table(box=box.SIMPLE, min_width=50)
        topics_table.add_column("Номер", justify="center", no_wrap=True)
        topics_table.add_column("Тема", justify="left")
        for key, topic in self.key_topic_map.items():
            if self.current_topic and key == self.current_topic:
                topics_table.add_row(key, topic, style="black on white")
            else:
                topics_table.add_row(key, topic)

        main_table = Table(expand=True, show_header=False, box=None)
        main_table.add_row("Выберите тему и нажмите Enter")
        main_table.add_row(topics_table)
        if self.current_topic and self.current_topic not in self.key_topic_map:
            main_table.add_row(
                f"Выберите вопросы из диапазона {', '.join(self.key_topic_map)}.\n"
                f"Нажмите Enter чтобы сбить введенные числа",
                style="black on red",
            )
        return Padding(main_table, 3)

    async def update(self, selected_topic):
        self.current_topic = selected_topic
        self.refresh()
