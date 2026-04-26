from flet import *
import sqlite3
import os
import shutil
import datetime

def log_msg(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {msg}"
    print(log_line)
    try:
        with open("app.log", "a", encoding="utf-8") as f:
            f.write(log_line + "\n")
    except Exception as e:
        print(f"LOG WRITE ERROR: {e}")

log_msg("App starting")

try:
    import tkinter as tk
    from tkinter import filedialog
    tk_support = True
except ImportError:
    tk_support = False

app_scale = 1.0
is_mobile = False
mobile_toggled = False
dev_tools_visible = False
current_page = "main"

drawer_open = False
drawer_panel = None
drawer_overlay = None
conn = None
cursor = None

def main(page: Page):
    global app_scale, is_mobile, mobile_toggled, conn, cursor

    log_msg(f"main started, page.platform={page.platform}, page.width={page.width}")

    bg = "#041955"
    fg = "#3450a1"

    page.bgcolor = bg
    page.padding = 0

    is_mobile = page.width < 600
    log_msg(f"is_mobile={is_mobile}")

    if conn:
        conn.close()
    conn = sqlite3.connect("data.db", check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        size TEXT,
        material TEXT,
        price REAL,
        sold REAL,
        made REAL,
        total REAL,
        materials_cost REAL,
        prod_cost REAL,
        time REAL,
        series TEXT,
        date TEXT,
        remainder REAL,
        remainder_rub REAL,
        markup REAL
    )
    """)
    conn.commit()

    def to_float(v):
        try:
            return float(v)
        except:
            return 0

    def get_year_from_date(date_str):
        if not date_str:
            return None
        parts = date_str.split('.')
        if len(parts) >= 3:
            try:
                return int(parts[2])
            except:
                return None
        return None

    def load_years():
        cursor.execute("SELECT DISTINCT date FROM products WHERE date IS NOT NULL")
        years = set()
        for (date,) in cursor.fetchall():
            y = get_year_from_date(date)
            if y:
                years.add(y)
        years = sorted(years, reverse=True)
        if not years:
            from datetime import datetime
            years = [datetime.now().year]
        year_dropdown.options = [DropdownOption(str(y)) for y in years]
        if year_dropdown.value is None or year_dropdown.value == "":
            year_dropdown.value = str(years[0])

    def calc_values(price, sold, made, mat_cost, time):
        p = to_float(price)
        s = to_float(sold)
        m = to_float(made)
        mat = to_float(mat_cost)
        t = to_float(time)

        work = t * 500
        cost = mat + work
        remainder = m - s
        profit = p - cost
        markup = (p / cost * 100) if cost != 0 else 0

        return cost, work, remainder, profit, markup

    row_ids = []

    balance_text = Text(color="white", size=28, weight=FontWeight.BOLD)
    income_text = Text(color="white")
    outcome_text = Text(color="white")

    search_input = TextField(label="Поиск", width=200)
    date_filter = TextField(label="Дата", width=150)
    year_dropdown = Dropdown(label="Год", width=120)

    table = DataTable(
        columns=[
            DataColumn(Text(c)) for c in [
                "№","Название","Размер","Материал","Цена",
                "Продано","Изготовлено","Ст-сть мат-ов",
                "Изготовление","Себестоимость","Время",
                "Серия","Дата","Остаток","Прибыль","Наценка %"
            ]
        ],
        rows=[]
    )

    categories_column = Column(scroll=ScrollMode.AUTO)

    cb_sold = Checkbox(label="Продано", on_change=lambda e: calc_total())
    cb_made = Checkbox(label="Изготовлено", on_change=lambda e: calc_total())
    cb_cost = Checkbox(label="Себестоимость", on_change=lambda e: calc_total())
    cb_remainder = Checkbox(label="Остаток", on_change=lambda e: calc_total())
    cb_profit = Checkbox(label="Прибыль", on_change=lambda e: calc_total())

    total_text = Text(color="white", size=16, weight=FontWeight.BOLD)

    def calc_total():
        total = 0
        for row in table.rows:
            cells = row.cells
            if cb_sold.value:
                total += to_float(cells[5].content.value)
            if cb_made.value:
                total += to_float(cells[6].content.value)
            if cb_cost.value:
                total += to_float(cells[9].content.value)
            if cb_remainder.value:
                total += to_float(cells[13].content.value)
            if cb_profit.value:
                total += to_float(cells[14].content.value)
        total_text.value = f"Итого: {round(total, 2)}"
        page.update()

    def load_data():
        table.rows.clear()
        row_ids.clear()

        search = search_input.value.lower() if search_input.value else ""
        date_f = date_filter.value if date_filter.value else ""
        selected_year = year_dropdown.value if year_dropdown.value else None

        query = "SELECT * FROM products"
        conditions = []
        params = []

        if search:
            conditions.append("(LOWER(name) LIKE ? OR LOWER(series) LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%"])
        if date_f:
            conditions.append("date LIKE ?")
            params.append(f"%{date_f}%")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        for i, row in enumerate(rows, start=1):
            if selected_year:
                y = get_year_from_date(row[12])
                if y != int(selected_year):
                    continue

            row_ids.append(row[0])

            cost, work, remainder, profit, markup = calc_values(
                row[4], row[5], row[6], row[8], row[10]
            )

            table.rows.append(
                DataRow(cells=[
                    DataCell(Text(str(i))),
                    DataCell(Text(str(row[1]))),
                    DataCell(Text(str(row[2]))),
                    DataCell(Text(str(row[3]))),
                    DataCell(Text(str(row[4]))),
                    DataCell(Text(str(row[5]))),
                    DataCell(Text(str(row[6]))),
                    DataCell(Text(str(row[8]))),
                    DataCell(Text(str(round(work, 2)))),
                    DataCell(Text(str(round(cost, 2)))),
                    DataCell(Text(str(row[10]))),
                    DataCell(Text(str(row[11]))),
                    DataCell(Text(str(row[12]))),
                    DataCell(Text(str(round(remainder, 2)))),
                    DataCell(Text(str(round(profit, 2)))),
                    DataCell(Text(str(round(markup, 2))))
                ])
            )

        calc_total()

    def update_balance():
        selected_year = year_dropdown.value if year_dropdown.value else None

        cursor.execute("SELECT price, sold, materials_cost, time, date FROM products")

        income = 0
        outcome = 0

        for p, s, m, t, d in cursor.fetchall():
            if selected_year:
                y = get_year_from_date(d)
                if y != int(selected_year):
                    continue

            p = to_float(p)
            s = to_float(s)
            m = to_float(m)
            t = to_float(t)

            work = t * 500
            cost = m + work

            income += p * s
            outcome += cost * s

        balance_text.value = f"{round(income - outcome, 2)} ₽"
        income_text.value = f"Доход: {round(income, 2)} ₽"
        outcome_text.value = f"Расход: {round(outcome, 2)} ₽"

    def update_categories():
        selected_year = year_dropdown.value if year_dropdown.value else None

        cursor.execute("SELECT series, name, price, materials_cost, sold, time, date FROM products")

        income_map = {}

        for series, name, price, mat, sold, time, d in cursor.fetchall():
            if selected_year:
                y = get_year_from_date(d)
                if y != int(selected_year):
                    continue

            price_f = to_float(price)
            sold_f = to_float(sold)
            mat_f = to_float(mat)
            time_f = to_float(time)

            work = time_f * 500
            cost = mat_f + work

            income = price_f * sold_f
            outcome = cost * sold_f
            markup = (price_f / cost * 100) if cost != 0 else 0

            if series not in income_map:
                income_map[series] = []

            income_map[series].append((name, income, outcome, markup))

        categories_column.controls.clear()

        for series, items in income_map.items():
            total_income = sum(i[1] for i in items)
            total_cost = sum(i[2] for i in items)
            avg_markup = sum(i[3] for i in items) / len(items) if items else 0

            categories_column.controls.append(
                Container(
                    padding=15,
                    bgcolor="#2a2f77",
                    border_radius=20,
                    content=Column([
                        Text(series, color="white", weight=FontWeight.BOLD),
                        Column([
                            Text(name, color="white70", size=12)
                            for name, _, _, _ in items
                        ]),
                        Divider(color="white24"),
                        Text(f"Доход: {round(total_income, 2)} ₽", color="green"),
                        Text(f"Себестоимость: {round(total_cost, 2)} ₽", color="red"),
                        Text(f"Наценка: {round(avg_markup, 2)}%", color="yellow")
                    ])
                )
            )

    def refresh():
        load_data()
        update_balance()
        update_categories()
        page.update()

    def show_main(bg="#041955", fg="#3450a1"):
        global app_scale, current_page, drawer_open, drawer_panel, drawer_overlay
        current_page = "main"
        page.controls.clear()
        page.overlay.clear()

        def export_db(_=None):
            log_msg("export_db CLICKED")
            page.snack_bar = SnackBar(Text("Экспорт БД: начало..."), open=True)
            page.update()
            log_msg("Snackbar shown")
            
            if drawer_panel:
                drawer_panel.left = -260
            if drawer_overlay:
                drawer_overlay.opacity = 0
                drawer_overlay.visible = False
            
            platform = page.platform
            log_msg(f"platform={platform}")
            page.snack_bar = SnackBar(Text(f"Платформа: {platform}"), open=True)
            page.update()
            
            if platform in ("android", "ios"):
                try:
                    import os
                    log_msg("Step 1: import os done")
                    page.snack_bar = SnackBar(Text("Шаг 1: проверка путей..."), open=True)
                    page.update()
                    
                    download_dir = "/storage/emulated/0/Download"
                    log_msg(f"download_dir={download_dir}, exists={os.path.exists(download_dir)}")
                    page.snack_bar = SnackBar(Text(f"Путь: {download_dir}"), open=True)
                    page.update()
                    
                    if not os.path.exists(download_dir):
                        download_dir = "/storage/emulated/0"
                        log_msg(f"Using alt: {download_dir}")
                    
                    dest_path = os.path.join(download_dir, "data_backup.db")
                    log_msg(f"dest_path={dest_path}")
                    
                    src_exists = os.path.exists("data.db")
                    log_msg(f"data.db exists={src_exists}")
                    page.snack_bar = SnackBar(Text(f"data.db есть: {src_exists}"), open=True)
                    page.update()
                    
                    if src_exists:
                        shutil.copy("data.db", dest_path)
                        log_msg("COPY DONE!")
                        page.snack_bar = SnackBar(Text(f"УСПЕХ: {dest_path}"), open=True)
                    else:
                        log_msg("data.db NOT FOUND")
                        page.snack_bar = SnackBar(Text("data.db не найден!"), open=True)
                    page.update()
                except Exception as ex:
                    import traceback
                    err = str(ex)
                    log_msg(f"ERROR: {err}")
                    log_msg(f"TB: {traceback.format_exc()}")
                    page.snack_bar = SnackBar(Text(f"ОШИБКА: {err[:50]}"), open=True)
                    page.update()
            elif tk_support:
                import tkinter as tk
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
            log_msg("import_db clicked")
            if drawer_panel:
                drawer_panel.left = -260
            if drawer_overlay:
                drawer_overlay.opacity = 0
                drawer_overlay.visible = False
            platform = page.platform
            log_msg(f"import_db called, platform={platform}")
            if platform in ("android", "ios"):
                try:
                    import os
                    log_msg("Starting import...")
                    possible_paths = [
                        "/storage/emulated/0/Download/data_backup.db",
                        "/storage/emulated/0/Download/data.db",
                        "/storage/emulated/0/data_backup.db",
                        "/storage/emulated/0/data.db",
                    ]
                    log_msg(f"Checking paths: {possible_paths}")
                    found_path = None
                    for p in possible_paths:
                        log_msg(f"Checking: {p}, exists={os.path.exists(p)}")
                        if os.path.exists(p):
                            found_path = p
                            break
                    
                    if found_path:
                        log_msg(f"Found: {found_path}")
                        shutil.copy(found_path, "data.db")
                        log_msg(f"DB imported from {found_path}")
                        page.snack_bar = SnackBar(Text(f"БД загружена из: {found_path}"), open=True)
                        page.update()
                        show_main()
                    else:
                        log_msg("No backup file found")
                        page.snack_bar = SnackBar(Text("Файл не найден. Положите файл в Download и назовите data_backup.db"), open=True)
                        page.update()
                except Exception as ex:
                    import traceback
                    log_msg(f"import_db error: {ex}")
                    log_msg(f"traceback: {traceback.format_exc()}")
                    page.snack_bar = SnackBar(Text(f"Ошибка: {ex}"), open=True)
                    page.update()
            elif tk_support:
                import tkinter as tk
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

        def show_logs_page():
            page.clean()
            log_content = ""
            try:
                with open("app.log", "r", encoding="utf-8") as f:
                    log_content = f.read()[-3000:]
            except:
                log_content = "Логов нет"
            page.add(Column([
                Text("Логи", size=25, color="white"),
                Container(
                    content=Text(log_content, size=10, color="white"),
                    bgcolor="#1a1a5e",
                    padding=10,
                    height=400,
                    width=page.width - 40 if page.width else 300
                ),
                Row([
                    Button("Экспорт", on_click=export_logs),
                    Button("Назад", on_click=lambda _: show_main())
                ])
            ]))
            log_msg("Logs page shown")

        def show_logs(_):
            log_msg("show_logs called")
            show_logs_page()

        def export_logs(_):
            log_msg("export_logs called")
            try:
                import os
                download_dir = "/storage/emulated/0/Download"
                if not os.path.exists(download_dir):
                    download_dir = "/storage/emulated/0"
                dest_path = os.path.join(download_dir, "app.log")
                with open("app.log", "r", encoding="utf-8") as f:
                    content = f.read()
                with open(dest_path, "w", encoding="utf-8") as f:
                    f.write(content)
                log_msg(f"Logs exported to {dest_path}")
                page.snack_bar = SnackBar(Text(f"Логи сохранены: {dest_path}"), open=True)
                page.update()
            except Exception as ex:
                log_msg(f"export_logs error: {ex}")
                page.snack_bar = SnackBar(Text(f"Ошибка: {ex}"), open=True)
                page.update()

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
                    subtitle=Text("Сохранить копию БД", color="white54", size=11),
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
                    leading=Icon(Icons.DESCRIPTION, color="white"),
                    title=Text("Показать логи", color="white"),
                    on_click=show_logs,
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
                Button("Удалить", on_click=show_delete),
                Button("Экспорт БД", on_click=export_db),
                Button("Импорт БД", on_click=import_db),
                Button("Логи", on_click=show_logs)
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

        tf_width = None
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

        tf_width = None
        if not is_mobile:
            tf_width = 200

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

        tf_width = None
        if not is_mobile:
            tf_width = 200

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