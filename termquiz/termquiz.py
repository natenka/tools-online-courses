import os

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
        self.digits_key = ""

    async def on_mount(self) -> None:
        self.topics_table = SelectQuestionTable(ALL_QA)
        await self.view.dock(self.topics_table)

    async def on_key(self, event):
        # Select topic table
        if self.current_topic is None:
            self.current_topic = await self.select_topic_on_key(event)
            if self.current_topic:
                self.current_topic_questions = self.all_topics[self.current_topic]
                await self.load_q_table()

        # Select answer in question table
        else:
            await self.select_answer_on_key(event)

    def clear_current_view(self):
        self.view.layout.docks = []

    async def action_change(self, change: str) -> None:
        if change == "change topic":
            self.current_topic = None
            self.clear_current_view()
            await self.view.dock(self.topics_table)

    async def action_step(self, step: str) -> None:
        current_question_number = self.q_table.current_question_number
        if step == "help":
            await self.help.toggle()
        elif step == "stats":
            await self.q_table.toggle_stats()
        elif step == "answer":
            await self.q_table.update(show_answer=True)
        elif step == "retry":
            # retry должен затирать key
            self.digits_key = ""
            await self.q_table.update(selected_answer="")
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
            "h": ("help", "toggle help"),
            "i": ("stats", "toggle stats"),
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

    async def select_topic_on_key(self, event):
        # Select topic table
        if event.key.isdigit():
            self.digits_key += event.key
            await self.topics_table.update(selected_topic=self.digits_key)
            return None
        elif event.key == "enter":
            key = self.digits_key
            self.digits_key = ""
            current_topic = self.topics_table.key_topic_map.get(key)
            await self.topics_table.update(selected_topic=key)
            return current_topic

    async def select_answer_on_key(self, event):
        current_question_dict = self.q_table.current_question_dict
        mult_choice = current_question_dict.get("multiple_choices")
        if event.key.isdigit():
            if not mult_choice:
                self.digits_key = event.key
            else:
                self.digits_key += event.key
            await self.q_table.update(selected_answer=self.digits_key)
        elif event.key == "enter":
            key = self.digits_key
            self.digits_key = ""
            await self.q_table.update(check_answer=key, selected_answer="")


def main():
    # windows https://github.com/Textualize/textual/discussions/335
    os.system("")
    TermQuiz.run()
    # TermQuiz.run(log="textual.log")


if __name__ == "__main__":
    main()
