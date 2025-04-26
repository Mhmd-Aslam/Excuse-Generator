import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
import random
import json

kivy.require('2.1.0')  # Specify Kivy version

# Load the excuses data from JSON file
with open('excuses.json') as f:
    excuses_data = json.load(f)

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Dropdown menu for category
        self.category_dropdown = DropDown()
        self.category_button = Button(text="Select Category: Life", size_hint_y=None, height=44)
        self.category_button.bind(on_release=self.category_dropdown.open)
        
        categories = ["School/College", "Work", "Life"]
        for category in categories:
            btn = Button(text=category, size_hint_y=None, height=44)
            btn.bind(on_release=self.set_category)
            self.category_dropdown.add_widget(btn)
        
        # Slider for sensitivity
        self.sensitivity_label = Label(text="Sensitivity: Medium", size_hint_y=None, height=44)
        self.sensitivity_slider = Slider(min=0, max=2, value=1, step=1)
        self.sensitivity_slider.bind(value=self.set_sensitivity)

        # Generate Excuse button
        self.generate_button = Button(text="Generate Excuse", size_hint_y=None, height=44)
        self.generate_button.bind(on_release=self.generate_excuse)
        
        layout.add_widget(self.category_button)
        layout.add_widget(self.sensitivity_label)
        layout.add_widget(self.sensitivity_slider)
        layout.add_widget(self.generate_button)
        
        self.add_widget(layout)

        # Default values
        self.category = "Life"
        self.sensitivity = 1  # Medium

    def set_category(self, btn):
        self.category_button.text = f"Select Category: {btn.text}"
        self.category = btn.text

    def set_sensitivity(self, slider, value):
        sensitivity_levels = ["Low", "Medium", "High"]
        self.sensitivity_label.text = f"Sensitivity: {sensitivity_levels[value]}"
        self.sensitivity = value

    def generate_excuse(self, instance):
        self.manager.current = 'excuse'

class ExcuseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        self.excuse_label = Label(text="Your Excuse", font_size=24)
        self.retry_button = Button(text="Retry", size_hint_y=None, height=44)
        self.home_button = Button(text="Home", size_hint_y=None, height=44)

        self.retry_button.bind(on_release=self.generate_new_excuse)
        self.home_button.bind(on_release=self.go_home)
        
        layout.add_widget(self.excuse_label)
        layout.add_widget(self.retry_button)
        layout.add_widget(self.home_button)
        
        self.add_widget(layout)

    def on_enter(self):
        # This is called when the screen is fully loaded and entered
        self.generate_new_excuse()

    def generate_new_excuse(self, instance=None):
        # Retrieve the selected category and sensitivity from the HomeScreen
        category = self.manager.get_screen('home').category
        sensitivity = self.manager.get_screen('home').sensitivity
        sensitivity_levels = ["Low", "Medium", "High"]
        
        excuse_list = excuses_data[category][sensitivity_levels[sensitivity]]
        excuse = random.choice(excuse_list)
        
        self.excuse_label.text = excuse

    def go_home(self, instance):
        self.manager.current = 'home'

class ExcuseApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(ExcuseScreen(name='excuse'))
        return sm

if __name__ == "__main__":
    ExcuseApp().run()
