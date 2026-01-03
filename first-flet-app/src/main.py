import flet as ft

# Market watch app launcher — real-time indices & BOC USD/CNY
from . import market_watch


def main(page: ft.Page):
    market_watch.main(page)


if __name__ == '__main__':
    ft.app(target=market_watch.main)
