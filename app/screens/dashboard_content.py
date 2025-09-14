import flet
from flet import (
    Container, Column, Row, Text, Divider, MainAxisAlignment, CrossAxisAlignment,
    IconButton, padding, BoxShadow, Offset, ShadowBlurStyle, border, alignment,
    border_radius, Dropdown, dropdown, ButtonStyle, BarChart, BarChartGroup,
    BarChartRod, ChartAxis, ChartAxisLabel, ChartGridLines, Icons
)
from services.data_cache import DataCache
import asyncio
import time

class TutorDarkMoodPalette:
    MAIN_BACKGROUND = "#1E252D"
    CARD_SURFACE = "#2A323C"
    BORDER_SUBTLE = "#3B4653"
    TRUST = "#90CAF9"            # Pastel blue for depression (BDI)
    TRUST_HOVER = "#B3E0FF"      # Lighter pastel blue for hover
    ALERT = "#FFCC80"            # Pastel yellow for anxiety (BAI)
    SUPPORT = "#5C9CE6"
    URGENT = "#FFAB91"           # Pastel red for stress (PSS)
    TEXT_MAIN = "#E2E8F0"
    TEXT_SUBTLE = "#94A3B8"
    TEXT_ON_ACCENT = "#FFFFFF"
    INPUT_SURFACE = "#343D48"
    INPUT_EDGE = "#4B5563"
    INPUT_FOCUS = "#90CAF9"      # Match pastel blue for input focus
    SUCCESS_FEEDBACK = "#2DD4BF"
    ERROR_FEEDBACK = "#F87171"
    WARNING_FEEDBACK = "#FBBF24"
    SHADOW_SOFT = "rgba(0,0,0,0.2)"

class MetricCard(Container):
    def __init__(self, label, value):
        super().__init__()
        color = (
            TutorDarkMoodPalette.ALERT if label == "Promedio Ansiedad" else
            TutorDarkMoodPalette.URGENT if label == "Promedio Depresión" else
            TutorDarkMoodPalette.TRUST if label == "Promedio Estrés" else
            TutorDarkMoodPalette.TEXT_MAIN
        )
        self.content = Column(
            controls=[
                Text(
                    label,
                    color=TutorDarkMoodPalette.TEXT_SUBTLE,
                    size=12,
                    weight='w600',
                    font_family="Fredoka"
                ),
                Text(
                    str(round(value, 2) if isinstance(value, float) else value),
                    color=color,
                    size=24,
                    weight='w700',
                    font_family="Fredoka"
                )
            ],
            spacing=8
        )
        self.padding = padding.all(16)
        self.bgcolor = TutorDarkMoodPalette.CARD_SURFACE
        self.border_radius = 8
        self.border = border.all(1, TutorDarkMoodPalette.BORDER_SUBTLE)
        self.width = 248
        self.shadow = BoxShadow(
            spread_radius=0,
            blur_radius=12,
            color=TutorDarkMoodPalette.SHADOW_SOFT,
            offset=Offset(0, 4),
            blur_style=ShadowBlurStyle.NORMAL
        )

class DashboardContent(Column):
    def __init__(self, page, tutor_data, cache: DataCache=None, selected_group=None, on_group_change=None):
        super().__init__()
        self.page = page
        self.tutor_data = tutor_data or {}
        self.tutor_id = tutor_data.get('id', '')
        self.cache = cache or DataCache()
        self.on_group_change = on_group_change
        self.selected_group = selected_group
        self.metrics_data = None
        self.last_group_select_time = 0
        self.debounce_interval = 0.5
        self.is_updating = False
        self.groups = tutor_data.get('groups', [])
        content_width = min(page.width - 40, 1012) if page and hasattr(page, 'width') else 1012
        print(f"[DASHBOARD] Inicializando con tutor_id={self.tutor_id}, grupos={self.groups}, selected_group={selected_group}, page={'válido' if page else 'None'}")

        self.group_dropdown = Dropdown(
            label="Seleccionar Grupo",
            value=selected_group if selected_group in self.groups else (self.groups[0] if self.groups else None),
            options=[dropdown.Option(group) for group in self.groups],
            on_change=self.on_group_dropdown_change,
            width=200,
            bgcolor=TutorDarkMoodPalette.INPUT_SURFACE,
            border_color=TutorDarkMoodPalette.INPUT_EDGE,
            focused_border_color=TutorDarkMoodPalette.INPUT_FOCUS,
            text_size=14,
            color=TutorDarkMoodPalette.TEXT_MAIN,
            label_style=flet.TextStyle(
                color=TutorDarkMoodPalette.TEXT_SUBTLE,
                font_family="Fredoka"
            ),
            text_style=flet.TextStyle(
                color=TutorDarkMoodPalette.TEXT_MAIN,
                font_family="Fredoka"
            ),
            border_radius=8,
            border_width=1,
            content_padding=padding.symmetric(horizontal=12, vertical=10)
        )
        self.refresh_button = IconButton(
            icon=Icons.REFRESH,
            icon_size=20,
            icon_color=TutorDarkMoodPalette.TEXT_ON_ACCENT,
            bgcolor=TutorDarkMoodPalette.TRUST,
            width=36,
            height=36,
            tooltip="Recargar Datos",
            style=ButtonStyle(
                shape=flet.RoundedRectangleBorder(radius=6),
                elevation=2,
                overlay_color=flet.Colors.with_opacity(0.2, TutorDarkMoodPalette.TRUST_HOVER)
            ),
            on_click=self.refresh_data
        )
        self.gender_dropdown = Dropdown(
            options=[
                dropdown.Option(None, "Todos"),
                dropdown.Option("Masculino", "Masculino"),
                dropdown.Option("Femenino", "Femenino"),
                dropdown.Option("Otro", "Otro")
            ],
            value=None,
            text_size=12,
            text_style=flet.TextStyle(
                color=TutorDarkMoodPalette.TEXT_MAIN,
                weight='w600',
                font_family="Fredoka"
            ),
            bgcolor=TutorDarkMoodPalette.INPUT_SURFACE,
            border_color=TutorDarkMoodPalette.INPUT_EDGE,
            border_width=1,
            border_radius=6,
            padding=padding.symmetric(horizontal=8, vertical=8),
            focused_border_color=TutorDarkMoodPalette.INPUT_FOCUS,
            focused_border_width=1,
            width=120,
            on_change=self.on_filter_change
        )
        self.age_dropdown = Dropdown(
            options=[
                dropdown.Option(None, "Todas"),
                dropdown.Option("<18", "Menor de 18"),
                dropdown.Option("18-20", "18-20 años"),
                dropdown.Option("21-23", "21-23 años"),
                dropdown.Option(">23", "Mayor de 23")
            ],
            value=None,
            text_size=12,
            text_style=flet.TextStyle(
                color=TutorDarkMoodPalette.TEXT_MAIN,
                weight='w600',
                font_family="Fredoka"
            ),
            bgcolor=TutorDarkMoodPalette.INPUT_SURFACE,
            border_color=TutorDarkMoodPalette.INPUT_EDGE,
            border_width=1,
            border_radius=6,
            padding=padding.symmetric(horizontal=8, vertical=8),
            focused_border_color=TutorDarkMoodPalette.INPUT_FOCUS,
            focused_border_width=1,
            width=120,
            on_change=self.on_filter_change
        )
        self.reset_button = IconButton(
            icon=Icons.DELETE_SWEEP_OUTLINED,
            icon_size=20,
            icon_color=TutorDarkMoodPalette.WARNING_FEEDBACK,
            bgcolor=TutorDarkMoodPalette.TRUST,
            width=36,
            height=36,
            tooltip="Reiniciar Gráfica",
            style=ButtonStyle(
                shape=flet.RoundedRectangleBorder(radius=6),
                overlay_color=flet.Colors.with_opacity(0.1, TutorDarkMoodPalette.TRUST_HOVER)
            ),
            on_click=self.on_reset_chart
        )
        self.metrics_row = Row(
            controls=[
                MetricCard("Total Alumnos", 0),
                MetricCard("Promedio BAI", 0),
                MetricCard("Promedio BDI", 0),
                MetricCard("Promedio PSS", 0)
            ],
            spacing=12,
            width=content_width
        )
        self.chart_title = Text(
            "Respuestas Alumnos",
            color=TutorDarkMoodPalette.TEXT_MAIN,
            size=16,
            weight='w700',
            font_family="Fredoka"
        )
        self.chart_container = Container(
            content=Column(
                controls=[
                    Row(
                        controls=[
                            self.chart_title,
                            self.gender_dropdown,
                            self.age_dropdown,
                            self.reset_button
                        ],
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=CrossAxisAlignment.CENTER,
                        spacing=8,
                        wrap=True
                    ),
                    Container(
                        content=Text("Cargando datos...", color=TutorDarkMoodPalette.TEXT_SUBTLE, size=14, font_family="Fredoka"),
                        alignment=alignment.center,
                        padding=padding.all(20),
                        expand=True
                    )
                ],
                spacing=12,
                expand=True
            ),
            bgcolor=TutorDarkMoodPalette.CARD_SURFACE,
            border_radius=8,
            border=border.all(1, TutorDarkMoodPalette.BORDER_SUBTLE),
            padding=padding.all(16),
            height=400,
            width=600,
            shadow=BoxShadow(
                spread_radius=0,
                blur_radius=12,
                color=TutorDarkMoodPalette.SHADOW_SOFT,
                offset=Offset(0, 4),
                blur_style=ShadowBlurStyle.NORMAL
            )
        )
        self.alerts_container = Container(
            content=Column(
                controls=[
                    Row(
                        controls=[
                            Text(
                                "Alertas Recientes",
                                color=TutorDarkMoodPalette.TEXT_MAIN,
                                size=16,
                                weight='w700',
                                font_family="Fredoka"
                            )
                        ],
                        spacing=10
                    ),
                    Container(
                        content=Column(
                            controls=[Text("Cargando alertas...", color=TutorDarkMoodPalette.TEXT_SUBTLE, size=14, font_family="Fredoka")],
                            spacing=12,
                            scroll="auto",
                            expand=True
                        ),
                        padding=padding.only(top=12),
                        expand=True
                    )
                ],
                expand=True
            ),
            bgcolor=TutorDarkMoodPalette.CARD_SURFACE,
            border_radius=8,
            border=border.all(1, TutorDarkMoodPalette.BORDER_SUBTLE),
            padding=padding.all(16),
            height=400,
            width=400,
            shadow=BoxShadow(
                spread_radius=0,
                blur_radius=12,
                color=TutorDarkMoodPalette.SHADOW_SOFT,
                offset=Offset(0, 4),
                blur_style=ShadowBlurStyle.NORMAL
            )
        )
        self.controls = [
            Container(
                content=Row(
                    controls=[
                        Text(
                            "Panel de Control",
                            color=TutorDarkMoodPalette.TEXT_MAIN,
                            size=24,
                            weight='w700',
                            font_family="Fredoka"
                        ),
                        Row(
                            controls=[self.group_dropdown, self.refresh_button],
                            spacing=8
                        )
                    ],
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=CrossAxisAlignment.CENTER
                ),
                padding=padding.only(bottom=20)
            ),
            self.metrics_row,
            Divider(height=30, color='transparent'),
            Row(
                controls=[
                    self.chart_container,
                    Container(width=12),
                    self.alerts_container
                ],
                spacing=0,
                expand=True
            )
        ]
        self.spacing = 0
        self.scroll = "auto"
        self.expand = True
        self.width = content_width

    def get_metrics_data(self, group):
        """Calcula métricas, niveles y alertas para el grupo seleccionado usando DataCache"""
        try:
            users = self.cache.get_users_by_group(group)
            if not users:
                print(f"[DASHBOARD] No hay usuarios para el grupo {group}")
                return {
                    "total_students": 0,
                    "bai_avg": 0,
                    "bdi_avg": 0,
                    "pss_avg": 0,
                    "level_counts": {"BAI": [0, 0, 0, 0], "BDI": [0, 0, 0, 0], "PSS": [0, 0, 0, 0]},
                    "alerts": [],
                    "gender_groups": {},
                    "age_groups": {}
                }

            total_students = len(users)
            bai_scores, bdi_scores, pss_scores = [], [], []
            level_counts = {"BAI": [0, 0, 0, 0], "BDI": [0, 0, 0, 0], "PSS": [0, 0, 0, 0]}
            alerts = []
            gender_groups = {
                "Masculino": {"BAI": [0, 0, 0, 0], "BDI": [0, 0, 0, 0], "PSS": [0, 0, 0, 0]},
                "Femenino": {"BAI": [0, 0, 0, 0], "BDI": [0, 0, 0, 0], "PSS": [0, 0, 0, 0]},
                "Otro": {"BAI": [0, 0, 0, 0], "BDI": [0, 0, 0, 0], "PSS": [0, 0, 0, 0]}
            }
            age_groups = {
                "<18": {"BAI": [0, 0, 0, 0], "BDI": [0, 0, 0, 0], "PSS": [0, 0, 0, 0]},
                "18-20": {"BAI": [0, 0, 0, 0], "BDI": [0, 0, 0, 0], "PSS": [0, 0, 0, 0]},
                "21-23": {"BAI": [0, 0, 0, 0], "BDI": [0, 0, 0, 0], "PSS": [0, 0, 0, 0]},
                ">23": {"BAI": [0, 0, 0, 0], "BDI": [0, 0, 0, 0], "PSS": [0, 0, 0, 0]}
            }

            for user in users:
                user_id = user.get("doc_id", "")
                name = user.get("name", "Sin nombre")
                gender = user.get("gender", "Otro")
                age = user.get("age", None)
                age_key = (
                    "<18" if age and age < 18 else
                    "18-20" if age and 18 <= age <= 20 else
                    "21-23" if age and 21 <= age <= 23 else
                    ">23" if age and age > 23 else
                    ">23"
                )
                responses = self.cache.get_user_responses(user_id)
                latest_levels = {"BAI": 0, "BDI": 0, "PSS": 0}
                questionnaires_alert = []

                for response in sorted(responses, key=lambda x: x.get("timestamp", ""), reverse=True):
                    questionnaire = response.get("questionnaire", "")
                    level = response.get("level", 0)
                    if questionnaire in latest_levels and latest_levels[questionnaire] == 0:
                        latest_levels[questionnaire] = level
                        if level >= 2:
                            questionnaires_alert.append(f"{questionnaire} (Nivel {level})")
                    if all(latest_levels[q] != 0 for q in ["BAI", "BDI", "PSS"]):
                        break

                for q, level in latest_levels.items():
                    level_counts[q][level] += 1
                    if gender in gender_groups:
                        gender_groups[gender][q][level] += 1
                    age_groups[age_key][q][level] += 1
                    if q == "BAI" and level > 0:
                        bai_scores.append(level * 10)
                    elif q == "BDI" and level > 0:
                        bdi_scores.append(level * 10)
                    elif q == "PSS" and level > 0:
                        pss_scores.append(level * 10)

                if questionnaires_alert:
                    alerts.append({
                        "student_name": name,
                        "questionnaires": ", ".join(questionnaires_alert),
                        "highest_level": max(latest_levels.values())
                    })

            bai_avg = sum(bai_scores) / len(bai_scores) if bai_scores else 0
            bdi_avg = sum(bdi_scores) / len(bdi_scores) if bdi_scores else 0
            pss_avg = sum(pss_scores) / len(pss_scores) if pss_scores else 0

            print(f"[DASHBOARD] Métricas para {group}: total={total_students}, BAI_avg={bai_avg:.2f}, BDI_avg={bdi_avg:.2f}, PSS_avg={pss_avg:.2f}, alertas={len(alerts)}")
            print(f"[DASHBOARD] Niveles: {level_counts}")
            print(f"[DASHBOARD] Grupos por género: {gender_groups}")
            print(f"[DASHBOARD] Grupos por edad: {age_groups}")

            return {
                "total_students": total_students,
                "bai_avg": bai_avg,
                "bdi_avg": bdi_avg,
                "pss_avg": pss_avg,
                "level_counts": level_counts,
                "alerts": alerts,
                "gender_groups": gender_groups,
                "age_groups": age_groups
            }
        except Exception as e:
            print(f"[DASHBOARD] Error al calcular métricas para {group}: {str(e)}")
            return {
                "total_students": 0,
                "bai_avg": 0,
                "bdi_avg": 0,
                "pss_avg": 0,
                "level_counts": {"BAI": [0, 0, 0, 0], "BDI": [0, 0, 0, 0], "PSS": [0, 0, 0, 0]},
                "alerts": [],
                "gender_groups": {},
                "age_groups": {}
            }

    def create_chart(self):
        """Crea un gráfico de barras con los niveles de los alumnos"""
        if not self.metrics_data:
            return Text("No hay datos disponibles", color=TutorDarkMoodPalette.TEXT_SUBTLE, size=14, font_family="Fredoka")
        level_counts = self.metrics_data.get("level_counts", {"BAI": [0, 0, 0, 0], "BDI": [0, 0, 0, 0], "PSS": [0, 0, 0, 0]})
        gender = self.gender_dropdown.value
        age = self.age_dropdown.value
        if gender or age:
            level_counts = {"BAI": [0, 0, 0, 0], "BDI": [0, 0, 0, 0], "PSS": [0, 0, 0, 0]}
            data_source = self.metrics_data.get("gender_groups", {}) if gender else self.metrics_data.get("age_groups", {})
            key = gender or age
            if key in data_source:
                level_counts = data_source[key]
        bar_groups = []
        for level in range(4):
            rods = [
                BarChartRod(
                    from_y=0,
                    to_y=level_counts["BAI"][level],
                    width=20,
                    color=TutorDarkMoodPalette.ALERT,
                    tooltip=f"BAI: {level_counts['BAI'][level]}",
                    border_radius=4
                ),
                BarChartRod(
                    from_y=0,
                    to_y=level_counts["BDI"][level],
                    width=20,
                    color=TutorDarkMoodPalette.URGENT,
                    tooltip=f"BDI: {level_counts['BDI'][level]}",
                    border_radius=4
                ),
                BarChartRod(
                    from_y=0,
                    to_y=level_counts["PSS"][level],
                    width=20,
                    color=TutorDarkMoodPalette.TRUST,
                    tooltip=f"PSS: {level_counts['PSS'][level]}",
                    border_radius=4
                )
            ]
            bar_groups.append(
                BarChartGroup(
                    x=level,
                    bar_rods=rods,
                    bars_space=5,
                    group_vertically=False
                )
            )
        max_y = max([max(counts) for counts in level_counts.values()] + [1]) + 1
        return BarChart(
            bar_groups=bar_groups,
            border=border.all(1, TutorDarkMoodPalette.BORDER_SUBTLE),
            left_axis=ChartAxis(
                labels_size=40,
                title=Text("Número de Estudiantes", size=14, color=TutorDarkMoodPalette.TEXT_MAIN, weight='w600', font_family="Fredoka"),
                title_size=20
            ),
            bottom_axis=ChartAxis(
                labels=[
                    ChartAxisLabel(value=0, label=Container(Text("Nivel 0", size=12, color=TutorDarkMoodPalette.TEXT_MAIN, font_family="Fredoka"), padding=10)),
                    ChartAxisLabel(value=1, label=Container(Text("Nivel 1", size=12, color=TutorDarkMoodPalette.TEXT_MAIN, font_family="Fredoka"), padding=10)),
                    ChartAxisLabel(value=2, label=Container(Text("Nivel 2", size=12, color=TutorDarkMoodPalette.TEXT_MAIN, font_family="Fredoka"), padding=10)),
                    ChartAxisLabel(value=3, label=Container(Text("Nivel 3", size=12, color=TutorDarkMoodPalette.TEXT_MAIN, font_family="Fredoka"), padding=10))
                ],
                labels_size=40
            ),
            horizontal_grid_lines=ChartGridLines(
                color=TutorDarkMoodPalette.TEXT_SUBTLE,
                width=1,
                dash_pattern=[3, 3]
            ),
            tooltip_bgcolor=TutorDarkMoodPalette.INPUT_SURFACE,
            max_y=max_y,
            interactive=True,
            groups_space=20,
            expand=True
        )

    def create_alerts(self):
        """Crea tarjetas de alertas para alumnos con niveles 2 o 3"""
        if not self.metrics_data:
            return [Text("No hay alertas disponibles", color=TutorDarkMoodPalette.TEXT_SUBTLE, size=14, font_family="Fredoka")]
        alerts = sorted(self.metrics_data.get("alerts", []), key=lambda x: x.get("highest_level", 0), reverse=True)
        alert_controls = []
        for alert in alerts:
            questionnaires = alert["questionnaires"].split(", ") if alert["questionnaires"] else []
            alert_controls.append(
                Container(
                    content=Column(
                        controls=[
                            Text(
                                f"Nombre: {alert['student_name']}",
                                color=TutorDarkMoodPalette.TEXT_MAIN,
                                size=14,
                                weight='w600',
                                font_family="Fredoka",
                                width=360
                            ),
                            *[Text(
                                q,
                                color=TutorDarkMoodPalette.TEXT_SUBTLE,
                                size=12,
                                weight='w400',
                                font_family="Fredoka",
                                width=360
                            ) for q in questionnaires]
                        ],
                        spacing=4
                    ),
                    bgcolor=TutorDarkMoodPalette.CARD_SURFACE,
                    border=border.Border(
                        left=border.BorderSide(4, TutorDarkMoodPalette.URGENT),
                        top=border.BorderSide(1, TutorDarkMoodPalette.BORDER_SUBTLE),
                        right=border.BorderSide(1, TutorDarkMoodPalette.BORDER_SUBTLE),
                        bottom=border.BorderSide(1, TutorDarkMoodPalette.BORDER_SUBTLE)
                    ),
                    border_radius=6,
                    padding=padding.all(12),
                    margin=padding.only(bottom=8),
                    width=360
                )
            )
        print(f"[DASHBOARD] Generadas {len(alert_controls)} alertas")
        return alert_controls

    def on_filter_change(self, e):
        """Actualiza el gráfico al cambiar los filtros de género o edad"""
        if not self.is_updating:
            self.chart_container.content.controls[1].content = self.create_chart()
            print(f"[DASHBOARD] Filtros aplicados: género={self.gender_dropdown.value}, edad={self.age_dropdown.value}")
            if self.page:
                self.page.update()
            else:
                print("[DASHBOARD] No se puede actualizar la página: self.page es None")

    def on_reset_chart(self, e):
        """Reinicia los filtros y actualiza el gráfico"""
        self.gender_dropdown.value = None
        self.age_dropdown.value = None
        if not self.is_updating:
            self.chart_container.content.controls[1].content = self.create_chart()
            print("[DASHBOARD] Gráfico reiniciado")
            if self.page:
                self.page.update()
            else:
                print("[DASHBOARD] No se puede actualizar la página: self.page es None")

    async def on_group_dropdown_change(self, e):
        """Maneja el cambio de grupo en el Dropdown"""
        current_time = time.time()
        if current_time - self.last_group_select_time < self.debounce_interval:
            print("[DASHBOARD] Cambio de grupo ignorado por debounce")
            return
        self.last_group_select_time = current_time
        new_group = e.data if hasattr(e, 'data') else e.control.value
        print(f"[DASHBOARD] Cambio de grupo a: {new_group}")
        if new_group == self.selected_group:
            print("[DASHBOARD] Mismo grupo seleccionado, no se actualiza")
            return
        if self.is_updating:
            print("[DASHBOARD] Actualización en curso, cambio de grupo ignorado")
            return
        self.is_updating = True
        try:
            self.selected_group = new_group
            self.metrics_data = self.get_metrics_data(new_group)
            await self.update_metrics_and_chart()
            if self.on_group_change:
                print(f"[DASHBOARD] Llamando on_group_change con grupo: {new_group}")
                if asyncio.iscoroutinefunction(self.on_group_change):
                    await self.on_group_change(new_group)
                else:
                    self.on_group_change(new_group)
        except Exception as e:
            print(f"[DASHBOARD] Error al cambiar grupo {new_group}: {str(e)}")
        finally:
            self.is_updating = False
            if self.page:
                self.page.update()
            else:
                print("[DASHBOARD] No se puede actualizar la página: self.page es None")

    async def update_metrics_and_chart(self):
        """Actualiza las métricas, gráfico y alertas"""
        if self.is_updating:
            print("[DASHBOARD] Actualización en curso, ignorando")
            return
        self.is_updating = True
        try:
            if self.selected_group:
                self.metrics_data = self.get_metrics_data(self.selected_group)
                if self.metrics_data["total_students"] == 0:
                    self.chart_container.content.controls[1].content = Text(
                        f"No hay alumnos en el grupo {self.selected_group}",
                        color=TutorDarkMoodPalette.WARNING_FEEDBACK,
                        size=14,
                        font_family="Fredoka"
                    )
                    self.alerts_container.content.controls[1].content.controls = [
                        Text(
                            f"No hay alumnos en el grupo {self.selected_group}",
                            color=TutorDarkMoodPalette.WARNING_FEEDBACK,
                            size=14,
                            font_family="Fredoka"
                        )
                    ]
                else:
                    self.metrics_row.controls = [
                        MetricCard("Total Alumnos", self.metrics_data.get("total_students", 0)),
                        MetricCard("Promedio BAI", self.metrics_data.get("bai_avg", 0)),
                        MetricCard("Promedio BDI", self.metrics_data.get("bdi_avg", 0)),
                        MetricCard("Promedio PSS", self.metrics_data.get("pss_avg", 0))
                    ]
                    self.alerts_container.content.controls[1].content.controls = self.create_alerts()
                    self.chart_container.content.controls[1].content = self.create_chart()
            else:
                self.metrics_data = None
                self.metrics_row.controls = [
                    MetricCard("Total Alumnos", 0),
                    MetricCard("Promedio BAI", 0),
                    MetricCard("Promedio BDI", 0),
                    MetricCard("Promedio PSS", 0)
                ]
                self.alerts_container.content.controls[1].content.controls = [
                    Text("No hay alertas disponibles", color=TutorDarkMoodPalette.TEXT_SUBTLE, size=14, font_family="Fredoka")
                ]
                self.chart_container.content.controls[1].content = Text(
                    "No hay datos disponibles", color=TutorDarkMoodPalette.TEXT_SUBTLE, size=14, font_family="Fredoka"
                )
        except Exception as e:
            print(f"[DASHBOARD] Error al actualizar métricas y gráfico: {str(e)}")
            self.metrics_data = None
            self.metrics_row.controls = [
                MetricCard("Total Alumnos", 0),
                MetricCard("Promedio BAI", 0),
                MetricCard("Promedio BDI", 0),
                MetricCard("Promedio PSS", 0)
            ]
            self.alerts_container.content.controls[1].content.controls = [
                Text("Error al cargar alertas", color=TutorDarkMoodPalette.ERROR_FEEDBACK, size=14, font_family="Fredoka")
            ]
            self.chart_container.content.controls[1].content = Text(
                "Error al cargar datos", color=TutorDarkMoodPalette.ERROR_FEEDBACK, size=14, font_family="Fredoka"
            )
        finally:
            self.is_updating = False
            if self.page:
                self.page.update()
            else:
                print("[DASHBOARD] No se puede actualizar la página: self.page es None")

    async def refresh_data(self, e):
        """Recarga los datos del caché y actualiza el dashboard"""
        try:
            print("[DASHBOARD] Recargando datos del caché")
            await self.cache.load_all_data()
            self.groups = self.tutor_data.get('groups', [])
            self.group_dropdown.options = [dropdown.Option(group) for group in self.groups]
            self.group_dropdown.value = self.selected_group if self.selected_group in self.groups else (self.groups[0] if self.groups else None)
            await self.on_group_dropdown_change(flet.ControlEvent(control=self.group_dropdown, data=self.group_dropdown.value))
            print("[DASHBOARD] Datos recargados correctamente")
        except Exception as e:
            print(f"[DASHBOARD] Error al recargar datos: {str(e)}")

    async def initialize(self):
        """Inicializa el dashboard"""
        print("[DASHBOARD] Ejecutando initialize")
        await self.update_metrics_and_chart()