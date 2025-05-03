import kivy
import os
import html
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.slider import Slider
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.properties import ListProperty, StringProperty
from kivy.animation import Animation
from kivy.metrics import dp, sp
from kivy.utils import platform
from kivy.core.clipboard import Clipboard
from kivy.clock import Clock
import random
import json

kivy.require('2.3.0')

# Platform configuration
if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
    Window.softinput_mode = 'below_target'
    FONT_SIZE_MULTIPLIER = 1
else:
    Window.size = (400, 700)
    FONT_SIZE_MULTIPLIER = 1

# Dynamic sizing functions
def scale_font(base_size):
    return sp(base_size * FONT_SIZE_MULTIPLIER) if platform == 'android' else dp(base_size)

def scale_size(base_size):
    return dp(base_size * (1 if platform == 'android' else 1))

def load_excuses():
    data_path = os.path.join(os.path.dirname(__file__), 'excuses.json')
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            return decode_special_chars(json.load(f))
    except Exception as e:
        print(f"Error loading excuses: {e}")
        return {'School/College': {'Low': ['Data not loaded'], 'Medium': [], 'High': []}}

def decode_special_chars(data):
    return {category: {level: [html.unescape(e).replace("’", "'").replace("‘", "'") 
                           for e in excuses] 
                   for level, excuses in levels.items()} 
            for category, levels in data.items()}

excuses_data = load_excuses()

class AdaptiveButton(Button):
    background_color = ListProperty([0.2, 0.6, 0.8, 1])
    border_radius = ListProperty([25])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = self.background_down = ''
        self.color = [1, 1, 1, 1]
        self.font_size = scale_font(18)
        self.bold = True
        self.size_hint_y = None
        self.height = scale_size(50)
        self.padding = (scale_size(10), scale_size(5))
        self.font_name = 'Roboto'
        self.shadow = None

    def on_press(self):
        anim = Animation(background_color=[c*0.7 for c in self.background_color[:3]]+[1], duration=0.1)
        anim += Animation(background_color=self.background_color, duration=0.2)
        anim.start(self)

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.category = "School/College"
        self.sensitivity = 1
        self._setup_ui()

    def _setup_ui(self):
        with self.canvas.before:
            Color(0.93, 0.96, 1, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_background)
        
        layout = BoxLayout(orientation='vertical', padding=scale_size(15), spacing=scale_size(15))
        layout.add_widget(self._create_title())
        layout.add_widget(self._create_category_selector())
        layout.add_widget(self._create_sensitivity_control())
        layout.add_widget(self._create_generate_button())
        self.add_widget(layout)

    def _create_title(self):
        return Label(
            text="Excuse Generator",
            font_size=scale_font(24),
            bold=True,
            color=[0.2, 0.3, 0.5, 1],
            size_hint_y=None,
            height=scale_size(50))

    def _create_category_selector(self):
        box = BoxLayout(orientation='vertical', spacing=scale_size(8))
        box.add_widget(Label(
            text="Select Category:",
            font_size=scale_font(18),
            color=[0.2, 0.3, 0.5, 1],
            size_hint_y=None,
            height=scale_size(30)))
        
        self.category_btn = AdaptiveButton(
            text=self.category,
            background_color=[0.4, 0.6, 0.9, 1])
        dropdown = DropDown()
        for category in ["School/College", "Work", "Life"]:
            btn = AdaptiveButton(text=category, background_color=[0.4, 0.6, 0.9, 1])
            btn.bind(on_release=lambda b: self._update_category(dropdown, b.text))
            dropdown.add_widget(btn)
        self.category_btn.bind(on_release=dropdown.open)
        box.add_widget(self.category_btn)
        return box

    def _update_category(self, dropdown, category):
        self.category_btn.text = self.category = category
        dropdown.dismiss()

    def _create_sensitivity_control(self):
        box = BoxLayout(orientation='vertical', spacing=scale_size(8))
        self.sensitivity_label = Label(
            text="Sensitivity: Medium",
            font_size=scale_font(18),
            color=[0.2, 0.3, 0.5, 1],
            size_hint_y=None,
            height=scale_size(30))
        
        self.sensitivity_slider = Slider(
            min=0, max=2, value=1, step=1,
            size_hint_y=None,
            height=scale_size(35))
        self.sensitivity_slider.bind(value=self._update_sensitivity)
        box.add_widget(self.sensitivity_label)
        box.add_widget(self.sensitivity_slider)
        return box

    def _update_sensitivity(self, instance, value):
        levels = ["Low", "Medium", "High"]
        self.sensitivity_label.text = f"Sensitivity: {levels[int(value)]}"
        self.sensitivity = int(value)

    def _create_generate_button(self):
        btn = AdaptiveButton(
            text="Generate Excuse",
            background_color=[0.4, 0.7, 0.4, 1],
            height=scale_size(55))
        
        with btn.canvas.before:
            Color(0, 0, 0, 0.1)
            btn.shadow = RoundedRectangle(
                pos=(btn.x-3, btn.y-3),
                size=(btn.width+6, btn.height+6),
                radius=[btn.border_radius[0] + 2])
        
        btn.bind(
            pos=self._update_shadow,
            size=self._update_shadow,
            on_release=lambda x: setattr(self.manager, 'current', 'excuse'))
        return btn

    def _update_shadow(self, instance, value):
        instance.shadow.pos = (instance.x-3, instance.y-3)
        instance.shadow.size = (instance.width+6, instance.height+6)

    def _update_background(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

class ExcuseScreen(Screen):
    excuse_text = StringProperty("Your excuse will appear here")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_ui()

    def _setup_ui(self):
        with self.canvas.before:
            Color(0.1, 0.3, 0.5, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_background)
        
        layout = BoxLayout(orientation='vertical', padding=scale_size(15), spacing=scale_size(15))
        layout.add_widget(self._create_title())
        layout.add_widget(self._create_settings_display())
        layout.add_widget(self._create_excuse_card())
        layout.add_widget(self._create_action_buttons())
        self.add_widget(layout)

    def _create_title(self):
        return Label(
            text="Your Excuse",
            font_size=scale_font(22),
            bold=True,
            color=[1, 1, 1, 1],
            size_hint_y=None,
            height=scale_size(45))

    def _create_settings_display(self):
        self.settings_label = Label(
            text="",
            font_size=scale_font(14),
            color=[1, 1, 1, 0.7],
            size_hint_y=None,
            height=scale_size(20))
        return self.settings_label

    def _create_excuse_card(self):
        card = FloatLayout(size_hint_y=0.6)
        with card.canvas.before:
            Color(0, 0, 0, 1)
            self.card_bg = RoundedRectangle(size=card.size, pos=card.pos, radius=[scale_size(15)])
        card.bind(pos=self._update_card_bg, size=self._update_card_bg)

        self.excuse_input = TextInput(
            text=self.excuse_text,
            size_hint=(0.9, None),
            height=scale_size(150),
            pos_hint={'center_x': 0.5, 'top': 0.7},
            font_size=scale_font(18),
            readonly=True,
            foreground_color=[1, 1, 1, 1],
            background_color=[0, 0, 0, 1],
            cursor_color=[1, 1, 1, 0.5],
            multiline=True,
            padding=(scale_size(10), scale_size(10)),
            halign='center',
            unfocus_on_touch=True
        )
        self.excuse_input.bind(
            focus=self._on_focus_change,
            touch_down=self._schedule_selection_clear
        )
        card.add_widget(self.excuse_input)
        return card

    def _on_focus_change(self, instance, value):
        if not value:
            self._clear_selection()

    def _schedule_selection_clear(self, instance, touch):
        Clock.schedule_once(lambda dt: self._check_selection_clear(touch), 0)

    def _check_selection_clear(self, touch):
        if not self.excuse_input.collide_point(*touch.pos):
            self._clear_selection()

    def _clear_selection(self):
        self.excuse_input.selection_start = 0
        self.excuse_input.selection_end = 0
        if platform == 'android':
            from kivy.base import EventLoop
            self.excuse_input._hide_handles(EventLoop.window)

    def _create_action_buttons(self):
        box = BoxLayout(orientation='vertical', spacing=scale_size(10), 
                      size_hint_y=None, height=scale_size(190))
        
        box.add_widget(Label(
            text="developed by Mhmd-Aslam",
            font_size=scale_font(12),
            color=[1, 1, 1, 0.5],
            size_hint_y=None,
            height=scale_size(20)))
        
        buttons = [
            ("Copy to Clipboard", [0.5, 0.7, 0.9, 1], self._copy_to_clipboard),
            ("Try Again", [0.3, 0.5, 0.8, 1], self._generate_new_excuse),
            ("Main Menu", [0.8, 0.3, 0.3, 1], lambda x: setattr(self.manager, 'current', 'home'))
        ]
        
        for text, color, callback in buttons:
            btn = AdaptiveButton(text=text, background_color=color)
            btn.bind(on_release=callback)
            box.add_widget(btn)
            
        return box

    def _copy_to_clipboard(self, instance):
        if self.excuse_input.text.strip():
            Clipboard.copy(self.excuse_input.text)
            original_text = instance.text
            instance.text, instance.background_color = "Copied!", [0.2, 0.8, 0.2, 1]
            Clock.schedule_once(lambda dt: self._reset_button(instance, original_text), 1)
        else:
            instance.text, instance.background_color = "Nothing to copy!", [0.8, 0.2, 0.2, 1]
            Clock.schedule_once(lambda dt: self._reset_button(instance, "Copy to Clipboard"), 1)

    def _reset_button(self, button, text):
        button.text, button.background_color = text, [0.5, 0.7, 0.9, 1]

    def _update_background(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def _update_card_bg(self, instance, value):
        self.card_bg.size, self.card_bg.pos = instance.size, instance.pos

    def on_enter(self):
        self._generate_new_excuse()

    def _generate_new_excuse(self, instance=None):
        self._clear_selection()
        anim = Animation(opacity=0, duration=0.2)
        anim += Animation(opacity=1, duration=0.2)
        anim.start(self.excuse_input)
        
        home = self.manager.get_screen('home')
        category, sensitivity = home.category, home.sensitivity
        levels = ["Low", "Medium", "High"]
        
        self.settings_label.text = f"Category: {category} | Sensitivity: {levels[sensitivity]}"
        self.excuse_input.text = random.choice(excuses_data[category][levels[sensitivity]])

class ExcuseApp(App):
    def build(self):
        self.title = 'Excuse Generator'
        self.icon = 'assets/applogo.png'
        self.sm = ScreenManager()
        self.sm.add_widget(HomeScreen(name='home'))
        self.sm.add_widget(ExcuseScreen(name='excuse'))
        
        if platform == 'android':
            from kivy.base import EventLoop
            EventLoop.window.bind(on_keyboard=self.on_keyboard)
            
        return self.sm

    def on_keyboard(self, window, key, *args):
        if key == 27:  # Android back button
            if self.sm.current == 'home':
                App.get_running_app().stop()
                return True
            elif self.sm.current == 'excuse':
                self.sm.current = 'home'
                return True
        return False

if __name__ == "__main__":
    ExcuseApp().run()