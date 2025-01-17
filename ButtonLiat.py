from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.button import MDRaisedButton, MDRectangleFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivy.uix.image import Image
from Consolidated1 import quiz_data, quiz_data2, quiz_data3, quiz_data4, quiz_data5, quiz_data6, quiz_data7, quiz_data8
from kivymd.uix.dialog import MDDialog
import json
from pathlib import Path

Window.size = (310, 580)


class QuizScreen(Screen):
    def __init__(self, quiz_data, **kwargs):
        super().__init__(**kwargs)
        self.quiz_data = quiz_data
        self.current_question = 0
        self.score = 0

        # Main Layout
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # Top Layout for Question and Feedback
        top_layout = BoxLayout(orientation='vertical', size_hint=(1, None), height=220)

        # Question Label
        self.qs_label = MDLabel(
            halign='center',
            valign='middle',
            font_style='H6',
            size_hint=(1, None),
            height=450,
        )
        top_layout.add_widget(self.qs_label)

        self.layout.add_widget(top_layout)

        # Bottom Layout for Answer Buttons and Navigation Buttons
        bottom_layout = BoxLayout(orientation='vertical', size_hint=(1, None), height=300, spacing=20)

        # Answer Buttons
        button_layout = GridLayout(cols=1, spacing=10, size_hint=(1, None), height=200)
        self.choice_btns = [MDRaisedButton(text="", size_hint=(None, None), size=(140, 50)) for _ in range(4)]
        for btn in self.choice_btns:
            btn.bind(on_release=self.check_answer)
            button_layout.add_widget(btn)
        bottom_layout.add_widget(button_layout)

        # Navigation Label Layout
        nav_label_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=50, spacing=20)
        self.feedback_label = MDLabel(text="", halign='left', height=50)
        self.score_label = MDLabel(text=f"Score: {self.score}/{len(self.quiz_data)}", halign='right', height=50)
        nav_label_layout.add_widget(self.feedback_label)
        nav_label_layout.add_widget(self.score_label)
        bottom_layout.add_widget(nav_label_layout)

        # Navigation Buttons (Next and Back)
        nav_buttons_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=50, spacing=20)
        self.back_button = MDRaisedButton(text="Back", size_hint=(0.5, None), height=50, md_bg_color=(0.4, 0.4, 0.4, 1))
        self.back_button.bind(on_release=self.show_confirmation_dialog)
        self.next_btn = MDRaisedButton(text="Next", size_hint=(0.5, None), height=50, disabled=True)
        self.next_btn.bind(on_release=self.next_question)
        nav_buttons_layout.add_widget(self.back_button)
        nav_buttons_layout.add_widget(self.next_btn)
        bottom_layout.add_widget(nav_buttons_layout)

        self.layout.add_widget(bottom_layout)

        self.add_widget(self.layout)
        self.show_question()

    def show_question(self):
        """Displays the current question and resets button states."""
        question = self.quiz_data[self.current_question]
        self.qs_label.text = question["question"]

        for i, btn in enumerate(self.choice_btns):
            btn.text = question["choices"][i]
            btn.disabled = False

        self.feedback_label.text = ""
        self.next_btn.disabled = True

    def check_answer(self, button):
        """Checks the answer and provides feedback."""
        selected_choice = button.text
        question = self.quiz_data[self.current_question]

        if selected_choice == question["answer"]:
            self.score += 1
            self.feedback_label.text = "Correct!"
            self.feedback_label.color = (0, 1, 0, 1)  # Green
        else:
            self.feedback_label.text = "Incorrect!"
            self.feedback_label.color = (1, 0, 0, 1)  # Red

        for btn in self.choice_btns:
            btn.disabled = True
        self.next_btn.disabled = False
        self.score_label.text = f"Score: {self.score}/{len(self.quiz_data)}"

    def next_question(self, *args):
        """Loads the next question or shows the final score."""
        self.current_question += 1
        if self.current_question < len(self.quiz_data):
            self.show_question()
        else:
            self.show_final_score()

    def show_final_score(self):
        """Displays the final score and saves it to a local file."""
        test_name = self.name  # Use the screen name as the test name
        self.save_test_score(test_name, f"{self.score}/{len(self.quiz_data)}")  # Use self.save_test_score

        self.dialog = MDDialog(
            title="Quiz Completed",
            text=f"Final score for {test_name}: {self.score}/{len(self.quiz_data)} "
                 f"({(self.score / len(self.quiz_data)) * 100:.2f}%)",
            buttons=[MDRaisedButton(text="OK", on_release=self.go_back)]
        )
        self.dialog.open()

    def save_test_score(self, test_name, score):
        """Saves the test name, score, and percentage to a local file."""
        app_directory = Path().home() / ".my_kivymd_app"  # App directory
        app_directory.mkdir(exist_ok=True)  # Ensure the directory exists

        score_file = app_directory / "test_scores.json"

        # Check if the file exists, if not initialize it as an empty dictionary
        if score_file.exists():
            try:
                with open(score_file, "r") as f:
                    scores = json.load(f)
            except json.JSONDecodeError:
                # If the file is corrupted or empty, reset the scores to an empty dictionary
                scores = {}
        else:
            scores = {}

        # Extract the score and total from the current test score
        score_value, total_questions = map(int, score.split('/'))

        # Calculate the percentage
        percentage = (score_value / total_questions) * 100

        # Update the scores with the current test (store only score and percentage)
        scores[test_name] = f"{score_value}/{total_questions} ({percentage:.2f}%)"

        # Save the updated scores back to the file
        with open(score_file, "w") as f:
            json.dump(scores, f, indent=4)

    def return_to_list_screen(self, *args):
        """Closes the dialog and navigates back to the Button List screen."""
        self.dialog.dismiss()
        self.manager.current = 'list'  # Navigate to the 'list' screen

    def show_confirmation_dialog(self, *args):
        """Shows a confirmation dialog when clicking the back button."""
        self.dialog = MDDialog(
            title="Confirm Exit",
            text="Are you sure you want to go back?",
            buttons=[
                MDRaisedButton(text="Yes", on_release=self.go_back),
                MDRaisedButton(text="No", on_release=self.close_confirmation_dialog)  # Call the renamed method
            ]
        )
        self.dialog.open()

    def close_confirmation_dialog(self, *args):
        """Closes the confirmation dialog."""
        self.dialog.dismiss()

    def go_back(self, *args):
        """Resets the quiz and navigates back to the list screen."""
        self.dialog.dismiss()
        self.current_question = 0
        self.score = 0
        self.score_label.text = f"Score: {self.score}/{len(self.quiz_data)}"
        self.show_question()
        self.manager.current = 'list'  # This assumes the screen manager is set to navigate back to 'list'

    def close_dialog(self, *args):
        """Closes the final score dialog and navigates back."""
        self.dialog.dismiss()
        self.go_back()


class ButtonListScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Add the background image
        background = Image(
            source="Bg1.jpg",  # Path to your image
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.add_widget(background)

        # Create a GridLayout for buttons
        layout = GridLayout(
            cols=2,  # Number of columns
            padding=25,
            spacing=40,
            size_hint=(1, 1), pos_hint={'center_x': 0.65, 'center_y': 0.25}
        )

        # Button data
        button_data = ["Test 1", "Test 2", "Test 3", "Test 4", "Test 5",
                       "Test 6", "Test 7", "Test 8", "View Score"]

        # Add buttons to the grid layout
        for name in button_data:
            button = MDRectangleFlatButton(
                text=name, md_bg_color=(0.4, 0.4, 0.4, 0.1), font_name="fonts/Roboto-Bold.ttf",
                size_hint=(None, None),
                size=(90, 50),  # Button size
                pos_hint={'center_x': 0.5, 'center_y': 0.8}

            )
            button.bind(on_press=self.go_to_page)
            layout.add_widget(button)

        # Add the grid layout to the screen
        self.add_widget(layout)

    def show_all_scores(self):
        """Reads and displays all test scores from the local file."""
        app_directory = Path().home() / ".my_kivymd_app"
        score_file = app_directory / "test_scores.json"

        # Check if the file exists
        if score_file.exists():
            with open(score_file, "r") as f:
                scores = json.load(f)

            # Format the scores for display
            scores_text = "\n".join([f"{test}: {score}" for test, score in scores.items()])
        else:
            scores_text = "No scores available yet."

        # Display the scores in a dialog
        self.dialog = MDDialog(
            title="All Test Scores",
            text=scores_text,
            buttons=[MDRaisedButton(text="OK", on_release=lambda x: self.dialog.dismiss())]
        )
        self.dialog.open()

    def go_to_page(self, instance):
        # Navigate to the corresponding quiz page
        if instance.text.startswith("Test"):
            quiz_name = f"Test{instance.text.split()[-1]}"
            self.manager.current = quiz_name
        elif instance.text == "View Score":
            self.show_all_scores()


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Add the background image
        background = Image(
            source="Bg1.jpg",  # Path to your image
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.add_widget(background)

        # Add a button to navigate to ButtonListScreen
        navigate_button = MDRectangleFlatButton(
            text="Go to Button List",
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        navigate_button.bind(on_press=self.go_to_button_list)
        self.add_widget(navigate_button)

    def go_to_button_list(self, instance):
        self.manager.current = "button_list"


class MyApp(MDApp):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(ButtonListScreen(name='list'))
        sm.add_widget(QuizScreen(name='Test1', quiz_data=quiz_data))
        sm.add_widget(QuizScreen(name='Test2', quiz_data=quiz_data2))
        sm.add_widget(QuizScreen(name='Test3', quiz_data=quiz_data3))
        sm.add_widget(QuizScreen(name='Test4', quiz_data=quiz_data4))
        sm.add_widget(QuizScreen(name='Test5', quiz_data=quiz_data5))
        sm.add_widget(QuizScreen(name='Test6', quiz_data=quiz_data6))
        sm.add_widget(QuizScreen(name='Test7', quiz_data=quiz_data7))
        sm.add_widget(QuizScreen(name='Test8', quiz_data=quiz_data8))
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(ButtonListScreen(name="button_list"))

        return sm


if __name__ == '__main__':
    MyApp().run()
