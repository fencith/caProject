import flet as ft

# 简单的 Flet 计数器应用
# - 显示一个数字计数器，通过浮动按钮点击递增
# - `counter.data` 用于保存数值，`counter.value` 用于显示文本

def main(page: ft.Page):
    # 创建用于显示计数的 Text 控件（初始为 "0"）
    counter = ft.Text("0", size=50, data=0)

    def increment_click(e):
        # 点击处理器：增加数据并更新显示文本
        counter.data += 1
        counter.value = str(counter.data)

    # 添加浮动操作按钮，点击时调用 increment_click
    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD, on_click=increment_click
    )

    # 使用 SafeArea + Container 将计数器居中显示
    page.add(
        ft.SafeArea(
            expand=True,
            content=ft.Container(
                content=counter,
                alignment=ft.Alignment.CENTER,
            ),
        )
    )


# 运行应用
ft.run(main)
