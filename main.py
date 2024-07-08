import flet as ft
import requests
from bs4 import BeautifulSoup


def main(page: ft.Page):
    page.title = "Login Simpel"
    page.bgcolor = "#ced4da"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    session = requests.Session()

    def create_login_view():
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        simpel = ft.Image(src="simpel.png", width=200, height=200)
        username_field = ft.TextField(
            label="Username",
            border_color=ft.colors.ORANGE,
            focused_border_color=ft.colors.ORANGE,
            filled=True,
        )
        garis = ft.Container(
            content=ft.Divider(color=ft.colors.ORANGE, thickness=2, height=5),
            expand=True,
        )
        password_field = ft.TextField(
            label="Password",
            password=True,
            border_color=ft.colors.ORANGE,
            focused_border_color=ft.colors.ORANGE,
            filled=True,
            can_reveal_password=True,
        )
        login_button = ft.ElevatedButton(
            text="Login",
            color=ft.colors.WHITE,
            bgcolor=ft.colors.ORANGE,
        )
        result_text = ft.Text()
        loading_ring = ft.ProgressRing(visible=False)

        def show_loading():
            loading_ring.visible = True
            login_button.disabled = True
            page.update()

        def hide_loading():
            loading_ring.visible = False
            login_button.disabled = False
            page.update()

        def login(e):
            show_loading()
            username = username_field.value
            password = password_field.value

            url = "https://simpel.ith.ac.id/"
            login_url = url + "login/index.php"

            response = session.get(login_url)
            soup = BeautifulSoup(response.text, "html.parser")
            logintoken_value = soup.find("input", {"name": "logintoken"})["value"]

            payload = {
                "logintoken": logintoken_value,
                "username": username,
                "password": password,
            }

            response = session.post(login_url, data=payload)
            soup = BeautifulSoup(response.text, "html.parser")
            check_login = soup.find("title").get_text()

            if check_login == "Dashboard":
                hide_loading()
                show_dashboard()
            else:
                result_text.value = "Login gagal. Silakan coba lagi."
                hide_loading()
                page.update()

        login_button.on_click = login
        kotak = kotak = ft.Container(
            bgcolor="white",
            padding=10,
            border_radius=10,
            width=300,
            height=600,
            content=ft.Column(
                [
                    ft.Image(
                        src="simpel.png",
                        width=200,
                        height=200,
                    ),
                    ft.Text(
                        "Login menggunakan akun simpel",
                        color="black",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    result_text,
                    username_field,
                    password_field,
                    ft.Row([garis, login_button, garis]),
                    ft.Row([loading_ring], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row([]),
                    ft.Text("Powered by Transhumanism3"),
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            shadow=ft.BoxShadow(
                color="black", offset=ft.Offset(0, 8), blur_radius=16, spread_radius=0
            ),
        )
        return kotak

    def create_dashboard_view():
        loading_ring = ft.ProgressRing(visible=False)
        result_text = ft.Text()
        task_list = ft.ExpansionPanelList(
            expand_icon_color=ft.colors.AMBER,
            elevation=8,
            divider_color=ft.colors.AMBER,
        )
        total = 0

        def on_scan_tugas(e):
            loading_ring.visible = True
            scan_button.disabled = True
            task_list.controls.clear()
            page.update()
            cek_tugas(e)

        scan_button = ft.ElevatedButton(
            "Scan Tugas", on_click=on_scan_tugas, icon=ft.icons.SEARCH
        )

        return ft.Column(
            [
                ft.Text("Selamat Datang", size=30, weight=ft.FontWeight.BOLD),
                scan_button,
                loading_ring,
                result_text,
                task_list,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            on_scroll=True,
        )

    def cek_tugas(e):
        url_course = "https://simpel.ith.ac.id/?redirect=0"
        response = session.get(url_course)
        soup = BeautifulSoup(response.text, "html.parser")
        course_links = []

        for link in soup.find_all("a", class_="aalink coursename mr-2 mb-1"):
            course_links.append((link["href"], link.text.strip()))

        data = {}
        for course_link, course_name in course_links:
            response = session.get(course_link)
            soup = BeautifulSoup(response.text, "html.parser")
            assignment_links = []

            for link in soup.find_all("a", class_="aalink stretched-link"):
                href = link["href"]
                if "https://simpel.ith.ac.id/mod/assign/view.php?" in href:
                    assignment_links.append(href)

            for assignment_link in assignment_links:
                response = session.get(assignment_link)
                soup = BeautifulSoup(response.text, "html.parser")
                verif = soup.find_all("td", class_="cell c1 lastcol")
                if verif and "No submissions have been made yet" in verif[0].text:
                    nama = soup.find_all("h1", class_="h2")
                    assignment_name = nama[0].text.strip()
                    if course_name not in data:
                        data[course_name] = {"link": course_link, "tugas": {}}
                    data[course_name]["tugas"][assignment_name] = assignment_link

        task_list = page.controls[-1].controls[-1]
        task_list.controls.clear()
        lv = ft.ListView(expand=True, spacing=10, padding=20, on_scroll=True)
        if data:
            for course_name, course_details in data.items():
                task_items = [
                    ft.TextButton(
                        text=f"- {assignment_name}",
                        url=assignment_link,
                        on_click=lambda e, url=assignment_link: ft.launch_url(url),
                    )
                    for assignment_name, assignment_link in course_details[
                        "tugas"
                    ].items()
                ]
                expansion_panel = ft.ExpansionTile(
                    title=ft.ListTile(title=ft.Text(course_name)),
                    controls=[
                        ft.Column(
                            task_items,
                            tight=True,
                            alignment=ft.MainAxisAlignment.START,
                        )
                    ],
                    expand=True,
                )
                lv.controls.append(expansion_panel)
        else:
            lv.controls.append(ft.Text("Tidak ada tugas yang belum dikerjakan."))

        # Update UI
        page.controls[-1].controls[1].disabled = False  # Enable scan button
        page.controls[-1].controls[2].visible = False  # Hide loading ring
        page.add(lv)
        page.update()

    def show_login():
        page.clean()
        page.add(create_login_view())
        page.update()

    def show_dashboard():
        page.clean()
        page.add(create_dashboard_view())
        page.update()

    show_login()


ft.app(target=main, assets_dir="assets")
