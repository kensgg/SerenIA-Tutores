import flet
from flet import (
    Container, Column, Row, Text, TextField, ElevatedButton, GestureDetector,
    MainAxisAlignment, CrossAxisAlignment, SnackBar, ButtonStyle, padding,
    BoxShadow, Offset, ShadowBlurStyle, border, alignment
)
import asyncio
import re
from datetime import datetime
from services.tutor_service import login_tutor, register_tutor
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

class LoginForm(Container):
    def __init__(self, page, navigate, cache: DataCache):
        super().__init__()
        self.page = page
        self.navigate = navigate
        self.cache = cache
        form_width = 400  # Ancho fijo para pantallas de 14.6 a 24 pulgadas
        field_style = {
            "color": TutorDarkMoodPalette.TEXT_MAIN,
            "bgcolor": TutorDarkMoodPalette.INPUT_SURFACE,
            "border_color": TutorDarkMoodPalette.INPUT_EDGE,
            "focused_border_color": TutorDarkMoodPalette.INPUT_FOCUS,
            "border_radius": 8,
            "width": form_width - 40,  # Ajustar al ancho del contenedor menos padding
            "text_size": 14,
            "cursor_color": TutorDarkMoodPalette.INPUT_FOCUS,
            "label_style": flet.TextStyle(color=TutorDarkMoodPalette.TEXT_SUBTLE, font_family="Fredoka"),
            "content_padding": padding.symmetric(horizontal=16, vertical=14),
            "border_width": 1
        }
        self.email_field = TextField(
            label="Email",
            hint_text="Ej. tutor@utsjr.edu.mx",
            **field_style
        )
        self.password_field = TextField(
            label="Contraseña",
            password=True,
            can_reveal_password=True,
            hint_text="Ingresa tu contraseña",
            **field_style
        )
        self.error_text = Text(
            value="",
            color=TutorDarkMoodPalette.ERROR_FEEDBACK,
            size=13,
            font_family="Fredoka",
            text_align="center",
            visible=False
        )
        self.content = Column(
            controls=[
                Column([
                    Text("SERENIA", size=48, weight='bold', color=TutorDarkMoodPalette.TRUST,
                         font_family="Fredoka", text_align="center"),
                    Container(width=120, height=3, bgcolor=TutorDarkMoodPalette.TRUST,
                              margin=flet.margin.symmetric(vertical=12)),
                ]),
                Text("Para Tutores", size=20, weight='bold',
                     color=TutorDarkMoodPalette.TEXT_MAIN, font_family="Fredoka", text_align="center"),
                Text("Ingresa tus credenciales para continuar", size=15,
                     color=TutorDarkMoodPalette.TEXT_SUBTLE, font_family="Fredoka", text_align="center"),
                flet.Divider(height=30, color='transparent'),
                self.email_field,
                flet.Divider(height=20, color='transparent'),
                self.password_field,
                flet.Divider(height=10, color='transparent'),
                self.error_text,
                flet.Divider(height=20, color='transparent'),
                ElevatedButton(
                    "INICIAR SESIÓN",
                    bgcolor=TutorDarkMoodPalette.TRUST,
                    color=TutorDarkMoodPalette.TEXT_ON_ACCENT,
                    width=form_width - 40,
                    height=48,
                    on_click=self.on_sign_in_click,
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
                            letter_spacing=0.8
                        )
                    )
                ),
                flet.Divider(height=20, color='transparent'),
                Container(
                    content=Row(
                        alignment=MainAxisAlignment.CENTER,
                        controls=[
                            Text("¿No tienes cuenta?", color=TutorDarkMoodPalette.TEXT_SUBTLE,
                                 font_family="Fredoka", size=13),
                            GestureDetector(
                                content=Text(" Regístrate", color=TutorDarkMoodPalette.TRUST,
                                             font_family="Fredoka", weight="w600", size=13),
                                on_tap=self.go_to_register,
                                mouse_cursor=flet.MouseCursor.CLICK
                            )
                        ],
                        spacing=2
                    ),
                    padding=padding.all(20)
                )
            ],
            spacing=0,
            alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER
        )
        self.width = form_width
        self.padding = 40
        self.bgcolor = TutorDarkMoodPalette.CARD_SURFACE
        self.border_radius = 16
        self.border = flet.border.all(1, TutorDarkMoodPalette.BORDER_SUBTLE)
        self.shadow = BoxShadow(
            spread_radius=0,
            blur_radius=20,
            color=TutorDarkMoodPalette.SHADOW_SOFT,
            offset=Offset(0, 6),
            blur_style=ShadowBlurStyle.NORMAL
        )

    async def go_to_register(self, e):
        self.error_text.value = ""
        self.error_text.visible = False
        await self.navigate("register")

    async def on_sign_in_click(self, e):
        email = self.email_field.value.strip().lower()
        password = self.password_field.value.strip()
        self.error_text.value = ""
        self.error_text.visible = False

        if not email or not password:
            self.error_text.value = "Por favor completa todos los campos"
            self.error_text.visible = True
            self.page.update()
            return
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            self.error_text.value = "Formato de correo inválido"
            self.error_text.visible = True
            self.page.update()
            return
        try:
            tutor_data = await login_tutor(email, password)
            if tutor_data:
                self.show_snackbar("¡Inicio de sesión exitoso!", TutorDarkMoodPalette.SUCCESS_FEEDBACK)
                await asyncio.sleep(1)
                await self.navigate("dashboard", tutor_data)
            else:
                self.error_text.value = "Correo o contraseña incorrectos"
                self.error_text.visible = True
                self.page.update()
        except Exception as ex:
            error_msg = str(ex).lower()
            if "no existe tutor con email" in error_msg:
                self.error_text.value = "No existe un tutor con ese correo"
            elif "contraseña incorrecta" in error_msg:
                self.error_text.value = "Contraseña incorrecta"
            else:
                self.error_text.value = f"Error en el inicio de sesión: {str(ex)}"
            self.error_text.visible = True
            self.page.update()

    def show_snackbar(self, message, color):
        if self.page:
            self.page.snack_bar = SnackBar(
                content=Text(message, color=TutorDarkMoodPalette.TEXT_ON_ACCENT, font_family="Fredoka"),
                behavior=flet.SnackBarBehavior.FLOATING,
                shape=flet.RoundedRectangleBorder(radius=8),
                bgcolor=color,
                elevation=8,
                margin=padding.all(20),
                show_close_icon=True
            )
            self.page.snack_bar.open = True
            self.page.update()

async def show_login(page: flet.Page, navigate, cache: DataCache):
    page.title = "Login | SERENIA"
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
    page.controls.clear()
    page.add(
        Container(
            content=LoginForm(page, navigate, cache),
            alignment=alignment.center,
            expand=True,
            padding=40,
            bgcolor=TutorDarkMoodPalette.MAIN_BACKGROUND
        )
    )
    page.update()