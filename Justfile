set shell := ["bash", "-c"]

[private]
@help:
  just --list

start:
  uv run src/main.py
