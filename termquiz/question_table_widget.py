from os import get_terminal_size

from rich.padding import Padding
from rich.table import Table
from rich import box
from rich.text import Text
from rich.syntax import Syntax

from textual.widget import Widget
from textual.reactive import Reactive


class QuestionTable(Widget):
    current_question_number = Reactive(0)

    def __init__(
        self,
        topic_questions,
        show_answer=False,
        check_answer=None,
    ):
        super().__init__()
        self.current_question_number = 0
        self.topic_questions = topic_questions
        self.current_question_dict = self.topic_questions[self.current_question_number]
        self.question_count = len(self.topic_questions)
        self.show_answer = show_answer
        self.check_answer = check_answer
        self.selected_answer = ""
        self.all_stats = {index: None for index in range(len(self.topic_questions))}
        self.topic_stats = {"correct": 0, "wrong": 0}
        self.show_stats = False

    def watch_current_question_number(self, value: str) -> None:
        """Called when self.current_question_number is modified."""
        self.current_question_dict = self.topic_questions[self.current_question_number]

    async def toggle_stats(self):
        self.show_stats = not self.show_stats
        self.refresh()

    async def update(
        self,
        selected_answer="",
        show_answer=False,
        check_answer=None,
        current_question_number=None,
    ):
        self.selected_answer = selected_answer
        self.show_answer = show_answer
        self.check_answer = check_answer
        if current_question_number is not None:
            self.current_question_number = current_question_number
        self.refresh()

    def reset_status(self):
        # self.selected_answer = ""
        self.show_answer = False
        self.check_answer = None

    def render(self):
        # Prepare info
        question_code = self._add_syntax_highlight(
            self.current_question_dict.get("code", "")
        )
        enter_number_prompt = self._format_enter_number_prompt()
        self.topic_stats["correct"] = list(self.all_stats.values()).count(True)
        self.topic_stats["wrong"] = list(self.all_stats.values()).count(False)

        # Answers table
        answers_table = Table(box=box.SIMPLE, min_width=50)
        answers_table.add_column("Номер ответа", justify="center", no_wrap=True)
        answers_table.add_column("Ответ", justify="left")
        for num, answer in self.current_question_dict["answers"].items():
            style = self._select_row_style(row_number=num)
            answers_table.add_row(num, answer, style=style)

        # Stats table
        stats_table = Table(box=None, min_width=30)
        stats_table.add_row(
            "Правильных ответов", f"{self.topic_stats['correct']:3}", style="black on green"
        )
        stats_table.add_row(
            "Неправильных ответов", f"{self.topic_stats['wrong']:3}", style="black on red"
        )

        # Question table
        q_table = Table(expand=True, show_header=False, box=None)
        q_table.add_row(
            f"[green]Вопрос {self.current_question_number + 1} из {self.question_count}[/]\n"
            f"{self.current_question_dict['description']}\n"
        )
        q_table.add_row(question_code)
        q_table.add_row(answers_table)
        q_table.add_row(enter_number_prompt)
        if self.show_stats:
            q_table.add_row(stats_table)

        self.reset_status()
        return Padding(q_table, 3)

    def _select_row_style(self, row_number):
        q_correct_answer = self.current_question_dict["correct_answer"]
        q_correct_answer = sorted(q_correct_answer)
        style = None
        if self.selected_answer and row_number in self.selected_answer:
            style = "black on white"
        elif self.show_answer and row_number in q_correct_answer:
            style = "black on green"
        elif self.check_answer:
            self.check_answer = sorted(self.check_answer)
            if row_number in self.check_answer:
                if row_number in q_correct_answer:
                    style = "black on green"
                else:
                    style = "black on red"
        return style

    def _format_enter_number_prompt(self):
        q_correct_answer = self.current_question_dict["correct_answer"]
        q_correct_answer = sorted(q_correct_answer)
        if self.show_answer:
            enter_number_prompt = (
                f"Номер правильного ответа: {', '.join(q_correct_answer)}"
            )
            return enter_number_prompt

        enter_number_prompt = f"Введите номер ответа и нажмите Enter:"
        if self.check_answer:
            enter_number_prompt = (
                f"Введите номер ответа и нажмите Enter: {', '.join(list(self.check_answer))} "
            )
            self.check_answer = sorted(self.check_answer)
            if self.check_answer == q_correct_answer:
                enter_number_prompt += "[black on green]правильный ответ"
                self.all_stats[self.current_question_number] = True
            elif set(self.check_answer) & set(q_correct_answer):
                enter_number_prompt += "[black on yellow]частично правильный ответ"
                self.all_stats[self.current_question_number] = False
            else:
                enter_number_prompt += "[black on red]неправильный ответ"
                self.all_stats[self.current_question_number] = False
        return enter_number_prompt

    def _add_syntax_highlight(self, question_code):
        if "Out" in question_code:
            question_code = Syntax(question_code, "python")
        else:
            question_code = Syntax(question_code, "python", line_numbers=True)
        return question_code
