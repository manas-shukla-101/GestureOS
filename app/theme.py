"""
Futuristic Dark Theme styling and design tokens for GestureOS.
Defined according to Design.md.
"""

PALETTE = {
    "bg": "#0B0D12",
    "surface": "#141824",
    "surface_elevated": "#1B2130",
    "cyan": "#35D9FF",
    "violet": "#8B5CF6",
    "green": "#38D996",
    "amber": "#FFB547",
    "red": "#FF5263",
    "text_main": "#F3F5FA",
    "text_muted": "#A7B0C2",
    "border": "#2A3345",
}

MAIN_STYLESHEET = f"""
QMainWindow {{
    background-color: {PALETTE['bg']};
}}

QWidget {{
    color: {PALETTE['text_main']};
    font-family: 'Segoe UI', 'SF Pro Display', -apple-system, sans-serif;
    font-size: 13px;
}}

/* Card Container */
QFrame#Card {{
    background-color: {PALETTE['surface']};
    border: 1px solid {PALETTE['border']};
    border-radius: 12px;
}}

QFrame#CardElevated {{
    background-color: {PALETTE['surface_elevated']};
    border: 1px solid {PALETTE['border']};
    border-radius: 12px;
}}

/* Navigation Sidebar */
QFrame#Sidebar {{
    background-color: {PALETTE['surface']};
    border-right: 1px solid {PALETTE['border']};
}}

/* Navigation Buttons */
QPushButton#NavButton {{
    background-color: transparent;
    color: {PALETTE['text_muted']};
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    text-align: left;
    font-size: 14px;
    font-weight: 500;
}}

QPushButton#NavButton:hover {{
    background-color: {PALETTE['surface_elevated']};
    color: {PALETTE['cyan']};
}}

QPushButton#NavButton:checked {{
    background-color: #17243B;
    color: {PALETTE['cyan']};
    border-left: 3px solid {PALETTE['cyan']};
}}

/* Primary Buttons */
QPushButton#PrimaryButton {{
    background-color: {PALETTE['cyan']};
    color: #060B14;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: bold;
}}

QPushButton#PrimaryButton:hover {{
    background-color: #63E2FF;
}}

QPushButton#PrimaryButton:pressed {{
    background-color: #1FB8DB;
}}

/* Stop / Danger Button */
QPushButton#StopButton {{
    background-color: {PALETTE['red']};
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: bold;
    letter-spacing: 0.5px;
}}

QPushButton#StopButton:hover {{
    background-color: #FF6E7C;
}}

QPushButton#StopButton:pressed {{
    background-color: #D93B4C;
}}

/* Status Pills */
QLabel#StatusPill {{
    background-color: {PALETTE['surface_elevated']};
    border: 1px solid {PALETTE['border']};
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 12px;
}}

QLabel#MetricValue {{
    font-size: 20px;
    font-weight: 700;
    color: {PALETTE['cyan']};
}}

QLabel#MetricLabel {{
    font-size: 11px;
    color: {PALETTE['text_muted']};
    text-transform: uppercase;
    letter-spacing: 1px;
}}

/* Switch / Checkbox styling */
QCheckBox {{
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid {PALETTE['border']};
    background-color: {PALETTE['surface_elevated']};
}}

QCheckBox::indicator:checked {{
    background-color: {PALETTE['cyan']};
    border: 1px solid {PALETTE['cyan']};
}}
"""

