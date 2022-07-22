import os
import asyncio

from textual.app import App

from question_table_widget import QuestionTable
from help_table_widget import HelpTable
from select_questions_widget import SelectQuestionTable
from qa_dict import all_questions


ALL_QA = all_questions


class TermQuiz(App):
    async def on_load(self, event):
        self.all_topics = ALL_QA
        self.current_topic = None
        self.current_topic_questions = None

    async def on_mount(self) -> None:
        self.topics_table = SelectQuestionTable(ALL_QA)
        await self.view.dock(self.topics_table)

    async def on_key(self, event):
        if self.current_topic is None and event.key.isdigit():
            self.current_topic = self.topics_table.key_topic_map.get(event.key)
            await self.topics_table.update(selected_topic=event.key)
            await asyncio.sleep(0.5)
            if self.current_topic:
                self.current_topic_questions = self.all_topics[self.current_topic]
                await self.load_q_table()

        elif event.key.isdigit():
            await self.q_table.update(check_answer=event.key)

    def clear_current_view(self):
        self.view.layout.docks = []

    async def load_q_table(self):
        self.clear_current_view()
        # load questions
        self.help = HelpTable()
        await self.view.dock(self.help, edge="bottom")
        self.q_table = QuestionTable(topic_questions=self.current_topic_questions)
        await self.view.dock(self.q_table)

        # bind keys
        self.help_dict = {
            "n": ("next", "Следующий вопрос"),
            "p": ("previous", "Предыдущий вопрос"),
            "r": ("retry", "Попробовать еще раз тот же вопрос"),
            "s": ("start", "Начать сначала"),
            "a": ("answer", "Показать ответ"),
            "h": ("help", "Toggle help"),
        }
        await self.bind("ctrl+q", "quit", "quit")
        for key, (word, desc) in self.help_dict.items():
            await self.bind(key, f"step('{word}')", word, key_display=desc)
        await self.bind(
            "c",
            "change('change topic')",
            "change topic",
            key_display="Выбрать другой раздел вопросов",
        )

    async def action_change(self, change: str) -> None:
        if change == "change topic":
            self.current_topic = None
            # await self.topics_table.update(selected_topic=None)
            self.clear_current_view()
            await self.view.dock(self.topics_table)

    async def action_step(self, step: str) -> None:
        current_question_number = self.q_table.current_question_number
        if step == "help":
            await self.help.toggle()
        elif step == "answer":
            await self.q_table.update(show_answer=True)
        elif step == "retry":
            self.q_table.refresh()
        elif step == "next":
            current_question_number += 1
        elif step == "previous":
            current_question_number -= 1
        elif step == "start":
            current_question_number = 0

        # clamp question number
        if current_question_number >= len(self.current_topic_questions):
            current_question_number = len(self.current_topic_questions) - 1
        elif current_question_number < 0:
            current_question_number = 0

        # set reactive attribute
        self.q_table.current_question_number = current_question_number


def main():
    # windows https://github.com/Textualize/textual/discussions/335
    os.system("")
    TermQuiz.run()
    # TermQuiz.run(log="textual.log")


if __name__ == "__main__":
    main()
