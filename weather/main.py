import flet as ft
import requests, json, date

area_api_req = json.loads(requests.get("http://www.jma.go.jp/bosai/common/const/area.json").text)

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
		# print(json.dumps(req["centers"], indent=2, ensure_ascii=False))
		global area_api_req
		for center in area_api_req["centers"]:
			result.append(ft.ExpansionTile(
				title=ft.Text(area_api_req["centers"][center]["name"]),
				initially_expanded=False,
				controls_padding=ft.padding.only(left=20),
				controls=gen_offices_list(area_api_req["centers"][center]["children"]),
			))
		return result
	
	def gen_offices_list(center_children: list):
		result = []
		global area_api_req
		for office in center_children:
			result.append(ft.ExpansionTile(
				title=ft.Text(area_api_req["offices"][office]["name"]),
				initially_expanded=False,
				controls_padding=ft.padding.only(left=20),
				controls=gen_class10s_tile(area_api_req["offices"][office]["children"], office),
			))
		return result
	
	def gen_class10s_list(office_children: list):
		result = []
		global area_api_req
		for class10 in office_children:
			if len(office_children) == 1:
				result.append(ft.ExpansionTile(
				title=ft.Text(area_api_req["class10s"][class10]["name"]),
				initially_expanded=True,
				controls_padding=ft.padding.only(left=20),
				controls=gen_class15s_list(area_api_req["class10s"][class10]["children"]),
				))
			else:
				result.append(ft.ExpansionTile(
					title=ft.Text(area_api_req["class10s"][class10]["name"]),
					initially_expanded=False,
					controls_padding=ft.padding.only(left=20),
					controls=gen_class15s_list(area_api_req["class10s"][class10]["children"]),
				))
		return result

	def gen_class15s_list(class10_children: list):
		result = []
		global area_api_req
		for class15 in class10_children:
			result.append(ft.ExpansionTile(
				title=ft.Text(area_api_req["class15s"][class15]["name"]),
				initially_expanded=False,
				controls_padding=ft.padding.only(left=20),
				controls=gen_class20s_list(area_api_req["class15s"][class15]["children"]),
			))
		return result
	
	def gen_class20s_list(class15_children: list):
		result = []
		global area_api_req
		for class20 in class15_children:
			result.append(ft.ListTile(
				title=ft.Text(area_api_req["class20s"][class20]["name"]),
				on_click=lambda _: page.go("/create_search_result"),
			))
		return result
	
	def gen_offices_tile(center_children: list):
		result = []
		global area_api_req
		for office in center_children:
			result.append(ft.ListTile(
				title=ft.Text(area_api_req["offices"][office]["name"]),
				on_click=lambda _: go_to_search_result(office),
			))
		return result
	
	def gen_class10s_tile(office_children, office_id: list):
		result = []
		global area_api_req
		for n, class10 in enumerate(office_children):
			area_name = area_api_req["class10s"][class10]["name"]
			# area_list[office_id][class10][area_name] = n
			result.append(ft.ListTile(
				# print(f'{area_api_req["class10s"][class10]["name"]} / {n}'),
				title=ft.Text(area_name),
				on_click=lambda _: go_to_search_result(class10, office_id),
			))
		return result

	def gen_weekly_weather():
		result = []
		# ft.Text(f"Search Result: {target_office_id.value} -> {target_area_id.value}"),
		# ft.Text(f"Selected Index: {target_selected_index.value}"),
		try:
			req = json.loads(requests.get(f"https://www.jma.go.jp/bosai/forecast/data/forecast/{target_office_id.value}.json").text)
			target_index = 0
			print(req[1]["timeSeries"][0]["timeDefines"])
			# for area in req[1]["timeSeries"]["timeDefines"]["areas"]:
			# 	n = []
			# 	n.append(area["area"]["code"])
			# 	target_index = n.index(f"{target_area_id.value}")
			# 	print(f"target_index: {target_index}")
			for date in req[1]["timeSeries"][0]["timeDefines"]:
				result.append(ft.Text(date))
		except:
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
			ft.Row(
				controls=[
					# ft.Text(f"Search Result: {target_office_id.value} -> {target_area_id.value}"),
					# ft.Text(f"Selected Index: {target_selected_index.value}"),
					*gen_weekly_weather(),
				],
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