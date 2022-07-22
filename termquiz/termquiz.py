from textual.app import App

from question_table_widget import QuestionTable
from help_table_widget import HelpTable
from qa_dict import all_questions


ALL_QA = all_questions


class TermQuiz(App):
    async def on_load(self, event):
        current_chapter = "04_data_structures"
        self.chapter_questions = ALL_QA.get(current_chapter)
        self.help_dict = {
            "n": ("next", "Следующий вопрос"),
            "p": ("previous", "Предыдущий вопрос"),
            "r": ("retry", "Попробовать еще раз тот же вопрос"),
            "s": ("start", "Начать сначала"),
            "h": ("help", "Toggle help"),
            "right": ("next", "Следующий вопрос"),
            "left": ("previous", "Предыдущий вопрос"),
        }
        await self.bind("ctrl+q", "quit", "quit")
        await self.bind("a", f"answer('show')", "answer", key_display="Показать ответ")
        for key, (word, desc) in self.help_dict.items():
            await self.bind(key, f"step('{word}')", word, key_display=desc)

    async def on_mount(self) -> None:
        self.help = HelpTable()
        await self.view.dock(self.help, edge="bottom")
        self.q_table = QuestionTable(chapter_questions=self.chapter_questions)
        await self.view.dock(self.q_table)

    async def action_answer(self, answer_key: str) -> None:
        if answer_key == "show":
            await self.q_table.update(show_answer=True)

    async def action_step(self, step: str) -> None:
        current_question_number = self.q_table.current_question_number
        if step == "help":
            await self.help.toggle()
        elif step == "retry":
            self.q_table.refresh()
        elif step == "next":
            current_question_number += 1
        elif step == "previous":
            current_question_number -= 1
        elif step == "start":
            current_question_number = 0

        # clamp question number
        if current_question_number >= len(self.chapter_questions):
            current_question_number = len(self.chapter_questions) - 1
        elif current_question_number < 0:
            current_question_number = 0

        # set reactive attribute
        self.q_table.current_question_number = current_question_number

    async def on_key(self, event):
        if event.key.isdigit():
            await self.q_table.update(check_answer=event.key)


def main():
    # windows https://github.com/Textualize/textual/discussions/335
    # os.system("")
    # TermQuiz.run(log="textual.log")
    TermQuiz.run()


if __name__ == "__main__":
    main()
