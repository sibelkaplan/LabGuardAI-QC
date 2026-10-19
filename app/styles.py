APP_STYLESHEET = """
QWidget {
    background: #FFFFFF;
    color: #18353A;
    font-family: "Helvetica Neue", Helvetica;
    font-size: 14px;
}
QFrame#Sidebar {
    background: #FFFFFF;
    border-right: 1px solid #DDE8E8;
}
QWidget#SidebarHost { background: #FFFFFF; }
QFrame#Card {
    background: #FFFFFF;
    border: 1px solid #DDE8E8;
    border-radius: 12px;
}
QLabel { background: transparent; color: #18353A; }
QLabel#Brand { color: #102E33; font-size: 16px; font-weight: 750; }
QLabel#BrandTag { color: #6A7C80; font-size: 11px; font-style: normal; background: transparent; }
QLabel#Sub { color: #6A7C80; font-size: 12px; }
QLabel#PageTitle { color: #102E33; font-size: 28px; font-weight: 800; background: transparent; }
QLabel#Heading { color: #0B5964; font-weight: 750; background: transparent; }
QLabel#Deep { color: #123F46; background: transparent; }
QLabel#CaptionChip { color: #123F46; background: #E5F0F1; border-radius: 8px; padding: 8px; }
QLabel#MediaWell { background: #F2F6F6; border-radius: 12px; }
QLabel#Muted { color: #5E7276; }
QLabel#Stat { font-size: 22px; font-weight: 750; color: #0B5964; }
QLabel#Banner {
    background: #FFF3D9;
    color: #5C3E06;
    border: 1px solid #E6C56E;
    border-radius: 8px;
    padding: 6px 10px;
    font-weight: 650;
}
QLabel#Warning {
    background: #FFF3D9;
    color: #5C3E06;
    border-radius: 8px;
    padding: 12px;
}
QLabel#ResultOk {
    background: #E5F0F1;
    color: #0B5964;
    border-radius: 8px;
    padding: 12px;
}
QLabel#ResultBlocked {
    background: #F8E8E8;
    color: #6D2A2A;
    border-radius: 8px;
    padding: 12px;
}
QFrame#IconCard, QLabel#IconCard {
    background: #FFFFFF;
    border: 1px solid #DDE8E8;
    border-radius: 12px;
    padding: 12px;
}
QFrame#Hero {
    background: #FFFFFF;
    border: 1px solid #D5E4E6;
    border-radius: 14px;
}
QLabel#HeroTitle {
    font-size: 16px;
    font-weight: 700;
    color: #102E33;
    background: transparent;
}
QLabel#QuietTitle {
    font-size: 14px;
    font-weight: 650;
    color: #102E33;
    background: transparent;
}
QLabel#IconBubble {
    background: #E5F0F1;
    color: #0B5964;
    border-radius: 14px;
    font-size: 14px;
    padding: 2px 8px;
}
QLabel#StepOn {
    background: #0B5964;
    color: #FFFFFF;
    border-radius: 14px;
    padding: 8px 6px;
    font-weight: 700;
}
QLabel#StepDone {
    background: #E5F0F1;
    color: #0B5964;
    border-radius: 14px;
    padding: 8px 6px;
    font-weight: 700;
}
QLabel#StepOff {
    background: #FFFFFF;
    color: #6D8286;
    border: 1px solid #DDE8E8;
    border-radius: 14px;
    padding: 8px 6px;
}
QLabel#Section {
    color: #0B5964;
    font-size: 11px;
    font-weight: 800;
    padding-top: 12px;
}
QPushButton {
    background: #FFFFFF;
    border: 1px solid #DCE7E7;
    border-radius: 8px;
    padding: 8px 12px;
    text-align: left;
}
QPushButton#Nav {
    background: transparent;
    border: 0;
    border-radius: 10px;
    padding: 8px 10px;
    font-size: 14px;
    color: #243E43;
}
QPushButton#GroupHeader {
    background: transparent;
    border: 0;
    color: #5C7579;
    font-size: 11px;
    font-weight: 750;
    padding: 6px 4px 2px 4px;
}
QPushButton#GroupHeader:checked, QPushButton#GroupHeader:hover {
    background: transparent;
    border: 0;
    color: #5C7579;
}
QPushButton#Back {
    background: transparent;
    border: 0;
    color: #0B5964;
    font-weight: 700;
    padding: 2px 4px;
}
QPushButton#Back:hover { background: #E5F0F1; border: 0; color: #0B5964; }
QWidget#TutorDock { background: transparent; }
QPushButton#Nav:hover { background: #F4FAFA; border: 0; color: #0B5964; }
QPushButton#Active:hover { background: #E5F0F1; color: #0B5964; }
QPushButton:hover { border-color: #0B5964; color: #0B5964; }
QPushButton:disabled { color: #6D8286; background: #F4F7F7; }
QPushButton#Active {
    background: #E7F3F4;
    color: #0B5964;
    border: 0;
    border-radius: 10px;
    font-weight: 650;
}
QPushButton#Primary {
    background: #0B5964;
    color: #FFFFFF;
    border: 0;
    border-radius: 20px;
    font-weight: 700;
    text-align: center;
    padding: 8px 16px;
}
QPushButton#Primary:hover { background: #08464F; color: #FFFFFF; }
QPushButton#RobotButton {
    background: #0B5964;
    color: #FFFFFF;
    border: 0;
    border-radius: 24px;
    font-weight: 700;
}
QPushButton#RobotButton:hover { background: #08464F; color: #FFFFFF; }
QLineEdit, QComboBox, QTextEdit {
    background: #FFFFFF;
    border: 1px solid #D7E3E4;
    border-radius: 7px;
    padding: 8px;
    selection-background-color: #0B5964;
    selection-color: #FFFFFF;
}
QLineEdit:focus, QComboBox:focus, QTextEdit:focus { border: 1px solid #0B5964; }
QTableWidget {
    background: #FFFFFF;
    alternate-background-color: #F4FAFA;
    border: 1px solid #DDE8E8;
    border-radius: 10px;
    gridline-color: #EAF0F0;
    selection-background-color: #E5F0F1;
    selection-color: #123F46;
}
QHeaderView::section {
    background: #EAF2F2;
    color: #345055;
    padding: 9px;
    border: 0;
    font-weight: 700;
}
QCheckBox, QRadioButton {
    background: #FFFFFF;
    border: 1px solid #DDE8E8;
    border-radius: 8px;
    padding: 6px 8px;
    spacing: 8px;
}
QScrollArea, QScrollArea > QWidget > QWidget { border: 0; background: #FFFFFF; }
QScrollArea#SidebarScroll, QScrollArea#SidebarScroll > QWidget, QScrollArea#SidebarScroll > QWidget > QWidget { background: #FFFFFF; }
QFrame#WelcomeBanner { background: transparent; border: 0; }
QFrame#HeroShell {
    background: #FFFFFF;
    border: 1px solid #DDE8E8;
    border-radius: 16px;
}
QLabel#WelcomeKicker {
    color: #6A7C80;
    font-size: 11px;
    font-weight: 700;
    background: transparent;
}
QLabel#WelcomeTitle { color: #102E33; font-size: 36px; font-weight: 800; background: transparent; }
QFrame#DemoStrip {
    background: #FFF3D9;
    border: 1px solid #E6C56E;
    border-radius: 10px;
}
QFrame#DemoStrip QLabel { color: #5C3E06; background: transparent; }
QPushButton#SideChoice { text-align: left; font-weight: 650; }
QLabel#WelcomeSub { color: #5E7276; font-size: 15px; background: transparent; }
QLabel#HomeSection { color: #102E33; font-size: 16px; font-weight: 750; background: transparent; }
QLabel#DemoName { color: #0B5964; font-size: 14px; font-weight: 750; background: transparent; }
QFrame#HomePanel {
    background: #FFFFFF;
    border: 1px solid #DDE8E8;
    border-radius: 14px;
}
QFrame#FeaturePetrol {
    background: #0B5964;
    border: 1px solid #08464F;
    border-radius: 14px;
}
QFrame#FeaturePetrol QLabel { color: #FFFFFF; background: transparent; }
QFrame#FeaturePetrol QLabel#Muted { color: #D7EBED; background: transparent; }
QFrame#FeatureGold {
    background: #F8F1DC;
    border: 1px solid #E4D3A8;
    border-radius: 14px;
}
QFrame#FeatureBlue {
    background: #E7F3F8;
    border: 1px solid #D0E4EE;
    border-radius: 14px;
}
QFrame#FeatureGold QLabel#HeroTitle, QFrame#FeatureBlue QLabel#HeroTitle {
    color: #0B5964;
    background: transparent;
}
QFrame#QuickCard {
    background: #FFFFFF;
    border: 1px solid #DDE8E8;
    border-radius: 14px;
}
QFrame#FeaturePetrol QPushButton#OpenLite {
    background: #E5F0F1;
    color: #0B5964;
    border: 0;
    border-radius: 8px;
    padding: 6px 12px;
    font-weight: 700;
    text-align: center;
}
QFrame#FeatureGold QPushButton#OpenLite, QFrame#FeatureBlue QPushButton#OpenLite {
    background: #0B5964;
    color: #FFFFFF;
    border: 0;
    border-radius: 8px;
    padding: 6px 12px;
    font-weight: 700;
    text-align: center;
}
QFrame#FeaturePetrol QPushButton#OpenLite:hover { background: #FFFFFF; color: #0B5964; }
QFrame#FeatureGold QPushButton#OpenLite:hover, QFrame#FeatureBlue QPushButton#OpenLite:hover {
    background: #08464F;
    color: #FFFFFF;
}
QFrame#QuickCard QPushButton#OpenLite {
    background: transparent;
    border: 0;
    color: #0B5964;
    font-weight: 700;
    padding: 0px 2px 2px 2px;
    text-align: left;
}
QFrame#QuickCard QPushButton#OpenLite:hover { background: transparent; color: #08464F; }
QLineEdit#HomeSearch {
    background: #F7FAFA;
    border: 1px solid #E3EEEE;
    border-radius: 22px;
    padding: 8px 16px;
    font-size: 14px;
}
QPushButton#ListRow {
    background: #FFFFFF;
    border: 1px solid #E6EEEE;
    border-radius: 8px;
    padding: 7px 8px;
    text-align: left;
}
QPushButton#ListRow:hover { border-color: #0B5964; color: #0B5964; }
QPushButton#HelpLink {
    background: #FFFFFF;
    border: 1px solid #D5E3E4;
    border-radius: 20px;
    padding: 8px 16px;
    text-align: center;
    color: #102E33;
    font-weight: 650;
}
QFrame#Canvas { background: #FFFFFF; border: 0; }
QFrame#FeatureCard {
    background: #FFFFFF;
    border: 1px solid #E3EEEE;
    border-radius: 18px;
}
QFrame#FeatureCard QLabel { background: transparent; }
QFrame#FeatureCard QLabel#HeroTitle { color: #102E33; background: transparent; }
QFrame#FeatureCard QPushButton#OpenLite, QFrame#QuickCard QPushButton#OpenLite {
    background: #F4F7F8;
    color: #0B5964;
    border: 0;
    border-radius: 16px;
    padding: 0px;
    min-width: 32px;
    max-width: 32px;
    min-height: 32px;
    max-height: 32px;
    font-weight: 700;
    text-align: center;
}
"""

SURFACE = {
    "laboratory": {"canvas": "#FFFFFF", "sidebar": "#FFFFFF", "card": "#FFFFFF"},
    "white": {"canvas": "#FFFFFF", "sidebar": "#FFFFFF", "card": "#F2F6F6"},
    "midnight": {"canvas": "#000000", "sidebar": "#080D12", "card": "#080D12"},
}

_WHITE_SHEET = """
QWidget { background: #FFFFFF; color: #18353A; }
QFrame#Canvas, QScrollArea, QScrollArea > QWidget > QWidget { background: #FFFFFF; }
QScrollArea#SidebarScroll, QScrollArea#SidebarScroll > QWidget > QWidget, QFrame#Sidebar { background: #FFFFFF; }
QFrame#Card, QFrame#HeroShell, QFrame#HomePanel, QFrame#QuickCard, QFrame#FeatureCard, QFrame#IconCard, QLabel#IconCard {
    background: #F2F6F6;
    border: 1px solid #D5E3E4;
}
QLineEdit, QComboBox, QTextEdit, QTableWidget, QPushButton, QCheckBox, QRadioButton { background: #FFFFFF; }
QLineEdit#HomeSearch, QPushButton#HelpLink, QPushButton#ListRow { background: #FFFFFF; }
"""

_MIDNIGHT_SHEET = """
QWidget { background: #000000; color: #F4F7F7; }
QFrame#Canvas { background: #000000; border: 0; }
QScrollArea, QScrollArea > QWidget > QWidget { background: #000000; color: #F4F7F7; }
QFrame#Sidebar, QWidget#SidebarHost, QScrollArea#SidebarScroll, QScrollArea#SidebarScroll > QWidget, QScrollArea#SidebarScroll > QWidget > QWidget { background: #080D12; color: #F4F7F7; }
QFrame#Card, QFrame#HeroShell, QFrame#HomePanel, QFrame#QuickCard, QFrame#FeatureCard, QFrame#FeaturePetrol, QFrame#FeatureGold, QFrame#FeatureBlue, QFrame#IconCard, QLabel#IconCard, QFrame#Hero {
    background: #080D12;
    color: #F4F7F7;
    border: 1px solid #1C3338;
}
QFrame#FeatureCard { border: 1px solid #1C3338; }
QLabel { background: transparent; color: #F4F7F7; }
QLabel#Brand, QLabel#WelcomeTitle, QLabel#HomeSection, QLabel#Heading, QLabel#PageTitle, QLabel#HeroTitle, QLabel#QuietTitle, QLabel#Stat, QLabel#Deep {
    color: #E7F4F5;
    background: transparent;
}
QLabel#WelcomeKicker, QLabel#BrandTag, QLabel#Section { color: #A8C0C4; background: transparent; }
QLabel#Muted, QLabel#Sub, QLabel#WelcomeSub { color: #A8C0C4; background: transparent; }
QLabel#Warning, QLabel#Banner { background: #3A3424; color: #F3E6C4; }
QFrame#DemoStrip { background: #3A3424; border: 1px solid #8A6A2F; }
QFrame#DemoStrip QLabel, QFrame#DemoStrip QLabel#DemoName { color: #F3E6C4; background: transparent; }
QLabel#ResultBlocked { background: #3A1C1C; color: #F6D0D0; }
QLabel#ResultOk, QLabel#CaptionChip, QLabel#IconBubble, QLabel#StepDone { background: #102026; color: #E7F4F5; }
QLabel#MediaWell { background: #101820; }
QLineEdit, QComboBox, QTextEdit, QTableWidget, QLineEdit#HomeSearch {
    background: #080D12;
    color: #F4F7F7;
    border: 1px solid #1C3338;
    selection-background-color: #0B5964;
    selection-color: #FFFFFF;
}
QPushButton, QCheckBox, QRadioButton {
    background: #101820;
    color: #F4F7F7;
    border: 1px solid #1C3338;
}
QPushButton#Nav { background: transparent; color: #F4F7F7; border: 0; }
QPushButton#Nav:hover { background: #102026; color: #FFFFFF; border: 0; }
QPushButton#Active, QPushButton#Primary, QPushButton#RobotButton, QFrame#FeatureCard QPushButton#OpenLite, QFrame#FeatureGold QPushButton#OpenLite, QFrame#FeatureBlue QPushButton#OpenLite {
    background: #0B5964;
    color: #FFFFFF;
    border: 1px solid #0B5964;
}
QPushButton#GroupHeader, QPushButton#GroupHeader:checked, QPushButton#GroupHeader:hover { color: #A8C0C4; background: transparent; border: 0; }
QPushButton#HelpLink, QPushButton#ListRow { background: #101820; color: #E7F4F5; border: 1px solid #1C3338; }
QHeaderView::section { background: #101820; color: #E7F4F5; }
QFrame#FeaturePetrol QLabel, QFrame#FeatureGold QLabel, QFrame#FeatureBlue QLabel, QFrame#FeatureCard QLabel { color: #F4F7F7; background: transparent; }
QFrame#FeatureCard QLabel#Muted, QFrame#FeaturePetrol QLabel#Muted { color: #A8C0C4; }
"""


def stylesheet(theme: str) -> str:
    """Three painted surfaces. The choice is not stored in the chemical database."""
    if theme == "white":
        return APP_STYLESHEET + _WHITE_SHEET
    if theme == "midnight":
        return APP_STYLESHEET + _MIDNIGHT_SHEET
    return APP_STYLESHEET
