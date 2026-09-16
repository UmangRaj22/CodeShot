from django import forms
from pygments.styles import get_all_styles

STYLE_CHOICES = sorted([(s, s) for s in list(get_all_styles())])

FONT_CHOICES = [
    ('Consolas', 'Consolas'),
    ('Courier New', 'Courier New'),
    ('Monospace', 'Monospace'), 
    ('Fira Code', 'Fira Code'),
    ('Source Code Pro', 'Source Code Pro'),
    ('Ubuntu Mono', 'Ubuntu Mono'),
    ('Inconsolata', 'Inconsolata'),
    ('JetBrains Mono', 'JetBrains Mono'),
    ('Menlo', 'Menlo'),
    ('Monaco', 'Monaco'),
]

LANG_CHOICES = [
    ('python', 'Python'),
    ('javascript', 'JavaScript'),   
    ('java', 'Java'),
    ('csharp', 'C#'),
    ('cpp', 'C++'),
    ('ruby', 'Ruby'),
    ('go', 'Go'),
    ('php', 'PHP'),
    ('swift', 'Swift'),
    ('kotlin', 'Kotlin'),
    ('typescript', 'TypeScript'),
    ('html', 'HTML'),
    ('css', 'CSS'),
    ('bash', 'Bash'),
    ('rust', 'Rust'),
    ('dart', 'Dart'),
    ('scala', 'Scala'),
    ('perl', 'Perl'),
    ('lua', 'Lua'),
]

class CodeForm(forms.Form):
    code = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'code-editor', 
            'placeholder': 'Paste your code here...'
        }),
        initial= "def hello_world():\n    print('Welcome to CodeShot! Write. Snap. Share beautiful code.')"
        )
    language = forms.ChoiceField(choices=LANG_CHOICES, initial='Python', widget=forms.Select(attrs={'class': 'form-select'}))
    theme = forms.ChoiceField(choices=STYLE_CHOICES, initial='Monokai', widget=forms.Select(attrs={'class': 'form-select'}))
    font = forms.ChoiceField(choices=FONT_CHOICES, initial='Consolas', widget=forms.Select(attrs={'class': 'form-select'}))
    
    
    line_numbers = forms.BooleanField(
        required=False, initial=True, 
        widget=forms.CheckboxInput(attrs={'class': 'toggle-checkbox'}))
    mac_buttons = forms.BooleanField(
        required=False, initial=True, 
        widget=forms.CheckboxInput(attrs={'class': 'toggle-checkbox'}))
    background_gradient = forms.BooleanField(
        required=False, initial=True, 
        widget=forms.CheckboxInput(attrs={'class': 'toggle-checkbox'}))
    watermark = forms.BooleanField(
        required=False, initial=False, 
        widget=forms.CheckboxInput(attrs={'class': 'toggle-checkbox'}))
    watermark_text = forms.CharField(
        required=False, initial='Made with CodeShot!', 
        widget=forms.TextInput(attrs={'class': 'form-input'}))
    
    padding = forms.IntegerField(
        min_value=20, max_value=100, initial=60,
        widget=forms.NumberInput(attrs={'type': 'range', 'class': 'slider', 'min': '20', 'max': '100'})
    )