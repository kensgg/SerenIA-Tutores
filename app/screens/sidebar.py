from flet import *
import logging
from screens.dashboard_content import DashboardContent
from screens.filter_content import FilterContent
from screens.profile_content import ProfileContent
from services.data_cache import DataCache

# Suppress Flet and Matplotlib logs
logging.getLogger('flet').setLevel(logging.WARNING)
logging.getLogger('matplotlib').setLevel(logging.WARNING)

class TutorDarkMoodPalette:
    MAIN_BACKGROUND = "#1E252D"
    CARD_SURFACE = "#2A323C"
    BORDER_SUBTLE = "#3B4653"
    TRUST = "#4A90E2"
    TRUST_HOVER = "#6AA8F7"
    ALERT = "#E68B50"
    SUPPORT = "#5C9CE6"
    URGENT = "#D16A6A"
    TEXT_MAIN = "#E2E8F0"
    TEXT_SUBTLE = "#94A3B8"
    TEXT_ON_ACCENT = "#FFFFFF"
    INPUT_SURFACE = "#343D48"
    INPUT_EDGE = "#4B5563"
    INPUT_FOCUS = "#4A90E2"
    SUCCESS_FEEDBACK = "#2DD4BF"
    ERROR_FEEDBACK = "#F87171"
    WARNING_FEEDBACK = "#FBBF24"
    SHADOW_SOFT = "rgba(0,0,0,0.2)"

class SidebarButton(Container):
    def __init__(self, label, icon, selected=False, on_click=None):
        super().__init__()
        self.label = label
        self.selected = selected
        self.on_click = on_click
        self.content = Row([
            IconButton(
                icon=icon,
                icon_size=20,
                icon_color=TutorDarkMoodPalette.TRUST if selected else TutorDarkMoodPalette.TEXT_SUBTLE,
                style=ButtonStyle(padding=0)
            ),
            Text(
                label,
                size=14,
                color=TutorDarkMoodPalette.TRUST if selected else TutorDarkMoodPalette.TEXT_SUBTLE,
                weight='w600',
                font_family="Fredoka"
            )
        ], spacing=12)
        self.padding = padding.symmetric(horizontal=16, vertical=12)
        self.border_radius = border_radius.all(6)
        self.bgcolor = "transparent"
        self.on_click = on_click

class Sidebar(Container):
    def __init__(self, page, tutor_data, on_page_change, cache: DataCache):
        super().__init__()
        self.page = page
        self.on_page_change = on_page_change
        self.cache = cache
        full_name = tutor_data.get("full_name", "Tutor")
        email = tutor_data.get("email", "Sin correo")
        initials = "".join(word[0].upper() for word in full_name.split()[:2]) if full_name != "Tutor" else "TU"
        self.buttons = [
            SidebarButton('Dashboard', Icons.DASHBOARD, selected=True, on_click=self.on_button_click),
            SidebarButton('Filtrado', Icons.FILTER_ALT, selected=False, on_click=self.on_button_click),
            SidebarButton('Config', Icons.SETTINGS, selected=False, on_click=self.on_button_click),
            SidebarButton('Actualizar Contenido', Icons.REFRESH, selected=False, on_click=self.on_refresh_cache)
        ]
        self.content = Column(
            controls=[
                Container(
                    content=Column(
                        controls=[
                            Container(
                                content=Container(
                                    content=Text(
                                        initials,
                                        size=32,
                                        color=TutorDarkMoodPalette.TEXT_ON_ACCENT,
                                        weight='w700',
                                        font_family="Fredoka",
                                        text_align="center"
                                    ),
                                    width=80,
                                    height=80,
                                    bgcolor=TutorDarkMoodPalette.TRUST,
                                    border_radius=360,
                                    alignment=alignment.center
                                ),
                                border=border.all(1, TutorDarkMoodPalette.TRUST_HOVER),
                                border_radius=360,
                                padding=3
                            ),
                            Text(
                                full_name,
                                color=TutorDarkMoodPalette.TEXT_MAIN,
                                size=18,
                                weight='w700',
                                font_family="Fredoka"
                            ),
                            Text(
                                email,
                                color=TutorDarkMoodPalette.TEXT_SUBTLE,
                                size=14,
                                weight='w500',
                                font_family="Fredoka"
                            ),
                            Divider(height=20, color=TutorDarkMoodPalette.BORDER_SUBTLE)
                        ],
                        spacing=8,
                        horizontal_alignment=CrossAxisAlignment.CENTER
                    ),
                    padding=padding.only(top=40, bottom=20, left=16, right=16),
                    alignment=alignment.center
                ),
                Divider(color=TutorDarkMoodPalette.BORDER_SUBTLE, height=1),
                Container(
                    content=Column(
                        controls=self.buttons,
                        spacing=4
                    ),
                    padding=padding.all(12)
                )
            ],
            alignment=MainAxisAlignment.START,
            spacing=0
        )
        self.width = 220
        self.bgcolor = TutorDarkMoodPalette.CARD_SURFACE
        self.border = border.all(1, TutorDarkMoodPalette.BORDER_SUBTLE)
        self.border_radius = 16
        self.shadow = BoxShadow(
            spread_radius=0,
            blur_radius=20,
            color=TutorDarkMoodPalette.SHADOW_SOFT,
            offset=Offset(0, 6),
            blur_style=ShadowBlurStyle.NORMAL
        )

    async def on_button_click(self, e):
        clicked_button = None
        for button in self.buttons:
            if e.control in (button.content.controls[0], button.content) or button == e.control:
                clicked_button = button
                break
        if clicked_button and clicked_button.label != "Actualizar Caché":
            for btn in self.buttons:
                btn.selected = (btn == clicked_button)
                btn.bgcolor = "transparent"
                btn.content.controls[0].icon_color = TutorDarkMoodPalette.TRUST if btn.selected else TutorDarkMoodPalette.TEXT_SUBTLE
                btn.content.controls[1].color = TutorDarkMoodPalette.TRUST if btn.selected else TutorDarkMoodPalette.TEXT_SUBTLE
                btn.update()
            if self.on_page_change:
                await self.on_page_change(clicked_button.label)

    async def on_refresh_cache(self, e):
        try:
            await self.cache.load_all_data()
            self.show_snackbar("Caché actualizado exitosamente", TutorDarkMoodPalette.SUCCESS_FEEDBACK)
        except Exception as ex:
            self.show_snackbar(f"Error al actualizar caché: {str(ex)}", TutorDarkMoodPalette.ERROR_FEEDBACK)

    def show_snackbar(self, message, color):
        self.page.snack_bar = SnackBar(
            content=Text(
                message,
                color=TutorDarkMoodPalette.TEXT_ON_ACCENT,
                font_family="Fredoka"
            ),
            behavior=SnackBarBehavior.FLOATING,
            shape=RoundedRectangleBorder(radius=8),
            bgcolor=color,
            elevation=8,
            margin=padding.all(20),
            show_close_icon=True
        )
        self.page.snack_bar.open = True
        self.page.update()

class DashboardTemplate(Container):
    def __init__(self, page, tutor_data, on_group_select, cache: DataCache):
        super().__init__()
        self.page = page
        self.tutor_data = tutor_data
        self.on_group_select = on_group_select
        self.cache = cache
        self.current_page = "Dashboard"
        self.selected_group = tutor_data.get("groups", [])[0] if tutor_data.get("groups") else None
        self.initializing = False
        self.content_container = Container(
            content=Column(
                controls=[
                    DashboardContent(
                        page,
                        tutor_data,
                        selected_group=self.selected_group,
                        on_group_change=self.on_group_select_wrapper,
                        cache=cache
                    )
                ],
                scroll="auto",
                expand=True
            ),
            width=1012,
            bgcolor=TutorDarkMoodPalette.CARD_SURFACE,
            border=border.all(1, TutorDarkMoodPalette.BORDER_SUBTLE),
            border_radius=16,
            padding=20,
            expand=True,
            shadow=BoxShadow(
                spread_radius=0,
                blur_radius=20,
                color=TutorDarkMoodPalette.SHADOW_SOFT,
                offset=Offset(0, 6),
                blur_style=ShadowBlurStyle.NORMAL
            )
        )
        self.sidebar = Sidebar(page, tutor_data, on_page_change=self.on_page_change, cache=cache)
        self.content = Row(
            controls=[self.sidebar, self.content_container],
            alignment=MainAxisAlignment.CENTER,
            spacing=20
        )
        self.bgcolor = TutorDarkMoodPalette.MAIN_BACKGROUND
        self.expand = True
        self.padding = padding.only(left=20, right=20, top=20, bottom=20)

    async def initialize_content(self):
        if isinstance(self.content_container.content, Column):
            dashboard_content = self.content_container.content.controls[0]
            if isinstance(dashboard_content, DashboardContent):
                await dashboard_content.initialize()
        if self.page:
            self.page.update()

    async def on_group_select_wrapper(self, selected_group, tutor_data=None):
        if self.initializing:
            return
        self.initializing = True
        try:
            self.selected_group = selected_group
            if tutor_data:
                self.tutor_data = tutor_data
            if self.current_page == "Filtrado":
                if isinstance(self.content_container.content, Column):
                    current_content = self.content_container.content.controls[0]
                    if isinstance(current_content, FilterContent):
                        await current_content.update_group(selected_group)
                    else:
                        new_content = FilterContent(
                            self.page,
                            self.tutor_data,
                            selected_group=selected_group,
                            on_group_change=self.on_group_select_wrapper,
                            cache=self.cache
                        )
                        await new_content.initialize()
                        self.content_container.content.controls = [new_content]
            elif self.current_page == "Dashboard":
                new_content = DashboardContent(
                    self.page,
                    self.tutor_data,
                    selected_group=selected_group,
                    on_group_change=self.on_group_select_wrapper,
                    cache=self.cache
                )
                await new_content.initialize()
                self.content_container.content.controls = [new_content]
            elif self.current_page == "Config":
                if isinstance(self.content_container.content, Column) and isinstance(self.content_container.content.controls[0], ProfileContent):
                    current_content = self.content_container.content.controls[0]
                    current_content.groups = self.tutor_data.get('groups', [])
                    current_content.groups_table.rows = [current_content.create_group_row(group) for group in current_content.groups]
                    current_content.selected_group = selected_group
                    await current_content.initialize()
                else:
                    new_content = ProfileContent(
                        self.page,
                        self.tutor_data,
                        on_group_change=self.on_group_select_wrapper,
                        cache=self.cache
                    )
                    await new_content.initialize()
                    self.content_container.content.controls = [new_content]
            if self.page:
                self.page.update()
            if self.on_group_select:
                await self.on_group_select(selected_group)
        finally:
            self.initializing = False

    async def on_page_change(self, page_label):
        self.current_page = page_label
        if page_label == "Dashboard":
            new_content = DashboardContent(
                self.page,
                self.tutor_data,
                selected_group=self.selected_group,
                on_group_change=self.on_group_select_wrapper,
                cache=self.cache
            )
            await new_content.initialize()
        elif page_label == "Filtrado":
            new_content = FilterContent(
                self.page,
                self.tutor_data,
                selected_group=self.selected_group,
                on_group_change=self.on_group_select_wrapper,
                cache=self.cache
            )
            await new_content.initialize()
        elif page_label == "Config":
            new_content = ProfileContent(
                self.page,
                self.tutor_data,
                on_group_change=self.on_group_select_wrapper,
                cache=self.cache
            )
            await new_content.initialize()
        else:
            new_content = Column(
                controls=[
                    Text(
                        "Página " + page_label + " en construcción",
                        color=TutorDarkMoodPalette.TEXT_MAIN,
                        size=24,
                        weight='w700',
                        font_family="Fredoka",
                        text_align="center"
                    ),
                    Text(
                        "¡Pronto estará disponible!",
                        color=TutorDarkMoodPalette.TEXT_SUBTLE,
                        size=16,
                        font_family="Fredoka",
                        text_align="center"
                    )
                ],
                alignment=MainAxisAlignment.CENTER,
                horizontal_alignment=CrossAxisAlignment.CENTER,
                expand=True,
                width=1012
            )
        await self.update_content(new_content)

    async def update_content(self, new_content):
        self.content_container.content.controls = [new_content]
        if self.page:
            self.page.update()

async def show_dashboard_template(page: Page, tutor_data, on_group_select, cache: DataCache):
    if not tutor_data or not isinstance(tutor_data, dict):
        page.controls.clear()
        page.add(
            Column(
                controls=[
                    Text(
                        "Error: Datos de tutor no válidos",
                        color=TutorDarkMoodPalette.ERROR_FEEDBACK,
                        size=24,
                        weight='w700',
                        font_family="Fredoka",
                        text_align="center"
                    )
                ],
                alignment=MainAxisAlignment.CENTER,
                horizontal_alignment=CrossAxisAlignment.CENTER
            )
        )
        page.update()
        return None
    page.title = "Dashboard | SERENIA"
    page.horizontal_alignment = 'center'
    page.vertical_alignment = 'center'
    page.bgcolor = TutorDarkMoodPalette.MAIN_BACKGROUND
    page.fonts = {
        "Fredoka": "https://fonts.googleapis.com/css2?family=Fredoka:wght@300;400;500;600;700&display=swap"
    }
    page.theme = Theme(
        color_scheme=ColorScheme(
            primary=TutorDarkMoodPalette.TRUST,
            on_primary=TutorDarkMoodPalette.TEXT_ON_ACCENT,
            surface=TutorDarkMoodPalette.CARD_SURFACE,
            on_surface=TutorDarkMoodPalette.TEXT_MAIN
        ),
        text_theme=TextTheme(
            body_large=TextStyle(
                font_family="Fredoka",
                color=TutorDarkMoodPalette.TEXT_MAIN
            )
        )
    )
    page.controls.clear()
    dashboard_template = DashboardTemplate(page, tutor_data, on_group_select, cache)
    page.add(dashboard_template)
    await dashboard_template.initialize_content()
    page.update()
    return dashboard_template
