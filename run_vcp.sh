#!/usr/bin/bash


echo; echo; echo
printf '=== Launcher for Lowell Instruments Voltage Controlled Pressure === \n'
source "$HOME"/PycharmProjects/vcp/venv/bin/activate && \
"$HOME"/PycharmProjects/vcp/venv/bin/python "$HOME"/PycharmProjects/vcp/main.py
