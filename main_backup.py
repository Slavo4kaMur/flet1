from flet import *
import sqlite3
import os
import shutil
import sys
import traceback

_log_lines = []


def _log(msg):
    _log_lines.append(msg)
    print(msg, flush=True)


def export_db(_=None):
            close_drawer()
            platform = page.platform
            _log(f"[EXPORT] platform={platform}")
            is_mobile_platform = platform in ("android", "ios")
            _log(f"[EXPORT] is_mobile_platform={is_mobile_platform}")

            if is_mobile_platform:
                import asyncio
                from flet.controls.services.file_picker import FilePicker as FPF, FilePickerFileType as FPT

                async def do_save():
                    try:
                        _log("[EXPORT] Creating FilePicker...")
                        fp = FPF()
                        page.overlay.append(fp)
                        page.update()
                        _log("[EXPORT] Calling save_file...")
                        result = await fp.save_file(
                            dialog_title="Сохранить базу данных",
                            file_name="data.db",
                            allowed_extensions=["db"]
                        )
                        _log(f"[EXPORT] save_file result={result}")
                        if result:
                            shutil.copy("data.db", result)
                            page.snack_bar = SnackBar(Text(f"БД сохранена: {result}"), open=True)
                            page.update()
                        else:
                            _log("[EXPORT] save_file returned None")
                    except Exception as e:
                        _log(f"[EXPORT] ERROR: {e}")
                        _log(traceback.format_exc())
                        page.snack_bar = SnackBar(Text(f"Ошибка: {e}"), open=True)
                        page.update()

                asyncio.create_task(do_save())
            elif tk_support:
                root = tk.Tk()
                root.withdraw()
                root.attributes('-topmost', True)
                path = filedialog.asksaveasfilename(
                    title="Сохранить базу данных",
                    defaultextension=".db",
                    filetypes=[("База данных", "*.db"), ("Все файлы", "*.*")],
                    initialfile="data.db"
                )
                root.destroy()
                if path:
                    shutil.copy("data.db", path)
                    page.snack_bar = SnackBar(Text(f"БД сохранена: {path}"), open=True)
                    page.update()
            else:
                page.snack_bar = SnackBar(Text("Проводник недоступен"), open=True)
                page.update()

        def import_db(_=None):
            close_drawer()
            platform = page.platform
            _log(f"[IMPORT] platform={platform}")
            is_mobile_platform = platform in ("android", "ios")
            _log(f"[IMPORT] is_mobile_platform={is_mobile_platform}")

            if is_mobile_platform:
                import asyncio
                from flet.controls.services.file_picker import FilePicker as FPF, FilePickerFileType as FPT

                async def do_load():
                    try:
                        _log("[IMPORT] Creating FilePicker...")
                        fp = FPF()
                        page.overlay.append(fp)
                        page.update()
                        _log("[IMPORT] Calling pick_files...")
                        files = await fp.pick_files(
                            dialog_title="Выбрать файл базы данных",
                            file_type=FPT.CUSTOM,
                            allowed_extensions=["db"]
                        )
                        _log(f"[IMPORT] pick_files result={files}")
                        if files:
                            src = files[0].path
                            shutil.copy(src, "data.db")
                            page.snack_bar = SnackBar(Text(f"БД загружена: {src}"), open=True)
                            page.update()
                            show_main()
                        else:
                            _log("[IMPORT] pick_files returned empty")
                    except Exception as e:
                        _log(f"[IMPORT] ERROR: {e}")
                        _log(traceback.format_exc())
                        page.snack_bar = SnackBar(Text(f"Ошибка: {e}"), open=True)
                        page.update()

                asyncio.create_task(do_load())
            elif tk_support:
                root = tk.Tk()
                root.withdraw()
                root.attributes('-topmost', True)
                path = filedialog.askopenfilename(
                    title="Выбрать файл базы данных",
                    filetypes=[("База данных", "*.db"), ("Все файлы", "*.*")]
                )
                root.destroy()
                if path:
                    shutil.copy(path, "data.db")
                    page.snack_bar = SnackBar(Text(f"БД загружена: {path}"), open=True)
                    page.update()
                    show_main()
            else:
                page.snack_bar = SnackBar(Text("Проводник недоступен"), open=True)
                page.update()

        def close_drawer():
            close_drawer()
            if tk_support:
                root = tk.Tk()
                root.withdraw()
                root.attributes('-topmost', True)
                path = filedialog.asksaveasfilename(
                    title="Сохранить базу данных",
                    defaultextension=".db",
                    filetypes=[("База данных", "*.db"), ("Все файлы", "*.*")],
                    initialfile="data.db"
                )
                root.destroy()
                if path:
                    shutil.copy("data.db", path)
                    page.snack_bar = SnackBar(Text(f"БД сохранена: {path}"), open=True)
                    page.update()
            else:
                page.snack_bar = SnackBar(Text("Выберите файл вручную"), open=True)
                page.update()

        def import_db(_=None):
            close_drawer()
            if tk_support:
                root = tk.Tk()
                root.withdraw()
                root.attributes('-topmost', True)
                path = filedialog.askopenfilename(
                    title="Выбрать файл базы данных",
                    filetypes=[("База данных", "*.db"), ("Все файлы", "*.*")]
                )
                root.destroy()
                if path:
                    shutil.copy(path, "data.db")
                    close_drawer()
                    page.snack_bar = SnackBar(Text(f"БД загружена: {path}"), open=True)
                    page.update()
                    show_main()
            else:
                page.snack_bar = SnackBar(Text("Выберите файл вручную"), open=True)
                page.update()

        def close_drawer():
            drawer_panel.left = -260
            drawer_overlay.opacity = 0
            drawer_overlay.visible = False
            page.update()

        def open_drawer():
            drawer_panel.left = 0
            drawer_overlay.opacity = 0.5
            drawer_overlay.visible = True
            page.update()

        def overlay_click(e):
            close_drawer()

        drawer_overlay = Container(
            bgcolor=Colors.BLACK54,
            expand=True,
            on_click=overlay_click,
            visible=False,
            opacity=0,
            left=0, top=0, right=0, bottom=0
        )

        drawer_panel = Container(
            width=260,
            bgcolor="#1a1a5e",
            padding=10,
            left=-260,
            top=0, bottom=0,
            content=Column([
                Container(height=20),
                Row([
                    Icon(Icons.STORAGE, color="white"),
                    Container(width=10),
                    Text("Для разработчика", color="white", size=18, weight=FontWeight.BOLD),
                ]),
                Divider(color="white24"),
                ListTile(
                    leading=Icon(Icons.HOME, color="white"),
                    title=Text("Главная", color="white"),
                    on_click=lambda _: close_drawer(),
                ),
                Divider(color="white24"),
ListTile(
                        leading=Icon(Icons.UPLOAD, color="white"),
                        title=Text("Выгрузить БД", color="white"),
                        subtitle=Text("Сохранить копию", color="white54", size=11),
                        on_click=export_db,
                    ),
                    ListTile(
                        leading=Icon(Icons.DOWNLOAD, color="white"),
                        title=Text("Загрузить БД", color="white"),
                        subtitle=Text("Восстановить из файла", color="white54", size=11),
                        on_click=import_db,
                    ),
                    Divider(color="white24"),
                    ListTile(
                        leading=Icon(Icons.BUG_REPORT, color="white"),
                        title=Text("Логи", color="white"),
                        subtitle=Text("Показать логи", color="white54", size=11),
                        on_click=lambda _: (
                            page.dialog and setattr(page.dialog, 'open', False),
                            setattr(page, 'dialog', AlertDialog(
                                title=Text("Логи", color="white"),
                                bgcolor="#1a1a5e",
                                content=Column([
                                    Text("\n".join(_log_lines[-50:]) or "(нет логов)", color="white70", size=11, selectable=True),
                                    Container(height=10),
                                    Row([
                                        Button("Очистить", on_click=lambda _: (_log_lines.clear(), setattr(page.dialog, 'open', False), page.update())),
                                        Button("Закрыть", on_click=lambda _: (setattr(page.dialog, 'open', False), page.update())),
                                    ], wrap=True),
                                ], scroll=ScrollMode.AUTO, height=400, width=300)
                            )),
                            setattr(page.dialog, 'open', True),
                            page.update()
                        ),
                    ),
            ])
        )

        page.overlay.extend([drawer_overlay, drawer_panel])

        search_input.on_change = lambda e: refresh()
        date_filter.on_change = lambda e: refresh()
        year_dropdown.on_change = lambda e: refresh()
        load_years()

        if is_mobile:
            search_input.label = "Поиск"
            date_filter.label = "Дата"
            year_dropdown.width = 100
            search_input.width = None
            date_filter.width = None
        else:
            search_input.width = 200
            date_filter.width = 150
            year_dropdown.width = 120

        def zoom_in(_):
            global app_scale
            app_scale = min(app_scale + 0.1, 2.0)
            page.clean()
            show_main()

        def zoom_out(_):
            global app_scale
            app_scale = max(app_scale - 0.1, 0.5)
            page.clean()
            show_main()

        def toggle_mobile(_):
            global is_mobile, mobile_toggled
            mobile_toggled = True
            is_mobile = not is_mobile
            page.clean()
            show_main()

        title_size = 24 if is_mobile else 20

        header = Row(
            alignment=MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                Row([
                    IconButton(Icons.MENU, icon_color="white", on_click=lambda _: open_drawer()),
                    Text("Учет производства", color="white", size=title_size, weight=FontWeight.BOLD),
                ]),
                Row([
                    IconButton(Icons.PHONE_ANDROID, icon_color="white", on_click=toggle_mobile, tooltip="Переключить мобильный/ПК", visible=dev_tools_visible),
                    IconButton(Icons.REMOVE, icon_color="white", on_click=zoom_out, tooltip="Уменьшить", visible=dev_tools_visible),
                    IconButton(Icons.ADD, icon_color="white", on_click=zoom_in, tooltip="Увеличить", visible=dev_tools_visible),
                ])
            ],
            expand=True
        )

        filter_controls = [search_input, date_filter, year_dropdown, Button("Обновить", on_click=lambda _: refresh())]
        if is_mobile:
            filter_column = Column([
                Row([search_input], alignment=MainAxisAlignment.CENTER),
                Row([date_filter], alignment=MainAxisAlignment.CENTER),
                Row([year_dropdown], alignment=MainAxisAlignment.CENTER),
                Row([Button("Обновить", on_click=lambda _: refresh())], alignment=MainAxisAlignment.CENTER)
            ], spacing=10)
        else:
            filter_column = Row([
                search_input, date_filter, year_dropdown, Button("Обновить", on_click=lambda _: refresh())
            ], spacing=10, alignment=MainAxisAlignment.CENTER)

        balance_card = Container(
            padding=20,
            bgcolor="#5f4bdb",
            border_radius=15,
            content=Column([
                Text("Баланс", color="white", weight=FontWeight.BOLD, size=18),
                balance_text,
                income_text,
                outcome_text
            ], horizontal_alignment=CrossAxisAlignment.CENTER),
            alignment=Alignment(0, 0),
            height=300
        )

        categories_card = Container(
            padding=10,
            bgcolor=fg,
            border_radius=15,
            content=Column([
                Text("Категории", color="white", weight=FontWeight.BOLD, size=18),
                categories_column
            ], horizontal_alignment=CrossAxisAlignment.CENTER, scroll=ScrollMode.AUTO),
            alignment=Alignment(0, 0),
            height=300
        )

        if is_mobile:
            cards_section = Container(
                content=Column([
                    Container(
                        padding=20,
                        bgcolor="#5f4bdb",
                        border_radius=15,
                        content=Column([
                            Text("Баланс", color="white", weight=FontWeight.BOLD, size=18),
                            balance_text,
                            income_text,
                            outcome_text
                        ], horizontal_alignment=CrossAxisAlignment.CENTER, alignment=MainAxisAlignment.CENTER),
                        alignment=Alignment(0, 0),
                        expand=True
                    ),
                    Container(
                        padding=10,
                        bgcolor=fg,
                        border_radius=15,
                        content=Column([
                            Text("Категории", color="white", weight=FontWeight.BOLD, size=18),
                            categories_column
                        ], horizontal_alignment=CrossAxisAlignment.CENTER, scroll=ScrollMode.AUTO),
                        alignment=Alignment(0, 0),
                        expand=True,
                        height=300
                    )
                ], spacing=10, expand=True),
                alignment=Alignment(0, 0),
                expand=True
            )
        else:
            cards_section = Container(
                content=Row([
                    Container(
                        padding=20,
                        bgcolor="#5f4bdb",
                        border_radius=15,
                        content=Column([
                            Text("Баланс", color="white", weight=FontWeight.BOLD, size=18),
                            balance_text,
                            income_text,
                            outcome_text
                        ], horizontal_alignment=CrossAxisAlignment.CENTER, alignment=MainAxisAlignment.CENTER),
                        alignment=Alignment(0, 0),
                        expand=True,
                        height=300
                    ),
                    Container(
                        padding=10,
                        bgcolor=fg,
                        border_radius=15,
                        content=Column([
                            Text("Категории", color="white", weight=FontWeight.BOLD, size=18),
                            categories_column
                        ], horizontal_alignment=CrossAxisAlignment.CENTER, scroll=ScrollMode.AUTO),
                        alignment=Alignment(0, 0),
                        expand=True,
                        height=300
                    ),
                ], spacing=15, expand=True),
                alignment=Alignment(0, 0),
                padding=15,
                bgcolor=bg,
                expand=True
            )

        table_container = Container(
            padding=10,
            bgcolor=fg,
            border_radius=15,
            content=Row([
                Container(
                    content=table,
                    width=None
                )
            ], scroll=ScrollMode.AUTO),
            alignment=Alignment(0, 0)
        )

        totals_container = Container(
            padding=15,
            bgcolor="#2a2f77",
            border_radius=15,
            content=Column([
                Text("Итоги (выберите столбцы):", color="white", weight=FontWeight.BOLD, size=16),
                Row([
                    cb_sold, cb_made, cb_cost, cb_remainder, cb_profit
                ], wrap=True),
                total_text
            ]),
            alignment=Alignment(0, 0)
        )

        buttons_row = Container(
            content=Row([
                Button("Добавить", on_click=show_create),
                Button("Редактировать", on_click=show_edit),
                Button("Удалить", on_click=show_delete)
            ], wrap=True, spacing=10),
            alignment=Alignment(0, 0)
        )

        main_content = Column([
            Container(header, alignment=Alignment(0, 0)),
            Container(filter_column, alignment=Alignment(0, 0)),
            Container(cards_section, alignment=Alignment(0, 0)),
            Container(table_container, alignment=Alignment(0, 0)),
            Container(totals_container, alignment=Alignment(0, 0)),
            Container(buttons_row, alignment=Alignment(0, 0))
        ], spacing=15, alignment=MainAxisAlignment.CENTER, horizontal_alignment=CrossAxisAlignment.CENTER)

        centered_content = Container(
            content=main_content,
            alignment=Alignment(0, 0)
        )

        page.add(
            Container(
                content=ListView([centered_content]),
                alignment=Alignment(0, 0),
                expand=True
            )
        )

        def on_keyboard(e: KeyboardEvent):
            global dev_tools_visible
            if e.shift and e.key == "D":
                dev_tools_visible = not dev_tools_visible
                page.clean()
                show_main()

        page.on_keyboard_event = on_keyboard

        refresh()


    def show_create(e):
        page.clean()

        tf_width = None if is_mobile else None
        if not is_mobile:
            tf_width = 200

        def build_form(values=None):
            name = TextField(label="Название", value=values[0] if values else "", width=tf_width)
            size = TextField(label="Размер", value=values[1] if values else "", width=tf_width)
            material = TextField(label="Материал", value=values[2] if values else "", width=tf_width)
            price = TextField(label="Цена", value=values[3] if values else "", width=tf_width)
            sold = TextField(label="Продано", value=values[4] if values else "", width=tf_width)
            made = TextField(label="Изготовлено", value=values[5] if values else "", width=tf_width)
            mat_cost = TextField(label="Ст-сть мат-ов", value=values[6] if values else "", width=tf_width)
            time = TextField(label="Время", value=values[7] if values else "", width=tf_width)
            series = TextField(label="Серия", value=values[8] if values else "", width=tf_width)
            date = TextField(label="Дата", value=values[9] if values else "", width=tf_width)

            cost = TextField(label="Себестоимость", read_only=True)
            work = TextField(label="Изготовление", read_only=True)
            remainder = TextField(label="Остаток", read_only=True)
            profit = TextField(label="Прибыль", read_only=True)
            markup = TextField(label="Наценка %", read_only=True)

            def calc(e=None):
                s_val = to_float(sold.value)
                m_val = to_float(made.value)

                if s_val > m_val:
                    sold.error_text = "Ошибка: продано не может быть больше изготовлено"
                else:
                    sold.error_text = None

                c, w, r, p, mu = calc_values(
                    price.value, sold.value, made.value,
                    mat_cost.value, time.value
                )
                cost.value = str(round(c, 2))
                work.value = str(round(w, 2))
                remainder.value = str(round(r, 2))
                profit.value = str(round(p, 2))
                markup.value = str(round(mu, 2))
                page.update()

            for f in [price, sold, made, mat_cost, time]:
                f.on_change = calc

            calc()

            return (name, size, material, price, sold, made,
                    mat_cost, time, series, date,
                    cost, work, remainder, profit, markup)

        fields = build_form()

        def save(_):
            cursor.execute(
                "INSERT INTO products VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                [
                    fields[0].value, fields[1].value, fields[2].value, fields[3].value,
                    fields[4].value, fields[5].value,
                    0,
                    fields[6].value,
                    0,
                    fields[7].value,
                    fields[8].value,
                    fields[9].value,
                    0, 0, 0
                ]
            )
            conn.commit()
            show_main()

        page.add(Column([
            Text("Добавить", size=25, color="white"),
            *fields[:10],
            Divider(),
            Text("Расчёты", color="white"),
            *fields[10:],
            Row([
                Button("Сохранить", on_click=save),
                Button("Назад", on_click=lambda _: show_main())
            ])
        ], scroll=ScrollMode.AUTO))


    def show_edit(e):
        page.clean()

        tf_width = None if is_mobile else 200

        inp = TextField(label="№ строки", width=tf_width)

        def build_form(values=None):
            name = TextField(label="Название", value=values[0] if values else "", width=tf_width)
            size = TextField(label="Размер", value=values[1] if values else "", width=tf_width)
            material = TextField(label="Материал", value=values[2] if values else "", width=tf_width)
            price = TextField(label="Цена", value=values[3] if values else "", width=tf_width)
            sold = TextField(label="Продано", value=values[4] if values else "", width=tf_width)
            made = TextField(label="Изготовлено", value=values[5] if values else "", width=tf_width)
            mat_cost = TextField(label="Ст-сть мат-ов", value=values[6] if values else "", width=tf_width)
            time = TextField(label="Время", value=values[7] if values else "", width=tf_width)
            series = TextField(label="Серия", value=values[8] if values else "", width=tf_width)
            date = TextField(label="Дата", value=values[9] if values else "", width=tf_width)

            cost = TextField(label="Себестоимость", read_only=True)
            work = TextField(label="Изготовление", read_only=True)
            remainder = TextField(label="Остаток", read_only=True)
            profit = TextField(label="Прибыль", read_only=True)
            markup = TextField(label="Наценка %", read_only=True)

            return (name, size, material, price, sold, made,
                    mat_cost, time, series, date,
                    cost, work, remainder, profit, markup)

        def load(_):
            try:
                real_id = row_ids[int(inp.value) - 1]
                cursor.execute("SELECT * FROM products WHERE id=?", (real_id,))
                row = cursor.fetchone()

                values = [
                    row[1], row[2], row[3], row[4],
                    row[5], row[6], row[8], row[10],
                    row[11], row[12]
                ]

                fields = build_form(values)

                def save(_):
                    cursor.execute("""
                    UPDATE products SET
                    name=?, size=?, material=?, price=?, sold=?, made=?,
                    materials_cost=?, time=?, series=?, date=?
                    WHERE id=?
                    """, (
                        fields[0].value, fields[1].value, fields[2].value, fields[3].value,
                        fields[4].value, fields[5].value,
                        fields[6].value, fields[7].value,
                        fields[8].value, fields[9].value,
                        real_id
                    ))
                    conn.commit()
                    show_main()

                page.clean()
                page.add(Column([
                    Text("Редактировать", size=25, color="white"),
                    *fields[:10],
                    Divider(),
                    Text("Расчёты", color="white"),
                    *fields[10:],
                    Row([
                        Button("Сохранить", on_click=save),
                        Button("Назад", on_click=lambda _: show_main())
                    ])
                ], scroll=ScrollMode.AUTO))

            except:
                page.snack_bar = SnackBar(Text("Ошибка"), open=True)
                page.update()

        page.add(Column([
            inp,
            Button("Загрузить", on_click=load),
            Button("Назад", on_click=lambda _: show_main())
        ]))


    def show_delete(e):
        page.clean()

        tf_width = None if is_mobile else 200

        inp = TextField(label="№ строки", width=tf_width)

        def delete_row(_):
            try:
                real_id = row_ids[int(inp.value) - 1]
                cursor.execute("DELETE FROM products WHERE id=?", (real_id,))
                conn.commit()
                show_main()
            except:
                page.snack_bar = SnackBar(Text("Ошибка"), open=True)
                page.update()

        page.add(Column([
            inp,
            Row([
                Button("Удалить", on_click=delete_row),
                Button("Назад", on_click=lambda _: show_main())
            ], wrap=is_mobile)
        ]))


    show_main()


app(target=main)
