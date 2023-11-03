import csv
import os
import time

import flet as ft

from utils import tx_rx, find_usb_port_automatically

g_csv_file_path = ''
g_serial_port_str = ''


def _main(page: ft.Page):

    def _t(s, color=""):
        # logging
        lv.controls.append(ft.Text(str(s), size=20, color=color))
        page.update()
        print(str(s))

    def _te(s):
        return _t(s, color="red")

    def click_btn_clear_trace(_):
        lv.controls = []
        page.update()

    def _select_csv_file(e: ft.FilePickerResultEvent):
        if not e.files:
            _te('select a VCP CSV file')
            return
        if len(e.files) > 1:
            _te('select only one, please')
            return
        global g_csv_file_path
        g_csv_file_path = e.files[0].path
        _t(f'loaded file: {e.files[0].name}', color="green")

    def click_btn_select_csv_file(_):
        dialog_select_csv_file.on_result = _select_csv_file
        dialog_select_csv_file.pick_files(allow_multiple=False)
        page.update()

    def _send_file():
        # get the serial port
        p = g_serial_port_str

        # build list of times and voltages
        ls_t = []
        ls_mv = []
        with open(g_csv_file_path, 'r') as f:
            rd = csv.reader(f, delimiter=',')
            for i, row in enumerate(rd):
                if i == 0 and row != ['delta time (s)', 'voltage (mV)']:
                    _te('bad CSV header')
                    _te('must be "delta time (s),voltage (mV)"')
                    return
                if i:
                    t, mv = row
                    ls_t.append(int(t))
                    if int(mv) > 5000:
                        _te(f'bad voltage {mv} at row #{i+1}')
                        return
                    # the power supply wants AB.CD
                    mv = int(int(mv) / 10)
                    mv = str(mv).rjust(4, '0')
                    ls_mv.append(mv)

        _t('starting...')

        # output off
        tx_rx(p, 'SOUT0\r', b'OK\r')

        # set ABC normal mode
        tx_rx(p, 'SABC3\r', b'OK\r')

        # output on
        tx_rx(p, 'SOUT1\r', b'OK\r')

        # run through the lists
        for i, t in enumerate(ls_t):
            mv = ls_mv[i]
            _t(f'row #{i+1} sleep {t} set {int(mv) * 10} mV')
            time.sleep(t)
            s = 'SETD3{}0100\r'.format(mv)
            tx_rx(p, s, b'OK\rOK\r')

        # output off
        tx_rx(p, 'SOUT0\r', b'OK\r')

        _t('done')

    def click_btn_send_file(_):
        vp = '10c4:ea60'
        global g_serial_port_str
        g_serial_port_str = find_usb_port_automatically(vp)
        if not g_serial_port_str:
            _te('error: USB power supply not detected')
            return
        if not g_csv_file_path:
            _te('no CSV file chosen')
            return
        _t(f'found power supply port {g_serial_port_str}')
        s = os.path.basename(g_csv_file_path)
        _t(f'sent file: {s}', color="green")
        try:
            # -------------
            # send CSV file
            # -------------
            _send_file()
        except (Exception, ) as ex:
            _te(f'exception {str(ex)}')

    # ============
    # HTML layout
    # ============
    lv = ft.ListView(spacing=10, padding=20, auto_scroll=True, height=600)
    dialog_select_csv_file = ft.FilePicker()

    page.add(
        # this only shows when needed :)
        dialog_select_csv_file,
        ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            "Voltage Controlled Pressure Regulator",
                            style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=100,
                ),
                ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.icons.FILE_UPLOAD,
                            icon_color="blue400",
                            icon_size=60,
                            tooltip="load CSV file",
                            on_click=click_btn_select_csv_file,
                            expand=2
                        ),
                        ft.IconButton(
                            icon=ft.icons.PLAY_ARROW,
                            icon_color="blue400",
                            icon_size=60,
                            tooltip="start",
                            on_click=click_btn_send_file,
                            expand=2
                        ),
                        ft.IconButton(
                            icon=ft.icons.DELETE,
                            icon_color="red400",
                            icon_size=60,
                            tooltip="clear trace",
                            on_click=click_btn_clear_trace,
                            expand=2
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    [
                        lv
                    ]
                )
            ], spacing=25
        )
    )

    page.window_center()
    page.window_width = 1024
    page.window_height = 800
    _t('VCP started')


def main():
    ft.app(target=_main)
    # ft.app(target=_main, view=ft.WEB_BROWSER, assets_dir="assets")


if __name__ == "__main__":
    main()
