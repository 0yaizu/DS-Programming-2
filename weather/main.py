import flet as ft

def main(page: ft.Page):

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

	def create_home():
		return [
			ft.AppBar(
				title=ft.Text("Home"),
				# bgcolor=ft.colors.BLUE
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
		]

	def create_view2():
		return [
			ft.AppBar(
				title=ft.Text("view2"),
			),
			ft.TextField(value="view2"),
			ft.ElevatedButton(
				"Go to home", on_click=lambda _: page.go("/home")),
		]
	
	def create_404():
		return [
			ft.AppBar(
				title=ft.Text("Page not found!"),
				bgcolor=ft.colors.BLUE),
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
		]

	def create_search():
		return [
			ft.AppBar(
				title=ft.Text("Search"),
				bgcolor=ft.colors.BLUE),
			ft.Row(
				controls=[
					ft.Column(
						controls=[
							ft.Text("Search", size=50),
							ft.ElevatedButton(
								"Go back to home", on_click=lambda _: page.go("/home")
							),
						],
						alignment=ft.MainAxisAlignment.CENTER,
						horizontal_alignment=ft.CrossAxisAlignment.CENTER,
						expand=True,
					),
				],
				expand=True,
			),
			navigation_bar,
		]

	# ルート
	def route_change(handler):
		routes = {
			"/home": create_home(),
			"/page_not_found": create_404(),
			"/view2": create_view2(),
			"/search": create_search(),
		}
		page.controls.clear()
		try:
			page.add(*routes[handler.route][0:])
		except:
			page.add(*routes["/page_not_found"][0:])
		# page.update()

	# ルート変更時のロジック設定
	page.on_route_change = route_change
	# Page レイアウト
	page.title = "Navigation and routing"
	# 初期表示
	page.go("/home")

if __name__ == "__main__":
	ft.app(target=main)