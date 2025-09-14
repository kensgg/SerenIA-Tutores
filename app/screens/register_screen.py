import flet
from flet import (
    Container, Column, Row, Text, TextField, ElevatedButton, IconButton,
    MainAxisAlignment, CrossAxisAlignment, SnackBar, ButtonStyle,
    padding, BoxShadow, Offset, ShadowBlurStyle, border, alignment,
    GestureDetector, ScrollMode, Icons, Dropdown, dropdown
)
import asyncio
from services.tutor_service import register_tutor
from services.data_cache import DataCache

class TutorDarkMoodPalette:
    # Fondo principal
    MAIN_BACKGROUND = "#1E252D"  # Gris oscuro azulado, ideal para modo oscuro
    CARD_SURFACE = "#2A323C"     # Gris oscuro para tarjetas, sutilmente elevado
    BORDER_SUBTLE = "#3B4653"    # Gris medio para bordes discretos
    # Colores emocionales
    TRUST = "#4A90E2"            # Azul vibrante para confianza y estabilidad (botones principales)
    TRUST_HOVER = "#6AA8F7"      # Azul más claro y vivo para estados hover
    ALERT = "#E68B50"            # Naranja apagado para advertencias o alertas de ansiedad
    SUPPORT = "#5C9CE6"          # Azul claro vibrante para acciones secundarias o feedback de depresión
    URGENT = "#D16A6A"           # Rojo apagado para errores o alertas de estrés
    # Texto
    TEXT_MAIN = "#E2E8F0"        # Gris claro para texto principal, legible en fondo oscuro
    TEXT_SUBTLE = "#94A3B8"      # Gris azulado para texto secundario
    TEXT_ON_ACCENT = "#FFFFFF"   # Blanco para texto sobre fondos coloreados
    # Inputs
    INPUT_SURFACE = "#343D48"    # Gris oscuro para fondos de campos de entrada
    INPUT_EDGE = "#4B5563"       # Borde gris para inputs
    INPUT_FOCUS = "#4A90E2"      # Azul vibrante para bordes de inputs enfocados
    # Feedback
    SUCCESS_FEEDBACK = "#2DD4BF" # Verde azulado para mensajes de éxito
    ERROR_FEEDBACK = "#F87171"   # Rojo claro para errores
    WARNING_FEEDBACK = "#FBBF24" # Amarillo ámbar para advertencias
    # Sombras
    SHADOW_SOFT = "rgba(0,0,0,0.2)"  # Sombra más pronunciada para modo oscuro

class RegisterForm(Container):
    def __init__(self, page, navigate, cache: DataCache):
        super().__init__()
        self.page = page
        self.navigate = navigate
        self.cache = cache
        self.selected_group = None
        self._create_form_fields()
        self._build_ui()

    def _create_form_fields(self):
        field_style = {
            "color": TutorDarkMoodPalette.TEXT_MAIN,
            "bgcolor": TutorDarkMoodPalette.INPUT_SURFACE,
            "border_color": TutorDarkMoodPalette.INPUT_EDGE,
            "focused_border_color": TutorDarkMoodPalette.INPUT_FOCUS,
            "border_radius": 8,
            "width": 380,
            "text_size": 14,
            "cursor_color": TutorDarkMoodPalette.INPUT_FOCUS,
            "label_style": flet.TextStyle(
                color=TutorDarkMoodPalette.TEXT_SUBTLE,
                font_family="Fredoka"
            ),
            "content_padding": padding.symmetric(horizontal=16, vertical=14),
            "border_width": 1
        }
        self.full_name_field = TextField(
            label="Nombre Completo",
            hint_text="Ej. Juan Pérez López",
            **field_style
        )
        self.email_field = TextField(
            label="Email",
            hint_text="Ej. tutor@utsjr.edu.mx",
            **field_style
        )
        self.password_field = TextField(
            label="Contraseña",
            password=True,
            can_reveal_password=True,
            hint_text="Mínimo 8 caracteres",
            **field_style
        )
        self.group_dropdown = Dropdown(
            label="Grupo",
            hint_text="Selecciona un grupo",
            width=380,
            text_size=14,
            color=TutorDarkMoodPalette.TEXT_MAIN,
            bgcolor=TutorDarkMoodPalette.INPUT_SURFACE,
            border_color=TutorDarkMoodPalette.INPUT_EDGE,
            focused_border_color=TutorDarkMoodPalette.INPUT_FOCUS,
            border_radius=8,
            border_width=1,
            content_padding=padding.symmetric(horizontal=16, vertical=14),
            label_style=flet.TextStyle(
                color=TutorDarkMoodPalette.TEXT_SUBTLE,
                font_family="Fredoka"
            ),
            options=[
                dropdown.Option("DSM1SM-25ERS"),
                dropdown.Option("QFA3SV-25ERS"),
                dropdown.Option("IER01SV-24"),
                dropdown.Option("IQF03SV-25")
            ],
            on_change=self.on_group_change
        )

    def _build_ui(self):
        self.content = Column(
            controls=[
                Column([
                    Text("SERENIA",
                         size=48,
                         weight='bold',
                         color=TutorDarkMoodPalette.TRUST,
                         font_family="Fredoka",
                         text_align="center"),
                    Container(
                        width=120,
                        height=3,
                        bgcolor=TutorDarkMoodPalette.TRUST,
                        margin=flet.margin.symmetric(vertical=12)
                    ),
                ]),
                Text("Registro de Tutor",
                     size=20,
                     weight='bold',
                     color=TutorDarkMoodPalette.TEXT_MAIN,
                     font_family="Fredoka",
                     text_align="center"),
                Text("Crea tu cuenta para comenzar",
                     size=15,
                     color=TutorDarkMoodPalette.TEXT_SUBTLE,
                     font_family="Fredoka",
                     text_align="center"),
                flet.Divider(height=30, color='transparent'),
                self.full_name_field,
                flet.Divider(height=20, color='transparent'),
                self.email_field,
                flet.Divider(height=20, color='transparent'),
                Text("Grupo que impartes",
                     size=14,
                     color=TutorDarkMoodPalette.TEXT_MAIN,
                     font_family="Fredoka"),
                flet.Divider(height=8, color='transparent'),
                self.group_dropdown,
                flet.Divider(height=20, color='transparent'),
                self.password_field,
                flet.Divider(height=30, color='transparent'),
                ElevatedButton(
                    "REGISTRARSE",
                    bgcolor=TutorDarkMoodPalette.TRUST,
                    color=TutorDarkMoodPalette.TEXT_ON_ACCENT,
                    width=380,
                    height=48,
                    on_click=self.on_register_click,
                    style=ButtonStyle(
                        shape=flet.RoundedRectangleBorder(radius=8),
                        elevation=1,
                        shadow_color=TutorDarkMoodPalette.SHADOW_SOFT,
                        overlay_color=flet.Colors.with_opacity(0.1, TutorDarkMoodPalette.TRUST_HOVER),
                        animation_duration=200,
                        padding=padding.symmetric(vertical=12),
                        text_style=flet.TextStyle(
                            font_family="Fredoka",
                            weight="w600",
                            size=15,
                            letter_spacing=0.8)
                    )
                ),
                flet.Divider(height=20, color='transparent'),
                Row(
                    alignment=MainAxisAlignment.CENTER,
                    controls=[
                        Text("¿Ya tienes cuenta?",
                             color=TutorDarkMoodPalette.TEXT_SUBTLE,
                             font_family="Fredoka",
                             size=13),
                        GestureDetector(
                            content=Text(" Inicia Sesión",
                                         color=TutorDarkMoodPalette.TRUST,
                                         font_family="Fredoka",
                                         weight="w600",
                                         size=13),
                            on_tap=self.go_to_login
                        )
                    ]
                )
            ],
            spacing=0,
            alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            scroll=ScrollMode.AUTO
        )
        self.width = 440
        self.padding = 40
        self.bgcolor = TutorDarkMoodPalette.CARD_SURFACE
        self.border_radius = 16
        self.border = border.all(1, TutorDarkMoodPalette.BORDER_SUBTLE)
        self.shadow = BoxShadow(
            spread_radius=0,
            blur_radius=20,
            color=TutorDarkMoodPalette.SHADOW_SOFT,
            offset=Offset(0, 6),
            blur_style=ShadowBlurStyle.NORMAL
        )

    async def go_to_login(self, e):
        await self.navigate("login")

    def on_group_change(self, e):
        self.selected_group = self.group_dropdown.value
        self.page.update()

    async def on_register_click(self, e):
        required_fields = [
            self.full_name_field.value.strip(),
            self.email_field.value.strip(),
            self.password_field.value.strip(),
            self.selected_group
        ]
        if not all(required_fields):
            self.show_snackbar("Por favor completa todos los campos", TutorDarkMoodPalette.ERROR_FEEDBACK)
            return
        if len(self.password_field.value.strip()) < 8:
            self.show_snackbar("La contraseña debe tener al menos 8 caracteres", TutorDarkMoodPalette.ERROR_FEEDBACK)
            return
        try:
            result = await register_tutor(
                self.full_name_field.value.strip(),
                self.email_field.value.strip(),
                self.password_field.value.strip(),
                [self.selected_group]  # Pass as a list with single item
            )
            if result["success"]:
                self.show_snackbar("¡Tutor registrado exitosamente! Por favor inicia sesión.", TutorDarkMoodPalette.SUCCESS_FEEDBACK)
                self.clear_form()
                await asyncio.sleep(1.5)
                await self.navigate("login")
            else:
                error_msg = result.get("error", "Error al registrar tutor")
                self.show_snackbar(error_msg, TutorDarkMoodPalette.ERROR_FEEDBACK)
        except Exception as ex:
            self.show_snackbar(f"Error en el registro: {str(ex)}", TutorDarkMoodPalette.ERROR_FEEDBACK)

    def show_snackbar(self, message, color):
        self.page.snack_bar = SnackBar(
            content=Text(
                message,
                color=TutorDarkMoodPalette.TEXT_ON_ACCENT,
                font_family="Fredoka"
            ),
            behavior=flet.SnackBarBehavior.FLOATING,
            shape=flet.RoundedRectangleBorder(radius=8),
            bgcolor=color,
            elevation=8,
            margin=padding.all(20),
            show_close_icon=True
        )
        self.page.snack_bar.open = True
        self.page.update()

    def clear_form(self):
        self.full_name_field.value = ""
        self.email_field.value = ""
        self.password_field.value = ""
        self.group_dropdown.value = None
        self.selected_group = None
        self.page.update()

async def show_register(page: flet.Page, navigate, cache: DataCache):
    page.title = "Registro | SERENIA"
    page.horizontal_alignment = 'center'
    page.vertical_alignment = 'center'
    page.bgcolor = TutorDarkMoodPalette.MAIN_BACKGROUND
    page.fonts = {
        "Fredoka": "https://fonts.googleapis.com/css2?family=Fredoka:wght@300;400;500;600;700&display=swap"
    }
    page.theme = flet.Theme(
        color_scheme=flet.ColorScheme(
            primary=TutorDarkMoodPalette.TRUST,
            on_primary=TutorDarkMoodPalette.TEXT_ON_ACCENT,
            surface=TutorDarkMoodPalette.CARD_SURFACE,
            on_surface=TutorDarkMoodPalette.TEXT_MAIN
        ),
        text_theme=flet.TextTheme(
            body_large=flet.TextStyle(
                font_family="Fredoka",
                color=TutorDarkMoodPalette.TEXT_MAIN
            )
        )
    )
    page.add(
        Container(
            content=RegisterForm(page, navigate, cache),
            alignment=alignment.center,
            expand=True,
            padding=40,
            bgcolor=TutorDarkMoodPalette.MAIN_BACKGROUND
        )
    )
    page.update()