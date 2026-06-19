#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Steam Game Checker — десктопное приложение (PyQt6).
Точка входа для сборки .exe (PyInstaller).
"""
from __future__ import annotations

import html
import json
import os
import sys
from typing import List, Optional

from PyQt6.QtCore import QObject, QRunnable, QSize, Qt, QThread, QThreadPool, QTimer, QUrl, pyqtSignal
from PyQt6.QtGui import QAction, QDesktopServices, QFont
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QDoubleSpinBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

import steam_core as sc

LOG_COLORS = {
    "info": "#9eceff",
    "ok": "#9ece6a",
    "err": "#f7768e",
    "warn": "#e0af68",
    "dim": "#565f89",
    "title": "#7dcfff",
}


def apply_dark_theme(app: QApplication) -> None:
    app.setStyle("Fusion")
    app.setStyleSheet(
        """
        QWidget { background-color: #1a1b26; color: #c0caf5; font-size: 13px; }
        QFrame#topNav {
            background-color: #16161e;
            border-bottom: 1px solid #3b4261;
            min-height: 44px;
            max-height: 48px;
        }
        QLabel#navBrand {
            color: #7aa2f7;
            font-weight: 700;
            font-size: 14px;
            letter-spacing: 0.5px;
        }
        QToolButton#navMenuBtn {
            background-color: transparent;
            color: #c0caf5;
            border: 1px solid transparent;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 600;
            font-size: 13px;
            margin: 0 2px;
        }
        QToolButton#navMenuBtn:hover {
            background-color: #24283b;
            border-color: #414868;
            color: #e0e6ff;
        }
        QToolButton#navMenuBtn:pressed {
            background-color: #1f2335;
            border-color: #3b4261;
        }
        QToolButton#navMenuBtn::menu-indicator { width: 0px; height: 0px; image: none; }
        QMenu {
            background-color: #16161e;
            color: #c0caf5;
            border: 1px solid #3b4261;
            border-radius: 10px;
            padding: 6px 4px;
        }
        QMenu::item {
            padding: 10px 36px 10px 16px;
            border-radius: 6px;
            margin: 2px 4px;
        }
        QMenu::item:selected {
            background-color: #3d59a1;
            color: #e0e6ff;
        }
        QMenu::item:pressed {
            background-color: #2b3f73;
        }
        QMenu::separator {
            height: 1px;
            background: #3b4261;
            margin: 6px 12px;
        }
        QGroupBox {
            font-weight: 600;
            border: 1px solid #3b4261;
            border-radius: 8px;
            margin-top: 12px;
            padding: 14px 10px 10px 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 6px;
            color: #7aa2f7;
        }
        QLineEdit, QTextEdit, QListWidget {
            background-color: #16161e;
            border: 1px solid #3b4261;
            border-radius: 6px;
            padding: 8px;
            selection-background-color: #7aa2f7;
            selection-color: #1a1b26;
        }
        QCheckBox { spacing: 8px; }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 1px solid #565f89;
            background: #16161e;
        }
        QCheckBox::indicator:checked {
            background: #3d59a1;
            border-color: #7aa2f7;
        }
        QDoubleSpinBox {
            background-color: #16161e;
            border: 1px solid #3b4261;
            border-radius: 6px;
            padding: 6px 10px;
            min-height: 22px;
        }
        QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
            width: 22px;
            border-left: 1px solid #3b4261;
            background: #24283b;
            border-radius: 0px;
        }
        QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
            background: #3b4261;
        }
        QPushButton {
            background-color: #3d59a1;
            color: #c0caf5;
            border: none;
            border-radius: 6px;
            padding: 10px 18px;
            font-weight: 600;
        }
        QPushButton:hover { background-color: #4e6bb3; }
        QPushButton:pressed { background-color: #2b3f73; }
        QPushButton#secondary {
            background-color: #414868;
        }
        QPushButton#secondary:hover { background-color: #565f89; }
        QPushButton#danger { background-color: #883d4e; }
        QPushButton#danger:hover { background-color: #a44d62; }
        QLabel#title {
            font-size: 22px;
            font-weight: 700;
            color: #7aa2f7;
        }
        QLabel#subtitle { color: #a9b1d6; font-size: 12px; }
        QScrollArea { border: none; }
        QSplitter::handle {
            background: #3b4261;
            width: 4px;
            border-radius: 2px;
            margin: 2px 0;
        }
        QSplitter::handle:hover { background: #7aa2f7; }
        """
    )


class CheckWorker(QObject):
    log_msg = pyqtSignal(str, str)
    finished_ok = pyqtSignal(list, list)
    failed = pyqtSignal(str)

    def __init__(
        self,
        api_key: str,
        accounts: List[str],
        games: List[str],
        delay: float,
    ):
        super().__init__()
        self.api_key = api_key
        self.accounts = accounts
        self.games = games
        self.delay = delay

    def run(self) -> None:
        try:
            def log_fn(msg: str, kind: str = "info") -> None:
                self.log_msg.emit(msg, kind)

            summary = sc.run_check(
                self.api_key,
                self.accounts,
                self.games,
                log_fn=log_fn,
                request_delay=self.delay,
            )
            self.finished_ok.emit(summary, sc.sort_game_names(self.games))
        except Exception as e:
            self.failed.emit(f"{type(e).__name__}: {e}")


class _StoreSearchSignals(QObject):
    """Сигналы из пула потоков → главный поток GUI (только примитивы Qt)."""

    done = pyqtSignal(int, str)  # seq, json.dumps(список игр)
    error = pyqtSignal(int, str)


class _StoreSearchRunnable(QRunnable):
    def __init__(self, term: str, seq: int, sigs: _StoreSearchSignals) -> None:
        super().__init__()
        self._term = term
        self._seq = seq
        self._sigs = sigs

    def run(self) -> None:
        try:
            apps = sc.store_search_apps(self._term)
        except Exception as e:
            self._sigs.error.emit(self._seq, str(e))
            return
        self._sigs.done.emit(self._seq, json.dumps(apps, ensure_ascii=False))


class SteamStoreSearchDialog(QDialog):
    """Поиск и выбор игры через API магазина Steam (как на витрине)."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Магазин Steam — поиск игры")
        self.setMinimumSize(780, 600)
        self._selected_name: Optional[str] = None
        self._closing = False

        self.setStyleSheet(
            """
            QDialog { background-color: #1b2838; color: #c6d4df; }
            QLabel { color: #c6d4df; }
            QLineEdit {
                background-color: #16202d;
                color: #dbe4ea;
                border: 1px solid #2a475e;
                border-radius: 3px;
                padding: 10px 12px;
                font-size: 15px;
            }
            QPushButton {
                background-color: #799905;
                color: #d2e885;
                border: 1px solid #536904;
                border-radius: 3px;
                padding: 10px 22px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #8cb108; color: #1b2838; }
            QListWidget {
                background-color: #16202d;
                border: 1px solid #2a475e;
                border-radius: 3px;
                padding: 6px;
                outline: none;
            }
            QListWidget::item {
                padding: 6px 8px;
                min-height: 28px;
                border-radius: 2px;
            }
            QListWidget::item:selected {
                background-color: #2a475e;
                border: 1px solid #66c0f4;
            }
            QListWidget::item:hover { background-color: #1f3347; }
            """
        )

        lay = QVBoxLayout(self)
        lay.setSpacing(12)

        hint = QLabel(
            "Введите запрос — как в строке поиска Steam. Выберите строку и нажмите "
            "«Добавить выбранную» или двойной щелчок."
        )
        hint.setWordWrap(True)
        lay.addWidget(hint)

        row = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Поиск в магазине Steam…")
        self.search_edit.returnPressed.connect(self._schedule_search)
        btn_find = QPushButton("Найти")
        btn_find.clicked.connect(self._schedule_search)
        row.addWidget(self.search_edit, 1)
        row.addWidget(btn_find)
        lay.addLayout(row)

        self.results = QListWidget()
        self.results.setIconSize(QSize(1, 1))
        self.results.itemDoubleClicked.connect(lambda _it: self._accept_selection())
        lay.addWidget(self.results, 1)

        self.status_lbl = QLabel("")
        self.status_lbl.setStyleSheet("color: #8f98a0;")
        lay.addWidget(self.status_lbl)

        bb = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        ok_btn = bb.button(QDialogButtonBox.StandardButton.Ok)
        if ok_btn is not None:
            ok_btn.setText("Добавить выбранную")
        bb.accepted.connect(self._accept_selection)
        bb.rejected.connect(self.reject)
        lay.addWidget(bb)

        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.timeout.connect(self._schedule_search)
        self.search_edit.textChanged.connect(self._on_search_text_changed)

        self._search_seq = 0
        self._search_sigs = _StoreSearchSignals(self)
        self._search_sigs.done.connect(
            self._on_store_search_done, Qt.ConnectionType.QueuedConnection
        )
        self._search_sigs.error.connect(
            self._on_store_search_error, Qt.ConnectionType.QueuedConnection
        )

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self._closing = True
        self._search_seq += 1
        self._debounce.stop()
        try:
            self._search_sigs.done.disconnect(self._on_store_search_done)
            self._search_sigs.error.disconnect(self._on_store_search_error)
        except TypeError:
            pass
        super().closeEvent(event)

    def _on_search_text_changed(self) -> None:
        t = self.search_edit.text().strip()
        if len(t) < 2:
            self._debounce.stop()
            self.results.clear()
            self.status_lbl.clear()
            self._search_seq += 1
            return
        self._debounce.stop()
        self._debounce.start(700)

    def _schedule_search(self) -> None:
        term = self.search_edit.text().strip()
        if len(term) < 2:
            self.status_lbl.setText("Введите минимум 2 символа.")
            return
        self._search_seq += 1
        seq = self._search_seq
        self.results.clear()
        self.status_lbl.setText("Поиск…")
        pool = QThreadPool.globalInstance()
        pool.start(_StoreSearchRunnable(term, seq, self._search_sigs))

    def _on_store_search_done(self, seq: int, payload: str) -> None:
        if self._closing or seq != self._search_seq:
            return
        try:
            apps = json.loads(payload) if payload else []
        except json.JSONDecodeError:
            return
        if not isinstance(apps, list):
            return
        try:
            if not apps:
                self.status_lbl.setText("Ничего не найдено. Уточните запрос.")
                return
            self.status_lbl.setText(f"Найдено: {len(apps)}")
            for app in apps:
                if not isinstance(app, dict):
                    continue
                name = app.get("name")
                aid = app.get("appid")
                if not isinstance(name, str) or not name.strip():
                    continue
                item = QListWidgetItem(name.strip())
                item.setData(Qt.ItemDataRole.UserRole, aid)
                item.setToolTip(
                    f"AppID: {aid}\n{name.strip()}\n"
                    f"(точное имя для проверки библиотеки)"
                )
                self.results.addItem(item)
        except RuntimeError:
            return

    def _on_store_search_error(self, seq: int, msg: str) -> None:
        if self._closing or seq != self._search_seq:
            return
        try:
            self.status_lbl.setText("Ошибка сети или Steam. Повторите позже.")
            self.results.clear()
        except RuntimeError:
            return

    def _accept_selection(self) -> None:
        item = self.results.currentItem()
        if item is None:
            QMessageBox.warning(
                self, "Выбор", "Выберите игру в списке (один щелчок по строке)."
            )
            return
        self._selected_name = item.text()
        self.accept()

    def selected_name(self) -> Optional[str]:
        return self._selected_name


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._thread: Optional[QThread] = None
        self._worker: Optional[CheckWorker] = None

        self.setWindowTitle("Steam Game Checker")
        self.setMinimumSize(880, 620)
        self._build_top_nav()
        self._build_ui()
        self._load_settings()

    def _build_top_nav(self) -> None:
        """Встроенная панель меню (не нативный QMenuBar) — стабильно на Windows."""
        nav = QFrame()
        nav.setObjectName("topNav")
        nav.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        lay = QHBoxLayout(nav)
        lay.setContentsMargins(14, 8, 14, 8)
        lay.setSpacing(6)

        brand = QLabel("Steam Game Checker")
        brand.setObjectName("navBrand")
        lay.addWidget(brand)
        lay.addStretch(1)

        def nav_button(label: str) -> QToolButton:
            b = QToolButton()
            b.setObjectName("navMenuBtn")
            b.setText(label)
            b.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setAutoRaise(True)
            return b

        btn_file = nav_button("Файл  ▾")
        m_file = QMenu(self)
        m_file.setToolTipsVisible(True)
        a_res = QAction("Открыть папку результатов", self)
        a_res.setStatusTip("steam_results рядом с программой")
        a_res.triggered.connect(self._open_results)
        m_file.addAction(a_res)
        a_acc = QAction("Открыть accounts.txt", self)
        a_acc.triggered.connect(self._open_accounts)
        m_file.addAction(a_acc)
        btn_file.setMenu(m_file)
        lay.addWidget(btn_file)

        self.setMenuWidget(nav)

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        left = QWidget()
        left.setMinimumWidth(300)
        left.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        left_l = QVBoxLayout(left)
        left_l.setContentsMargins(0, 0, 8, 0)

        grp_key = QGroupBox("Steam Web API")
        gk = QVBoxLayout(grp_key)
        row = QHBoxLayout()
        self.api_edit = QLineEdit()
        self.api_edit.setPlaceholderText("Ключ с https://steamcommunity.com/dev/apikey")
        self.api_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.show_key = QCheckBox("Показать")
        self.show_key.toggled.connect(
            lambda on: self.api_edit.setEchoMode(
                QLineEdit.EchoMode.Normal
                if on
                else QLineEdit.EchoMode.Password
            )
        )
        row.addWidget(self.api_edit, 1)
        row.addWidget(self.show_key)
        gk.addLayout(row)
        btn_save = QPushButton("Сохранить ключ")
        btn_save.clicked.connect(self._save_api_key)
        gk.addWidget(btn_save)
        left_l.addWidget(grp_key)

        grp_delay = QGroupBox("Задержка между запросами, в секундах")
        gd = QHBoxLayout(grp_delay)
        self.spin_delay = QDoubleSpinBox()
        self.spin_delay.setRange(0.5, 15.0)
        self.spin_delay.setSingleStep(0.1)
        self.spin_delay.setValue(sc.REQUEST_DELAY)
        gd.addWidget(self.spin_delay)
        gd.addStretch()
        left_l.addWidget(grp_delay)

        grp_games = QGroupBox("Игры для проверки (только точное имя как в Steam)")
        gg = QVBoxLayout(grp_games)
        hint = QLabel(
            "Добавьте игру через поиск магазина Steam "
            "или введите имя / псевдоним вручную."
        )
        hint.setWordWrap(True)
        hint.setObjectName("subtitle")
        gg.addWidget(hint)

        row_store = QHBoxLayout()
        btn_store = QPushButton("Поиск как в магазине Steam…")
        btn_store.setMinimumHeight(40)
        btn_store.clicked.connect(self._open_steam_store_search)
        row_store.addWidget(btn_store)
        row_store.addStretch()
        gg.addLayout(row_store)

        gg.addWidget(QLabel("Точное имя вручную (как в Steam) или псевдоним:"))
        row_g = QHBoxLayout()
        self.game_input = QLineEdit()
        self.game_input.setPlaceholderText(
            "Имя игры в Steam или похожее её название (например: Rust, кс го, дота)"
        )
        btn_add_g = QPushButton("Добавить")
        btn_add_g.clicked.connect(self._add_games)
        row_g.addWidget(self.game_input, 1)
        row_g.addWidget(btn_add_g)
        gg.addLayout(row_g)

        gg.addWidget(QLabel("Игры к проверке:"))
        self.list_games = QListWidget()
        self.list_games.setMinimumHeight(140)
        gg.addWidget(self.list_games)
        row_rm = QHBoxLayout()
        btn_sort_g = QPushButton("По алфавиту А-Я")
        btn_sort_g.setObjectName("secondary")
        btn_sort_g.setToolTip("Сортировать список игр по названию")
        btn_sort_g.clicked.connect(self._sort_games_list)
        btn_rm_g = QPushButton("Удалить выбранные")
        btn_rm_g.setObjectName("secondary")
        btn_rm_g.clicked.connect(self._remove_selected_games)
        row_rm.addWidget(btn_sort_g)
        row_rm.addWidget(btn_rm_g)
        row_rm.addStretch()
        gg.addLayout(row_rm)
        left_l.addWidget(grp_games)

        grp_acc = QGroupBox("Аккаунты Steam")
        ga = QVBoxLayout(grp_acc)
        self.text_accounts = QTextEdit()
        self.text_accounts.setPlaceholderText(
            "По одному аккаунту на строку: nickname, SteamID64, или URL профиля"
        )
        self.text_accounts.setMinimumHeight(160)
        ga.addWidget(self.text_accounts)
        row_a = QHBoxLayout()
        btn_load = QPushButton("Загрузить из accounts.txt")
        btn_load.setObjectName("secondary")
        btn_load.clicked.connect(self._load_accounts_file)
        row_a.addWidget(btn_load)
        row_a.addStretch()
        ga.addLayout(row_a)
        left_l.addWidget(grp_acc)

        row_run = QHBoxLayout()
        self.btn_run = QPushButton("Начать проверку")
        self.btn_run.clicked.connect(self._start_check)
        self.btn_run.setMinimumHeight(44)
        btn_clear = QPushButton("Очистить лог")
        btn_clear.setObjectName("secondary")
        btn_clear.clicked.connect(self._clear_log)
        row_run.addWidget(self.btn_run, 1)
        row_run.addWidget(btn_clear)
        left_l.addLayout(row_run)

        left_l.addStretch()

        right = QWidget()
        right.setMinimumWidth(260)
        right.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        rl = QVBoxLayout(right)
        rl.setContentsMargins(8, 0, 0, 0)
        log_label = QLabel("Журнал")
        log_label.setStyleSheet("font-weight:600;color:#7aa2f7;")
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setFont(QFont("Consolas", 10))
        self.log.setMinimumWidth(200)
        rl.addWidget(log_label)
        rl.addWidget(self.log, 1)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([620, 420])
        root.addWidget(splitter, 1)

    def _append_log(self, msg: str, kind: str = "info") -> None:
        color = LOG_COLORS.get(kind, LOG_COLORS["info"])
        esc = html.escape(msg).replace("\n", "<br>")
        self.log.append(f'<span style="color:{color}">{esc}</span>')

    def _clear_log(self) -> None:
        self.log.clear()

    def _load_settings(self) -> None:
        sc.ensure_dir(sc.OUTPUT_DIR)
        sc.create_accounts_template()
        cfg = sc.load_config()
        self.api_edit.setText((cfg or {}).get("api_key") or "")
        self._append_log("Ready.", "ok")

    def _save_api_key(self) -> None:
        key = self.api_edit.text().strip()
        cfg = sc.load_config()
        cfg["api_key"] = key
        sc.save_config(cfg)
        QMessageBox.information(self, "Saved", "API key saved to config.json.")

    def _open_steam_store_search(self) -> None:
        dlg = SteamStoreSearchDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        name = dlg.selected_name()
        if name:
            self._append_game_to_list(name)

    def _append_game_to_list(self, name: str) -> None:
        name = name.strip()
        if not name:
            return
        existing = {
            self.list_games.item(i).text()
            for i in range(self.list_games.count())
        }
        if name in existing:
            QMessageBox.information(
                self, "Игры", f'«{name}» уже есть в списке проверки.'
            )
            return
        self.list_games.addItem(name)

    def _add_games(self) -> None:
        raw = self.game_input.text().strip()
        if not raw:
            return
        for part in [p.strip() for p in raw.split(",") if p.strip()]:
            resolved = sc.resolve_game_name(part, self._append_log)
            self._append_game_to_list(resolved)
        self.game_input.clear()

    def _sort_games_list(self) -> None:
        names = []
        for i in range(self.list_games.count()):
            names.append(self.list_games.item(i).text())
        if not names:
            return
        self.list_games.clear()
        for name in sc.sort_game_names(names):
            self.list_games.addItem(name)

    def _remove_selected_games(self) -> None:
        for item in self.list_games.selectedItems():
            self.list_games.takeItem(self.list_games.row(item))

    def _load_accounts_file(self) -> None:
        path = sc.ACCOUNTS_FILE
        if not os.path.isfile(path):
            QMessageBox.information(
                self,
                "Файл",
                f"Файл не найден: {path}",
            )
            return
        with open(path, "r", encoding="utf-8") as f:
            self.text_accounts.setPlainText(f.read())

    def _collect_games(self) -> List[str]:
        out = []
        for i in range(self.list_games.count()):
            out.append(self.list_games.item(i).text())
        return out

    def _collect_accounts(self) -> List[str]:
        lines = []
        for line in self.text_accounts.toPlainText().splitlines():
            s = line.strip()
            if s and not s.startswith("#"):
                lines.append(s)
        return lines

    def _start_check(self) -> None:
        if self._thread is not None:
            QMessageBox.warning(self, "Занято", "Проверка уже выполняется.")
            return
        api_key = self.api_edit.text().strip()
        if not api_key:
            QMessageBox.warning(self, "Нет ключа", "Введите и сохраните Steam Web API ключ.")
            return
        games = self._collect_games()
        accounts = self._collect_accounts()
        if not games:
            QMessageBox.warning(self, "Нет игр", "Добавьте хотя бы одну игру.")
            return
        if not accounts:
            QMessageBox.warning(self, "Нет аккаунтов", "Укажите хотя бы один аккаунт.")
            return

        self.btn_run.setEnabled(False)
        delay = float(self.spin_delay.value())
        self._thread = QThread()
        self._worker = CheckWorker(api_key, accounts, games, delay)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.log_msg.connect(self._append_log)
        self._worker.finished_ok.connect(self._worker_finished_ok)
        self._worker.failed.connect(self._worker_failed)
        self._thread.finished.connect(self._cleanup_thread)
        self._thread.start()

    def _worker_finished_ok(self, summary: list, games: list) -> None:
        self._on_check_done(summary, games)
        if self._thread:
            self._thread.quit()

    def _worker_failed(self, msg: str) -> None:
        self._on_check_fail(msg)
        if self._thread:
            self._thread.quit()

    def _on_check_done(self, summary: list, games: list) -> None:
        self._print_summary(summary, games)
        self._append_log(
            f"\nГотово. Результаты: {os.path.abspath(sc.OUTPUT_DIR)}",
            "title",
        )
        QMessageBox.information(self, "Готово", "Проверка завершена.")

    def _on_check_fail(self, msg: str) -> None:
        self._append_log(msg, "err")
        QMessageBox.critical(self, "Ошибка", msg)

    def _cleanup_thread(self) -> None:
        self.btn_run.setEnabled(True)
        if self._worker:
            self._worker.deleteLater()
            self._worker = None
        if self._thread:
            self._thread.deleteLater()
            self._thread = None

    def _print_summary(self, summary: list, games: list) -> None:
        self._append_log("\n" + "=" * 50, "title")
        self._append_log("ИТОГОВЫЙ ОТЧЁТ", "title")
        self._append_log("=" * 50, "title")
        for game in sc.sort_game_names(games):
            rows = [(a, sid, s, pt) for a, sid, g, s, pt in summary if g == game]
            found = [(a, sid, pt) for a, sid, s, pt in rows if s == "ЕСТЬ"]
            nope = [(a, sid) for a, sid, s, pt in rows if s == "НЕТ"]
            err = [(a, sid, s) for a, sid, s, pt in rows if s.startswith("ОШИБКА")]
            self._append_log(f"\nИгра: {game}", "title")
            self._append_log(f"  Найдено: {len(found)}", "ok")
            self._append_log(f"  Нет: {len(nope)}", "err")
            if err:
                self._append_log(f"  Ошибки: {len(err)}", "warn")

    def _open_results(self) -> None:
        sc.ensure_dir(sc.OUTPUT_DIR)
        QDesktopServices.openUrl(
            QUrl.fromLocalFile(os.path.abspath(sc.OUTPUT_DIR))
        )

    def _open_accounts(self) -> None:
        sc.create_accounts_template()
        QDesktopServices.openUrl(
            QUrl.fromLocalFile(os.path.abspath(sc.ACCOUNTS_FILE))
        )


def main() -> int:
    app = QApplication(sys.argv)
    apply_dark_theme(app)

    sc.ensure_dir(sc.OUTPUT_DIR)
    sc.create_accounts_template()
    w = MainWindow()
    w.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
