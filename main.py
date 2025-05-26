import sys
import sqlite3
import csv
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QHeaderView,
    QDialog, QFormLayout, QDialogButtonBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class DialogEdit(QDialog):
    def __init__(self, id_data, judul, penulis, tahun):
        super().__init__()
        self.setWindowTitle("Edit Data Buku")
        self.setFixedSize(300, 180)

        self.id_data = id_data

        layout = QFormLayout()
        self.in_judul = QLineEdit(judul)
        self.in_penulis = QLineEdit(penulis)
        self.in_tahun = QLineEdit(tahun)

        layout.addRow("Judul:", self.in_judul)
        layout.addRow("Penulis:", self.in_penulis)
        layout.addRow("Tahun:", self.in_tahun)

        tombol = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        tombol.accepted.connect(self.accept)
        tombol.rejected.connect(self.reject)
        layout.addWidget(tombol)

        self.setLayout(layout)

    def get_data(self):
        return self.in_judul.text(), self.in_penulis.text(), self.in_tahun.text()

class AplBuku(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aplikasi Data Buku")
        self.resize(750, 500)
        self.setStyleSheet("""
            QWidget { font-size: 12pt; }
            QLineEdit, QPushButton { padding: 5px; }
        """)
        self.ui()
        self.db()
        self.load_data()

    def ui(self):
        layout = QVBoxLayout()

        form = QHBoxLayout()
        self.nm = QLineEdit()
        self.pnls = QLineEdit()
        self.thn = QLineEdit()
        self.nm.setPlaceholderText("Judul Buku")
        self.pnls.setPlaceholderText("Penulis")
        self.thn.setPlaceholderText("Tahun")

        form.addWidget(self.nm)
        form.addWidget(self.pnls)
        form.addWidget(self.thn)

        self.btn_simpan = QPushButton("Simpan")
        self.btn_simpan.setStyleSheet("background-color: #4CAF50; color: white;")
        self.btn_simpan.clicked.connect(self.simpan_data)

        self.cari = QLineEdit()
        self.cari.setPlaceholderText("Cari judul buku...")
        self.cari.textChanged.connect(self.cari_data)

        self.tbl = QTableWidget()
        self.tbl.setColumnCount(4)
        self.tbl.setHorizontalHeaderLabels(["ID", "Judul", "Penulis", "Tahun"])
        self.tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl.cellDoubleClicked.connect(self.edit_data)

        baris_btn = QHBoxLayout()
        self.btn_hapus = QPushButton("Hapus")
        self.btn_hapus.setStyleSheet("background-color: #f44336; color: white;")
        self.btn_hapus.clicked.connect(self.hapus_data)

        self.btn_export = QPushButton("Export CSV")
        self.btn_export.setStyleSheet("background-color: #2196F3; color: white;")
        self.btn_export.clicked.connect(self.export_csv)

        baris_btn.addWidget(self.btn_hapus)
        baris_btn.addWidget(self.btn_export)

        self.footer = QLabel("Muh. Ressa Arsy Ma'rif | NIM: F1D022137")
        self.footer.setAlignment(Qt.AlignCenter)
        self.footer.setStyleSheet("color: gray; font-size: 9pt; padding-top: 10px;")

        layout.addLayout(form)
        layout.addWidget(self.btn_simpan)
        layout.addWidget(self.cari)
        layout.addWidget(self.tbl)
        layout.addLayout(baris_btn)
        layout.addWidget(self.footer)

        self.setLayout(layout)

    def db(self):
        self.koneksi = sqlite3.connect("data.db")
        self.kur = self.koneksi.cursor()
        self.kur.execute("""
            CREATE TABLE IF NOT EXISTS buku (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                judul TEXT,
                penulis TEXT,
                tahun INTEGER
            )
        """)
        self.koneksi.commit()

    def load_data(self):
        self.tbl.setRowCount(0)
        self.kur.execute("SELECT * FROM buku")
        for baris in self.kur.fetchall():
            idx = self.tbl.rowCount()
            self.tbl.insertRow(idx)
            for kol, isi in enumerate(baris):
                self.tbl.setItem(idx, kol, QTableWidgetItem(str(isi)))

    def simpan_data(self):
        judul = self.nm.text()
        penulis = self.pnls.text()
        tahun = self.thn.text()

        if not (judul and penulis and tahun.isdigit()):
            QMessageBox.warning(self, "Peringatan", "Isi data dengan lengkap dan benar!")
            return

        self.kur.execute("INSERT INTO buku (judul, penulis, tahun) VALUES (?, ?, ?)",
                         (judul, penulis, int(tahun)))
        self.koneksi.commit()
        self.kosongkan_input()
        self.load_data()

    def kosongkan_input(self):
        self.nm.clear()
        self.pnls.clear()
        self.thn.clear()

    def cari_data(self, teks):
        self.tbl.setRowCount(0)
        self.kur.execute("SELECT * FROM buku WHERE judul LIKE ?", ('%' + teks + '%',))
        for baris in self.kur.fetchall():
            idx = self.tbl.rowCount()
            self.tbl.insertRow(idx)
            for kol, isi in enumerate(baris):
                self.tbl.setItem(idx, kol, QTableWidgetItem(str(isi)))

    def edit_data(self, baris, kolom):
        id_data = int(self.tbl.item(baris, 0).text())
        judul = self.tbl.item(baris, 1).text()
        penulis = self.tbl.item(baris, 2).text()
        tahun = self.tbl.item(baris, 3).text()

        dlg = DialogEdit(id_data, judul, penulis, tahun)
        if dlg.exec_():
            judul_baru, penulis_baru, tahun_baru = dlg.get_data()
            if not (judul_baru and penulis_baru and tahun_baru.isdigit()):
                QMessageBox.warning(self, "Peringatan", "Data tidak valid!")
                return

            self.kur.execute(
                "UPDATE buku SET judul=?, penulis=?, tahun=? WHERE id=?",
                (judul_baru, penulis_baru, int(tahun_baru), id_data)
            )
            self.koneksi.commit()
            self.load_data()

    def hapus_data(self):
        baris = self.tbl.currentRow()
        if baris < 0:
            QMessageBox.warning(self, "Peringatan", "Pilih baris yang ingin dihapus!")
            return

        id_data = int(self.tbl.item(baris, 0).text())
        self.kur.execute("DELETE FROM buku WHERE id=?", (id_data,))
        self.koneksi.commit()
        self.load_data()

    def export_csv(self):
        self.kur.execute("SELECT * FROM buku")
        data = self.kur.fetchall()
        with open("data_buku.csv", "w", newline="", encoding="utf-8") as f:
            tulis = csv.writer(f)
            tulis.writerow(["ID", "Judul", "Penulis", "Tahun"])
            tulis.writerows(data)
        QMessageBox.information(self, "Berhasil", "Data berhasil disimpan ke data_buku.csv")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = AplBuku()
    win.show()
    sys.exit(app.exec_())
