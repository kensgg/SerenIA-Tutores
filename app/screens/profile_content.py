import flet
from flet import (
    Container, Column, Row, Text, TextField, IconButton, padding, alignment, border, border_radius,
    BoxShadow, Offset, ShadowBlurStyle, DataTable, DataColumn, DataRow, DataCell, AlertDialog, ButtonStyle, Icons, SnackBar
)
from services.data_cache import DataCache
import asyncio
import time
import logging

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

class ProfileContent(Column):
    def __init__(self, page, tutor_data, on_group_change=None, cache: DataCache=None):
        super().__init__()
        self.page = page
        self.tutor_data = tutor_data or {}
        self.tutor_id = tutor_data.get('id', '')
        self.on_group_change = on_group_change
        self.cache = cache
        self.groups = tutor_data.get('groups', [])
        self.selected_group = tutor_data.get('groups', [])[0] if tutor_data.get('groups') else None
        self.last_action_time = 0
        self.debounce_interval = 0.5
        self.is_updating = False
        self.initializing = False
        content_width = min(page.width - 40, 1012) if page.width else 1012
        groups_container_width = content_width * 0.7

        self.group_input = TextField(
            label="Nombre del Grupo",
            bgcolor=TutorDarkMoodPalette.INPUT_SURFACE,
            border_color=TutorDarkMoodPalette.INPUT_EDGE,
            focused_border_color=TutorDarkMoodPalette.INPUT_FOCUS,
            text_size=14,
            color=TutorDarkMoodPalette.TEXT_MAIN,
            label_style=flet.TextStyle(color=TutorDarkMoodPalette.TEXT_SUBTLE, font_family="Fredoka"),
            text_style=flet.TextStyle(color=TutorDarkMoodPalette.TEXT_MAIN, font_family="Fredoka"),
            border_radius=8,
            border_width=1,
            content_padding=padding.symmetric(horizontal=12, vertical=10),
            width=300
        )
        self.add_button = IconButton(
            icon=Icons.ADD,
            icon_size=20,
            icon_color=TutorDarkMoodPalette.TEXT_ON_ACCENT,
            bgcolor=TutorDarkMoodPalette.TRUST,
            width=48,
            height=48,
            tooltip="Agregar Grupo",
            style=ButtonStyle(
                shape=flet.RoundedRectangleBorder(radius=8),
                elevation=2,
                shadow_color=TutorDarkMoodPalette.SHADOW_SOFT,
                overlay_color=flet.Colors.with_opacity(0.2, TutorDarkMoodPalette.TRUST_HOVER)
            ),
            on_click=self.on_add_group
        )
        self.groups_table = DataTable(
            columns=[
                DataColumn(
                    Text(
                        "Grupo",
                        color=TutorDarkMoodPalette.TEXT_SUBTLE,
                        size=16,
                        weight='w600',
                        font_family="Fredoka"
                    )
                ),
                DataColumn(
                    Text(
                        "Acciones",
                        color=TutorDarkMoodPalette.TEXT_SUBTLE,
                        size=16,
                        weight='w600',
                        font_family="Fredoka"
                    ),
                    numeric=True
                )
            ],
            rows=[self.create_group_row(group) for group in self.groups],
            bgcolor=TutorDarkMoodPalette.CARD_SURFACE,
            border=border.all(1, TutorDarkMoodPalette.BORDER_SUBTLE),
            border_radius=12,
            heading_row_color=TutorDarkMoodPalette.INPUT_SURFACE,
            heading_row_height=48,
            data_row_color={
                "hovered": flet.Colors.with_opacity(0.15, TutorDarkMoodPalette.TRUST_HOVER),
                "selected": flet.Colors.with_opacity(0.1, TutorDarkMoodPalette.TRUST)
            },
            data_row_min_height=56,
            data_row_max_height=56,
            column_spacing=16,
            divider_thickness=1,
            vertical_lines=border.BorderSide(1, TutorDarkMoodPalette.BORDER_SUBTLE),
            horizontal_lines=border.BorderSide(1, TutorDarkMoodPalette.BORDER_SUBTLE),
            width=groups_container_width - 32
        )
        self.groups_container = Container(
            content=Column(
                controls=[
                    Row(
                        controls=[
                            Text(
                                "Gestionar Grupos",
                                color=TutorDarkMoodPalette.TEXT_MAIN,
                                size=20,
                                weight='w700',
                                font_family="Fredoka"
                            ),
                            Container(
                                content=Row(
                                    controls=[self.group_input, self.add_button],
                                    spacing=8,
                                    alignment=flet.MainAxisAlignment.END
                                ),
                                bgcolor=TutorDarkMoodPalette.INPUT_SURFACE,
                                border_radius=8,
                                padding=padding.symmetric(horizontal=12, vertical=8)
                            )
                        ],
                        alignment=flet.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=flet.CrossAxisAlignment.CENTER
                    ),
                    Container(
                        content=self.groups_table,
                        padding=padding.only(top=16),
                        alignment=alignment.center,
                        expand=True
                    )
                ],
                spacing=16,
                scroll="auto"
            ),
            bgcolor=TutorDarkMoodPalette.CARD_SURFACE,
            border_radius=12,
            border=border.all(1, TutorDarkMoodPalette.BORDER_SUBTLE),
            padding=padding.all(16),
            height=400,
            width=groups_container_width,
            shadow=BoxShadow(
                spread_radius=0,
                blur_radius=16,
                color=TutorDarkMoodPalette.SHADOW_SOFT,
                offset=Offset(0, 4),
                blur_style=ShadowBlurStyle.NORMAL
            )
        )
        self.edit_dialog = AlertDialog(
            title=Text("Editar Grupo", color=TutorDarkMoodPalette.TEXT_MAIN, font_family="Fredoka", size=18),
            content=TextField(
                label="Nuevo Nombre",
                bgcolor=TutorDarkMoodPalette.INPUT_SURFACE,
                border_color=TutorDarkMoodPalette.INPUT_EDGE,
                focused_border_color=TutorDarkMoodPalette.INPUT_FOCUS,
                text_size=14,
                color=TutorDarkMoodPalette.TEXT_MAIN,
                label_style=flet.TextStyle(color=TutorDarkMoodPalette.TEXT_SUBTLE, font_family="Fredoka"),
                text_style=flet.TextStyle(color=TutorDarkMoodPalette.TEXT_MAIN, font_family="Fredoka"),
                border_radius=8,
                border_width=1,
                content_padding=padding.symmetric(horizontal=12, vertical=10),
                width=300
            ),
            actions=[
                IconButton(
                    icon=Icons.SAVE,
                    icon_color=TutorDarkMoodPalette.SUCCESS_FEEDBACK,
                    bgcolor=TutorDarkMoodPalette.TRUST,
                    tooltip="Guardar",
                    style=ButtonStyle(
                        shape=flet.RoundedRectangleBorder(radius=8),
                        elevation=1
                    ),
                    on_click=self.on_save_edit
                ),
                IconButton(
                    icon=Icons.CANCEL,
                    icon_color=TutorDarkMoodPalette.ERROR_FEEDBACK,
                    bgcolor=TutorDarkMoodPalette.INPUT_SURFACE,
                    tooltip="Cancelar",
                    style=ButtonStyle(
                        shape=flet.RoundedRectangleBorder(radius=8),
                        elevation=1
                    ),
                    on_click=self.close_dialog
                )
            ],
            actions_alignment=flet.MainAxisAlignment.END,
            bgcolor=TutorDarkMoodPalette.CARD_SURFACE,
            content_padding=padding.all(16),
            modal=True,
            shape=flet.RoundedRectangleBorder(radius=12)
        )
        self.delete_dialog = AlertDialog(
            title=Text("Confirmar Eliminación", color=TutorDarkMoodPalette.TEXT_MAIN, font_family="Fredoka", size=18),
            content=Text("", color=TutorDarkMoodPalette.TEXT_SUBTLE, font_family="Fredoka", size=14),
            actions=[
                IconButton(
                    icon=Icons.DELETE,
                    icon_color=TutorDarkMoodPalette.ERROR_FEEDBACK,
                    bgcolor=TutorDarkMoodPalette.INPUT_SURFACE,
                    tooltip="Eliminar",
                    style=ButtonStyle(
                        shape=flet.RoundedRectangleBorder(radius=8),
                        elevation=1
                    ),
                    on_click=self.on_confirm_delete
                ),
                IconButton(
                    icon=Icons.CANCEL,
                    icon_color=TutorDarkMoodPalette.ERROR_FEEDBACK,
                    bgcolor=TutorDarkMoodPalette.INPUT_SURFACE,
                    tooltip="Cancelar",
                    style=ButtonStyle(
                        shape=flet.RoundedRectangleBorder(radius=8),
                        elevation=1
                    ),
                    on_click=self.close_dialog
                )
            ],
            actions_alignment=flet.MainAxisAlignment.END,
            bgcolor=TutorDarkMoodPalette.CARD_SURFACE,
            content_padding=padding.all(16),
            modal=True,
            shape=flet.RoundedRectangleBorder(radius=12)
        )
        self.controls = [
            Text(
                "Configuración",
                color=TutorDarkMoodPalette.TEXT_MAIN,
                size=28,
                weight='w700',
                font_family="Fredoka"
            ),
            flet.Divider(height=24, color='transparent'),
            Container(
                content=self.groups_container,
                alignment=alignment.center,
                expand=True
            )
        ]
        self.scroll = "auto"
        self.spacing = 0
        self.expand = True
        self.horizontal_alignment = flet.CrossAxisAlignment.CENTER

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

    async def initialize(self):
        if self.initializing:
            return
        self.initializing = True
        try:
            if not self.tutor_id:
                self.show_snackbar("Tutor ID no válido", TutorDarkMoodPalette.ERROR_FEEDBACK)
                return
            groups_response = await self.cache.get_tutor_groups(self.tutor_id)
            if not isinstance(groups_response, list):
                self.show_snackbar("Error al cargar grupos: Respuesta inválida", TutorDarkMoodPalette.ERROR_FEEDBACK)
                return
            self.groups = groups_response
            self.tutor_data['groups'] = self.groups
            self.groups_table.rows = [self.create_group_row(group) for group in self.groups]
            if self.on_group_change and self.selected_group is not None:
                await self.on_group_change(self.selected_group)
        except Exception as e:
            self.show_snackbar(f"Error al cargar grupos: {str(e)}", TutorDarkMoodPalette.ERROR_FEEDBACK)
        finally:
            self.initializing = False
            self.page.update()

    def create_group_row(self, group):
        return DataRow(
            cells=[
                DataCell(
                    Text(
                        group,
                        color=TutorDarkMoodPalette.TEXT_MAIN,
                        size=14,
                        weight='w600',
                        font_family="Fredoka"
                    )
                ),
                DataCell(
                    Row(
                        controls=[
                            IconButton(
                                icon=Icons.EDIT,
                                icon_size=16,
                                icon_color=TutorDarkMoodPalette.WARNING_FEEDBACK,
                                bgcolor=TutorDarkMoodPalette.TRUST,
                                tooltip="Editar",
                                style=ButtonStyle(
                                    shape=flet.RoundedRectangleBorder(radius=6),
                                    overlay_color=flet.Colors.with_opacity(0.2, TutorDarkMoodPalette.TRUST_HOVER),
                                    elevation=1
                                ),
                                on_click=lambda e, g=group: self.on_edit_group(e, g)
                            ),
                            IconButton(
                                icon=Icons.DELETE,
                                icon_size=16,
                                icon_color=TutorDarkMoodPalette.ERROR_FEEDBACK,
                                bgcolor=TutorDarkMoodPalette.INPUT_SURFACE,
                                tooltip="Eliminar",
                                style=ButtonStyle(
                                    shape=flet.RoundedRectangleBorder(radius=6),
                                    overlay_color=flet.Colors.with_opacity(0.2, TutorDarkMoodPalette.ERROR_FEEDBACK),
                                    elevation=1
                                ),
                                on_click=lambda e, g=group: self.on_delete_group(e, g)
                            )
                        ],
                        spacing=8,
                        alignment=flet.MainAxisAlignment.END
                    )
                )
            ],
            selected=False,
            data=group
        )

    async def on_add_group(self, e):
        current_time = time.time()
        if current_time - self.last_action_time < self.debounce_interval:
            return
        self.last_action_time = current_time
        if self.is_updating:
            return
        self.is_updating = True
        try:
            group_name = self.group_input.value.strip()
            if not group_name:
                self.show_snackbar("El nombre del grupo no puede estar vacío", TutorDarkMoodPalette.ERROR_FEEDBACK)
                return
            if group_name in self.groups:
                self.show_snackbar("El grupo ya existe", TutorDarkMoodPalette.ERROR_FEEDBACK)
                return
            await self.cache.add_tutor_group(self.tutor_id, group_name)
            self.groups.append(group_name)
            self.tutor_data['groups'] = self.groups
            self.groups_table.rows.append(self.create_group_row(group_name))
            self.group_input.value = ""
            self.selected_group = group_name
            if self.on_group_change:
                await self.on_group_change(group_name)
            self.show_snackbar(f"Grupo {group_name} agregado exitosamente", TutorDarkMoodPalette.SUCCESS_FEEDBACK)
        except Exception as e:
            self.show_snackbar(f"Error al agregar grupo: {str(e)}", TutorDarkMoodPalette.ERROR_FEEDBACK)
        finally:
            self.is_updating = False
            self.page.update()

    def on_edit_group(self, e, group):
        self.edit_dialog.content.value = group
        self.edit_dialog.data = group
        if self.edit_dialog not in self.page.overlay:
            self.page.overlay.append(self.edit_dialog)
        self.page.dialog = self.edit_dialog
        self.edit_dialog.open = True
        self.page.update()

    async def on_save_edit(self, e):
        current_time = time.time()
        if current_time - self.last_action_time < self.debounce_interval:
            return
        self.last_action_time = current_time
        if self.is_updating:
            return
        self.is_updating = True
        try:
            old_group = self.edit_dialog.data
            new_group = self.edit_dialog.content.value.strip()
            if not new_group:
                self.show_snackbar("El nombre del grupo no puede estar vacío", TutorDarkMoodPalette.ERROR_FEEDBACK)
                return
            if new_group == old_group:
                self.close_dialog()
                return
            if new_group in self.groups:
                self.show_snackbar("El grupo ya existe", TutorDarkMoodPalette.ERROR_FEEDBACK)
                return
            await self.cache.update_tutor_group(self.tutor_id, old_group, new_group)
            self.groups[self.groups.index(old_group)] = new_group
            self.tutor_data['groups'] = self.groups
            self.groups_table.rows = [self.create_group_row(group) for group in self.groups]
            self.selected_group = new_group
            if self.on_group_change:
                await self.on_group_change(new_group)
            self.show_snackbar(f"Grupo actualizado a {new_group}", TutorDarkMoodPalette.SUCCESS_FEEDBACK)
            self.close_dialog()
        except Exception as e:
            self.show_snackbar(f"Error al actualizar grupo: {str(e)}", TutorDarkMoodPalette.ERROR_FEEDBACK)
        finally:
            self.is_updating = False
            self.page.update()

    def on_delete_group(self, e, group):
        self.delete_dialog.content.value = f"¿Estás seguro de eliminar el grupo {group}?"
        self.delete_dialog.data = group
        if self.delete_dialog not in self.page.overlay:
            self.page.overlay.append(self.delete_dialog)
        self.page.dialog = self.delete_dialog
        self.delete_dialog.open = True
        self.page.update()

    async def on_confirm_delete(self, e):
        current_time = time.time()
        if current_time - self.last_action_time < self.debounce_interval:
            return
        self.last_action_time = current_time
        if self.is_updating:
            return
        self.is_updating = True
        try:
            group = self.delete_dialog.data
            await self.cache.delete_tutor_group(self.tutor_id, group)
            self.groups.remove(group)
            self.tutor_data['groups'] = self.groups
            self.groups_table.rows = [self.create_group_row(group) for group in self.groups]
            self.selected_group = self.groups[0] if self.groups else None
            if self.on_group_change:
                await self.on_group_change(self.selected_group)
            self.show_snackbar(f"Grupo {group} eliminado exitosamente", TutorDarkMoodPalette.SUCCESS_FEEDBACK)
            self.close_dialog()
        except Exception as e:
            self.show_snackbar(f"Error al eliminar grupo: {str(e)}", TutorDarkMoodPalette.ERROR_FEEDBACK)
        finally:
            self.is_updating = False
            self.page.update()

    def close_dialog(self, e=None):
        self.page.dialog = None
        self.edit_dialog.open = False
        self.delete_dialog.open = False
        self.page.update()