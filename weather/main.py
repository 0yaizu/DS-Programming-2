import flet as ft


def main(page: ft.Page):

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
    on_change=lambda e: print(f"選択されたインデックス: {e.control.selected_index}"),
		bgcolor=custom_color_scheme.background,
  )

	def create_home():
		return ft.View("/home", [
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
		],
		bgcolor=custom_color_scheme.background,
		)

	def create_view2():
		return ft.View("/view2", [
			ft.AppBar(
				title=ft.Text("view2"),
			),
			ft.TextField(value="view2"),
			ft.ElevatedButton(
				"Go to home", on_click=lambda _: page.go("/home")),
		])
	
	def create_404():
		return ft.View("/page_not_found", [
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
		])

	# ルート
	def route_change(handler):
		routes = {
			"/home": create_home(),
			"/page_not_found": create_404(),
			"/view2": create_view2(),
		}
		page.views.clear()
		try:
			page.views.append(routes[handler.route])
		except:
			page.views.append(routes["/page_not_found"])
		page.update()

	# ルート変更時のロジック設定
	page.on_route_change = route_change
	# Page レイアウト
	page.title = "Navigation and routing"
	# 初期表示
	page.go("/home")

if __name__ == "__main__":
	ft.app(target=main)