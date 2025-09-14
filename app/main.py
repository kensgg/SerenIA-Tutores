import flet
from flet import Page, Text
import logging
from screens.login_screen import show_login
from screens.register_screen import show_register
from screens.sidebar import show_dashboard_template
from screens.filter_content import FilterContent
from services.data_cache import DataCache

# Configurar logging para minimizar mensajes en consola
logging.basicConfig(level=logging.WARNING)
logging.getLogger('flet').setLevel(logging.WARNING)
logging.getLogger('matplotlib').setLevel(logging.WARNING)
logging.getLogger().setLevel(logging.WARNING)  # Nivel global

# Punto de entrada principal para la aplicación SerenIA
async def main(page: Page):
    page.title = "SERENIA"
    page.horizontal_alignment = 'center'
    page.vertical_alignment = 'center'
    page.bgcolor = "#1E252D"  # Usar color de fondo consistente con el tema
    page.fonts = {
        "Fredoka": "https://fonts.googleapis.com/css2?family=Fredoka:wght@300;400;500;600;700&display=swap"
    }

    # Inicializar caché
    cache = DataCache()
    logged_in = False
    tutor_data = None
    dashboard_template = None
    selected_group = None
    group_change_in_progress = False

    async def on_group_select(group):
        nonlocal dashboard_template, tutor_data, selected_group, group_change_in_progress
        if group_change_in_progress:
            return
        group_change_in_progress = True
        try:
            selected_group = group
            if dashboard_template and tutor_data:
                await dashboard_template.on_group_select_wrapper(group)
            page.update()
        except Exception as e:
            page.controls.clear()
            page.add(
                Text(
                    f"Error al seleccionar grupo: {str(e)}",
                    color="#F87171",
                    size=20,
                    font_family="Fredoka"
                )
            )
            page.update()
        finally:
            group_change_in_progress = False

    async def navigate(route, data=None):
        nonlocal logged_in, tutor_data, dashboard_template, selected_group
        page.controls.clear()
        if route == "login":
            await show_login(page, navigate, cache)
        elif route == "register":
            await show_register(page, navigate, cache)
        elif route == "dashboard":
            if not data or not isinstance(data, dict):
                await navigate("login")
                return
            logged_in = True
            tutor_data = data
            selected_group = tutor_data.get("groups", [None])[0]
            try:
                dashboard_template = await show_dashboard_template(page, tutor_data, on_group_select, cache)
            except Exception as e:
                page.controls.clear()
                page.add(
                    Text(
                        f"Error al cargar el dashboard: {str(e)}",
                        color="#F87171",
                        size=20,
                        font_family="Fredoka"
                    )
                )
                page.update()
                return
        elif route == "filter":
            page.add(FilterContent(page, tutor_data, selected_group, on_group_select, cache))
        else:
            page.add(Text("Página no encontrada", color="#F87171", size=20, font_family="Fredoka"))
        page.update()

    await navigate("login")

if __name__ == "__main__":
    flet.app(target=main, view=flet.WEB_BROWSER, port=8080)