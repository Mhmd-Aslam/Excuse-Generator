import kivy
import os
import html
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.boxlayout import BoxLayout
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

# Platform-specific configuration
if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
    Window.softinput_mode = 'below_target'
    DEFAULT_FONT_SIZE = sp(18)
else:
    DEFAULT_FONT_SIZE = dp(18)
    Window.size = (400, 700)

def load_excuses():
    data_path = os.path.join(os.path.dirname(__file__), 'excuses.json')
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return decode_special_chars(data)

def decode_special_chars(data):
    """Handle special characters and apostrophes"""
    decoded = {}
    for category, levels in data.items():
        decoded[category] = {}
        for level, excuses in levels.items():
            decoded[category][level] = [
                html.unescape(e)
                .replace("’", "'")
                .replace("‘", "'")
                for e in excuses
            ]
    return decoded

excuses_data = load_excuses()

class PlatformAwareRoundedButton(Button):
    background_color = ListProperty([0.2, 0.6, 0.8, 1])
    border_radius = ListProperty([25 if platform == 'android' else 25])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = kwargs.get('background_color', [0.2, 0.6, 0.8, 1])
        self.color = [1, 1, 1, 1]
        self.font_size = sp(18) if platform == 'android' else dp(18)
        self.bold = True
        self.size_hint_y = None
        self.height = dp(45) if platform == 'android' else dp(45)
        self.padding = (dp(10), dp(10))
        self.font_name = 'Roboto'

    def on_press(self):
        anim = Animation(background_color=[c * 0.8 for c in self.background_color[:3]] + [1],
                         duration=0.1)
        anim += Animation(background_color=self.background_color, duration=0.1)
        anim.start(self)
        return super().on_press()

class OptimizedHomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._configure_background()
        self._setup_ui()
        self.category = "School/College"
        self.sensitivity = 1

    def _configure_background(self):
        with self.canvas.before:
            Color(0.93, 0.96, 1, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_background)

    def _setup_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(15))
        content_layout = self._create_content_layout()
        main_layout.add_widget(content_layout)
        self.add_widget(main_layout)

    def _create_content_layout(self):
        layout = BoxLayout(orientation='vertical', spacing=dp(15))
        
        # Title
        layout.add_widget(Label(
            text="Excuse Generator",
            font_size=sp(28) if platform == 'android' else dp(28),
            bold=True,
            color=[0.2, 0.3, 0.5, 1],
            size_hint_y=None,
            height=dp(50)))
        
        # Category Selection
        layout.add_widget(self._create_category_selector())
        # Sensitivity Control
        layout.add_widget(self._create_sensitivity_control())
        # Generate Button
        layout.add_widget(self._create_generate_button())
        
        return layout

    def _create_category_selector(self):
        box = BoxLayout(orientation='vertical', spacing=dp(8))
        box.add_widget(Label(
            text="Select Category:",
            font_size=DEFAULT_FONT_SIZE,
            color=[0.2, 0.3, 0.5, 1],
            size_hint_y=None,
            height=dp(30)))
        
        self.category_dropdown = DropDown()
        self.category_button = PlatformAwareRoundedButton(
            text="School/College",
            background_color=[0.4, 0.6, 0.9, 1])
        self.category_button.bind(on_release=self.category_dropdown.open)
        
        for category in ["School/College", "Work", "Life"]:
            btn = PlatformAwareRoundedButton(
                text=category,
                background_color=[0.4, 0.6, 0.9, 1])
            btn.bind(on_release=lambda b: self._update_category(b.text))
            self.category_dropdown.add_widget(btn)
        
        box.add_widget(self.category_button)
        return box

    def _create_sensitivity_control(self):
        box = BoxLayout(orientation='vertical', spacing=dp(8))
        self.sensitivity_label = Label(
            text="Sensitivity: Medium",
            font_size=DEFAULT_FONT_SIZE,
            color=[0.2, 0.3, 0.5, 1],
            size_hint_y=None,
            height=dp(30))
        
        self.sensitivity_slider = Slider(
            min=0,
            max=2,
            value=1,
            step=1,
            size_hint_y=None,
            height=dp(30) if platform == 'android' else dp(30))
        self.sensitivity_slider.bind(value=self._update_sensitivity)
        
        box.add_widget(self.sensitivity_label)
        box.add_widget(self.sensitivity_slider)
        return box

    def _create_generate_button(self):
        btn = PlatformAwareRoundedButton(
            text="Generate Excuse",
            background_color=[0.4, 0.7, 0.4, 1],
            size_hint_y=None,
            height=dp(45) if platform == 'android' else dp(45))
        
        with btn.canvas.before:
            Color(0, 0, 0, 0.1)
            self.shadow = RoundedRectangle(
                pos=(btn.x-3, btn.y-3),
                size=(btn.width+6, btn.height+6),
                radius=[btn.border_radius[0] + 2])
        
        btn.bind(
            pos=self._update_shadow,
            size=self._update_shadow,
            on_release=self._navigate_to_excuse)
        return btn

    def _update_background(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def _update_shadow(self, instance, value):
        self.shadow.pos = (instance.x-3, instance.y-3)
        self.shadow.size = (instance.width+6, instance.height+6)

    def _update_category(self, category):
        self.category_button.text = category
        self.category = category
        self.category_dropdown.dismiss()

    def _update_sensitivity(self, instance, value):
        levels = ["Low", "Medium", "High"]
        self.sensitivity_label.text = f"Sensitivity: {levels[int(value)]}"
        self.sensitivity = int(value)

    def _navigate_to_excuse(self, instance):
        anim = Animation(opacity=0.7, duration=0.1)
        anim += Animation(opacity=1, duration=0.1)
        anim.start(instance)
        self.manager.current = 'excuse'

class OptimizedExcuseScreen(Screen):
    excuse_text = StringProperty("Your excuse will appear here")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._configure_background()
        self._setup_ui()

    def _configure_background(self):
        with self.canvas.before:
            Color(0.1, 0.3, 0.5, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_background)

    def _setup_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(15))
        content = self._create_content()
        main_layout.add_widget(content)
        self.add_widget(main_layout)

    def _create_content(self):
        layout = BoxLayout(orientation='vertical', spacing=dp(15))
        
        # Title with fixed height
        layout.add_widget(Label(
            text="Your Excuse",
            font_size=sp(24) if platform == 'android' else dp(24),
            bold=True,
            color=[1, 1, 1, 1],
            size_hint_y=None,
            height=dp(45)))
        
        # Settings display (new addition)
        layout.add_widget(self._create_settings_display())
        
        # Excuse Card with proportional height
        layout.add_widget(self._create_excuse_card())
        
        # Action Buttons with fixed height
        layout.add_widget(self._create_action_buttons())
        
        return layout

    def _create_settings_display(self):
        # Subtle settings display
        self.settings_label = Label(
            text="",
            font_size=sp(14) if platform == 'android' else dp(14),
            color=[1, 1, 1, 0.7],  # Semi-transparent white
            size_hint_y=None,
            height=dp(20))
        return self.settings_label

    def _create_excuse_card(self):
        # Card takes 60% of available vertical space
        card = BoxLayout(orientation='vertical', size_hint_y=0.6)
        with card.canvas.before:
            Color(1, 1, 1, 0.2)
            RoundedRectangle(size=card.size, pos=card.pos, radius=[dp(15)])
        
        self.excuse_label = Label(
            text=self.excuse_text,
            font_size=sp(20) if platform == 'android' else dp(20),
            color=[1, 1, 1, 1],
            halign='center',
            valign='middle',
            text_size=(self.width - dp(20), None),  # Fixed width for text wrapping
            padding=(dp(10), dp(10)),
            font_name='Roboto',
            markup=True
        )
        self.excuse_label.bind(size=lambda instance, value: setattr(self.excuse_label, 'text_size', (value[0], None)))
        card.add_widget(self.excuse_label)
        return card

    def _create_action_buttons(self):
        # Fixed height button container
        box = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(170))  # Fixed total height for buttons
            
        # Watermark
        box.add_widget(Label(
            text="developed by Mhmd-Aslam",
            font_size=sp(12) if platform == 'android' else dp(12),
            color=[1, 1, 1, 0.5],
            size_hint_y=None,
            height=dp(20)))
        
        # Buttons with fixed heights
        copy_btn = PlatformAwareRoundedButton(
            text="Copy to Clipboard",
            background_color=[0.5, 0.7, 0.9, 1],
            size_hint_y=None,
            height=dp(50))
        copy_btn.bind(on_release=self._copy_to_clipboard)
        box.add_widget(copy_btn)
        
        retry_btn = PlatformAwareRoundedButton(
            text="Try Again",
            background_color=[0.3, 0.5, 0.8, 1],
            size_hint_y=None,
            height=dp(50))
        retry_btn.bind(on_release=self._generate_new_excuse)
        box.add_widget(retry_btn)
        
        home_btn = PlatformAwareRoundedButton(
            text="Main Menu",
            background_color=[0.8, 0.3, 0.3, 1],
            size_hint_y=None,
            height=dp(50))
        home_btn.bind(on_release=self._return_home)
        box.add_widget(home_btn)
        
        return box

    def _copy_to_clipboard(self, instance):
        if self.excuse_label.text.strip():
            Clipboard.copy(self.excuse_label.text)
            original_text = instance.text
            instance.text = "Copied!"
            instance.background_color = [0.2, 0.8, 0.2, 1]
            Clock.schedule_once(
                lambda dt: self._reset_button(instance, original_text), 1
            )
        else:
            instance.text = "Nothing to copy!"
            instance.background_color = [0.8, 0.2, 0.2, 1]
            Clock.schedule_once(
                lambda dt: self._reset_button(instance, "Copy to Clipboard"), 1
            )

    def _reset_button(self, button, text):
        button.text = text
        button.background_color = [0.5, 0.7, 0.9, 1]

    def _update_background(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def on_enter(self):
        self._generate_new_excuse()

    def _generate_new_excuse(self, instance=None):
        anim = Animation(opacity=0, duration=0.2)
        anim += Animation(opacity=1, duration=0.2)
        anim.start(self.excuse_label)
        home_screen = self.manager.get_screen('home')
        category = home_screen.category
        sensitivity = home_screen.sensitivity
        
        levels = ["Low", "Medium", "High"]
        level = levels[sensitivity]
        
        # Update settings display
        self.settings_label.text = f"Category: {category} | Sensitivity: {level}"
        self.excuse_label.text = random.choice(excuses_data[category][level])

    def _return_home(self, instance):
        self.manager.current = 'home'

class OptimizedExcuseApp(App):
    def build(self):
        self.title = 'Excuse Generator'
        self.icon = 'assets/applogo.png'
        
        sm = ScreenManager()
        sm.add_widget(OptimizedHomeScreen(name='home'))
        sm.add_widget(OptimizedExcuseScreen(name='excuse'))
        return sm

if __name__ == "__main__":
    OptimizedExcuseApp().run()