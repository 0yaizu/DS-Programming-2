import flet as ft
import requests, json, datetime, sqlite3, os

area_api_req = json.loads(requests.get("http://www.jma.go.jp/bosai/common/const/area.json").text)

dbfile = f"{os.path.dirname(__file__)}/weather_data.db"

def db_init():
	conn = sqlite3.connect(dbfile)
	cur = conn.cursor()
	cur.execute("CREATE TABLE IF NOT EXISTS centers (id INTEGER PRIMARY KEY NOT NULL, name TEXT NOT NULL, en_name TEXT, office_name TEXT)")
	cur.execute("CREATE TABLE IF NOT EXISTS offices (id INTEGER PRIMARY KEY NOT NULL, name TEXT NOT NULL, en_name TEXT, center_id INTEGER NOT NULL, FOREIGN KEY (center_id) REFERENCES centers(id))")
	cur.execute("CREATE TABLE IF NOT EXISTS class10s (id INTEGER PRIMARY KEY NOT NULL, name TEXT NOT NULL, en_name TEXT, office_id INTEGER NOT NULL, FOREIGN KEY (office_id) REFERENCES offices(id))")
	conn.commit()
	conn.close()

# center, office, class10の情報を取得
def get_points():
	conn = sqlite3.connect(dbfile)
	cur = conn.cursor()
	for center in area_api_req["centers"]:
		# officeの情報をdatabaseに追加
		cur.execute("INSERT INTO centers (id, name, en_name) VALUES (?, ?, ?) ON CONFLICT(id) DO NOTHING", (center, area_api_req["centers"][center]["name"], area_api_req["centers"][center]["enName"]))
	
	# officeの情報をdatabaseに追加
	for office in area_api_req["offices"].keys():
		for center in area_api_req["centers"]:
			if office in area_api_req["centers"][center]["children"]:
				cur.execute("INSERT INTO offices (id, name, en_name, center_id) VALUES (?, ?, ?, ?) ON CONFLICT(id) DO NOTHING", (office, area_api_req["offices"][office]["name"], area_api_req["offices"][office]["enName"], center))
				break

	# class10の情報をdatabaseに追加
	for class10 in area_api_req["class10s"].keys():
		for office in area_api_req["offices"]:
			if class10 in area_api_req["offices"][office]["children"]:
				cur.execute("INSERT INTO class10s (id, name, en_name, office_id) VALUES (?, ?, ?, ?) ON CONFLICT(id) DO NOTHING", (class10, area_api_req["class10s"][class10]["name"], area_api_req["class10s"][class10]["enName"], office))
				break

	conn.commit()
	conn.close()

# 親IDから子IDのリストを取得
def get_children_id(paret_id: int, table: str = "offices" or "class10s"):
	search_column_name = ""
	if table == "offices": search_column_name = "center_id"
	elif table == "class10s": search_column_name = "office_id"
	conn = sqlite3.connect(dbfile)
	cur = conn.cursor()
	cur.execute(f"SELECT id FROM {table} WHERE {search_column_name} = {paret_id}")
	result = []
	for children in cur.fetchall():
		result.append(children[0])
	conn.close()
	return result

db_init()
get_points()

def main(page: ft.Page):

	target_area_id = ft.TextField(label="area_id", value=0)
	target_office_id = ft.TextField(label="area_id", value=0)
	target_selected_index = ft.TextField(label="selected_index", value=0)

	def go_to_search_result(value: int = 0, office_id: int = 0):
		target_area_id.value = value
		target_office_id.value = office_id
		page.go("/search_result")

	def change_page(pageid: int):
		if pageid == 0:
			page.go("/home")
		elif pageid == 1:
			page.go("/search")
		elif pageid == 2:
			page.go("/view2")

	custom_color_scheme = ft.ColorScheme(
		primary='#141417',
		background='#ffffff',
		# background='#838e9a',
	)

	page.window_bgcolor = ft.colors.AMBER,
	navigation_rail = ft.NavigationRail(
    selected_index=0,
    destinations=[
      ft.NavigationRailDestination(icon=ft.icons.HOME, label="ホーム"),
      ft.NavigationRailDestination(icon=ft.icons.SETTINGS, label="設定"),
      ft.NavigationRailDestination(icon=ft.icons.INFO, label="情報"),
    ],
    on_change=lambda e: print(f"選択されたインデックス: {e.control.selected_index}"),
		bgcolor=custom_color_scheme.background,
  )

	navigation_bar = ft.NavigationBar(
    destinations=[
      ft.NavigationDestination(icon=ft.icons.HOME, label="ホーム"),
      ft.NavigationDestination(icon=ft.icons.SEARCH, label="検索"),
      ft.NavigationDestination(icon=ft.icons.ACCOUNT_CIRCLE, label="アカウント"),
    ],
		offset=ft.transform.Offset(0, 0),
		animate_offset=ft.animation.Animation(0),
    on_change=lambda e: change_page(e.control.selected_index),
		bgcolor=custom_color_scheme.background,
  )
	
	def gen_center_list():
		result = []
		conn = sqlite3.connect(dbfile)
		cur = conn.cursor()
		cur.execute("SELECT id, name FROM centers")
		for center in cur.fetchall():
			# print(get_children_id(center[0], "offices"))
			result.append(ft.ExpansionTile(
				title=ft.Text(center[1]),
				initially_expanded=False,
				controls_padding=ft.padding.only(left=20),
				controls=gen_offices_list(get_children_id(center[0], "offices")),
			))
		conn.close()
		return result
	
	def gen_offices_list(center_children: list):
		result = []
		conn = sqlite3.connect(dbfile)
		cur = conn.cursor()
		for office in center_children:
			cur.execute(f"SELECT id, name FROM offices WHERE id = {office}")
			data = cur.fetchone()
			result.append(ft.ExpansionTile(
				title=ft.Text(data[1]),
				initially_expanded=False,
				controls_padding=ft.padding.only(left=20),
				controls=gen_class10s_tile(get_children_id(data[0], "class10s"), office),
			))
		conn.close()
		return result
	
	def gen_class10s_tile(office_children: list, office_id: int = 0):
		result = []
		conn = sqlite3.connect(dbfile)
		cur = conn.cursor()
		for class10 in office_children:
			cur.execute(f"SELECT name FROM class10s WHERE id = {class10}")
			data = cur.fetchone()
			result.append(ft.ListTile(
				title=ft.Text(data[0]),
				on_click=lambda _: go_to_search_result('0' * (6 - len(str(class10))) + str(class10), '0' * (6 - len(str(office_id))) + str(office_id)),
			))
		conn.close()
		return result

	# 天気データ取得->DBに格納
	def get_weather_data():
		try:
			conn = sqlite3.connect(dbfile)
			cur = conn.cursor()
			cur.execute(f"SELECT * FROM class10s WHERE id = {target_area_id.value}")
			if cur.fetchone() != None:
				cur.execute(f"CREATE TABLE IF NOT EXISTS days_weather_{target_area_id.value} (date TEXT PRIMARY KEY NOT NULL, min_temp INTEGER, max_temp INTEGER, pops INTEGER, weather INTEGER, wind_dir INT, wind_power INTEGER , FOREIGN KEY (weather) REFERENCES weather_types(id), FOREIGN KEY (wind_dir) REFERENCES wind_directions(id))")

			req = requests.get(f"https://www.jma.go.jp/bosai/forecast/data/forecast/{target_office_id.value}.json", timeout=100)
			req_json = json.loads(req.text)
			weeks = req_json[1]["timeSeries"][0]
			weeks_date = weeks["timeDefines"]
			temp = req_json[1]["timeSeries"][1]["areas"]
			area_codes = []
			for area in weeks["areas"]:
				area_codes.append(area["area"]["code"])
			area_index = area_codes.index(f'{target_area_id.value}')

			for i in range(len(weeks_date)):
				date = weeks_date[i]
				pops = weeks["areas"][area_index]["pops"][i]
				min_temp = temp[area_index]["tempsMin"][i]
				max_temp = temp[area_index]["tempsMax"][i]
				cur.execute(f"INSERT INTO days_weather_{target_area_id.value} (date, min_temp, max_temp, pops) VALUES (?, ?, ?, ?) ON CONFLICT(date) DO UPDATE SET min_temp = ?, max_temp = ?, pops = ?", (date, min_temp, max_temp, pops, min_temp, max_temp, pops))
			conn.commit()
			conn.close()
		except:
			print("Error")

	def gen_weekly_weather():
		get_weather_data()
		result = []
		# ft.Text(f"Search Result: {target_office_id.value} -> {target_area_id.value}"),
		# ft.Text(f"Selected Index: {target_selected_index.value}"),
		try:
			print(target_office_id.value)
			conn = sqlite3.connect(dbfile)
			cur = conn.cursor()
			cur.execute(f"SELECT date, min_temp, max_temp, pops FROM days_weather_{target_area_id.value} ORDER BY date DESC LIMIT 7")
			select_result = cur.fetchall()
			print(select_result)
			for data in select_result:
				print(data)
				if data[1] == "": min_temp = "N/A"
				else: min_temp = data[1]
				if data[2] == "": max_temp = "N/A"
				else: max_temp = data[2]
				if data[3] == "": pop = "N/A"
				else: pop = data[3]
				result.append(ft.Column(
					controls=[
						ft.Text(f"{data[0][5:7]} / {data[0][8:10]}"),
						ft.Text(f"降水確率: {pop}%"),
						ft.Row(
							controls=[
								ft.Text(f"{min_temp}", color="#0000ff"),
								ft.Text(" / ", color="#000000"),
								ft.Text(f"{max_temp}", color="#ff0000"),
							],
						)
					],
					horizontal_alignment=ft.CrossAxisAlignment.CENTER,
				))
			conn.close()

		except Exception as e:
			print(e)
			result.append(ft.Text("No data available"))
		return result

	def create_home():
		return ft.View("/home", [
			ft.AppBar(
				title=ft.Text("Home", color="#ffffff"),
				bgcolor="#838e9a",
			),
			ft.Row(
				controls=[
					navigation_rail,
					ft.VerticalDivider(width=1),
					ft.Column(
						controls=[
							ft.TextField(value="view1"),
							ft.ElevatedButton(
								text="Go to view2",
								on_click=lambda _:
									page.go("/view2"),
							),
						],
						expand=True,
					)
				],
				expand=True,
			),
			navigation_bar,
			])

	def create_view2():
		return ft.View("/view2", [
			ft.AppBar(
				title=ft.Text("view2", color="#ffffff"),
				bgcolor="#838e9a",
			),
			ft.TextField(value="view2"),
			ft.ElevatedButton(
				"Go to home", on_click=lambda _: page.go("/home")),
		])
	
	def create_404():
		return ft.View("/page_not_found", [
			ft.AppBar(
				title=ft.Text("Page not found!", color="#ffffff"),
				bgcolor="#838e9a",
				),
			ft.Row(
				controls=[
					ft.Column(
						controls=[
							ft.Text("404 Not found", size=50),
							ft.ElevatedButton(
								"Go back to home", on_click=lambda _: page.go("/home")
							),
						],
						alignment=ft.MainAxisAlignment.CENTER,
						horizontal_alignment=ft.CrossAxisAlignment.CENTER,
					),
				],
				expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
			),
			navigation_bar,
		])

	def create_search():
		return ft.View("/search", [
			ft.AppBar(
				title=ft.Text("Search", color="#ffffff"),
				bgcolor= "#838e9a"
			),
			ft.Row(
				controls=[
					ft.Column(
						controls=[
							ft.Row(
								controls=[
									ft.TextField(
										text_size=15,
										suffix_icon=ft.icons.SEARCH,
										tooltip="Search",
										width=500,
									),
									ft.IconButton(
										icon=ft.icons.REPLAY,
										tooltip="Reload",
									),
									ft.IconButton(
										icon=ft.icons.INFO,
										tooltip="How to use",
									),
								],
								vertical_alignment=ft.CrossAxisAlignment.CENTER,
								alignment=ft.MainAxisAlignment.CENTER,
							),
							ft.Column(
								controls=[
									ft.ExpansionTile(
									title=ft.Text("地方から探す"),
									controls=gen_center_list(),
									initially_expanded=True,
									controls_padding=ft.padding.only(left=20),
									),
								],
        				scroll=ft.ScrollMode.ALWAYS,
								expand=True,
							),
						],
						alignment=ft.MainAxisAlignment.START,
						expand=True,
					),
				],
				expand=True,
			),
			navigation_bar,
		])

	def create_search_result():
		return ft.View("/search_result", [
			ft.AppBar(
				title=ft.Text("Search Result", color="#ffffff"),
				bgcolor= "#838e9a"
			),
			ft.Text("週間天気予報", size=20),
			ft.Container(
				margin=ft.Margin(top=0, bottom=0, left=100, right=100),
				content=ft.Row(
					controls=gen_weekly_weather(),
					alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
					expand=True,
				),
			),
			navigation_bar,
		])

	# ルート
	def route_change(handler):
		routes = {
			"/home": create_home(),
			"/page_not_found": create_404(),
			"/view2": create_view2(),
			"/search": create_search(),
			"/search_result": create_search_result(),
		}
		page.views.clear()
		try:
			page.views.append(routes[handler.route])
		except:
			page.views.append(routes["/page_not_found"])
		page.update()

	# page theme
	page.theme = ft.Theme(
		page_transitions=ft.PageTransitionsTheme(
			android=ft.PageTransitionTheme.NONE,
			ios=ft.PageTransitionTheme.NONE,
			macos=ft.PageTransitionTheme.NONE,
			linux=ft.PageTransitionTheme.NONE,
			windows=ft.PageTransitionTheme.NONE,
		),
	)
	# ルート変更時のロジック設定
	page.on_route_change = route_change
	# Page レイアウト
	page.title = "Weather "
	# 初期表示
	page.go("/home")

if __name__ == "__main__":
	ft.app(target=main)