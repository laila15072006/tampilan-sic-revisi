from . import db
from datetime import datetime

class Kelas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    siswas = db.relationship('Siswa', backref='kelas', lazy=True, cascade='all, delete-orphan')

class Siswa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    absensi = db.Column(db.String(100), nullable=False)
    nama = db.Column(db.String(100), nullable=False)
    id_kelas = db.Column(db.Integer, db.ForeignKey('kelas.id'), nullable=False)
    data_scans = db.relationship('DataScan', backref='siswa', lazy=True, cascade='all, delete-orphan')

class DataScan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_siswa = db.Column(db.Integer, db.ForeignKey('siswa.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    pelanggaran = db.Column(db.Boolean, nullable=True)