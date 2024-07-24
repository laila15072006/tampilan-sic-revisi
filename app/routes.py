from . import create_app, db
from .models import Kelas, Siswa, DataScan
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import func, and_, case
import pendulum
import joblib

main = Blueprint('main', __name__)
csrf = CSRFProtect()
kmeans = joblib.load('app/kmeans_model.pkl')

@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nama = request.form.get('nama')
        if not nama:
            flash('Nama tidak boleh kosong', 'danger')
        else:
            new_class = Kelas(nama=nama)
            db.session.add(new_class)
            db.session.commit()
            return redirect(url_for('main.index'))

    # Get the current date in Jakarta timezone
    now_jakarta = pendulum.now('Asia/Jakarta')
    start_of_day_jakarta = now_jakarta.start_of('day').in_timezone('UTC')
    end_of_day_jakarta = now_jakarta.end_of('day').in_timezone('UTC')

    # Query to count the number of students in each class and get the class name
    classes = db.session.query(
        Kelas.id,
        Kelas.nama, 
        func.count(Siswa.id).label('total_siswa'),
        func.sum(case((DataScan.pelanggaran == True, 1), else_=0)).label('total_pelanggaran')
    ).outerjoin(Siswa, Kelas.id == Siswa.id_kelas
    ).outerjoin(DataScan, and_(
        DataScan.id_siswa == Siswa.id,
        DataScan.created_at >= start_of_day_jakarta,
        DataScan.created_at <= end_of_day_jakarta
    )).group_by(Kelas.id).all()

    class_list = [{'id': cls.id, 'nama': cls.nama, 'total_siswa': cls.total_siswa, 'total_pelanggaran': cls.total_pelanggaran} for cls in classes]

    return render_template('index.html', classes=class_list)


@main.route('/clustering', methods=['GET', 'POST'])
def clustering():
    if request.method == 'POST':
        data = request.get_json()
        siswa = data.get('siswa')
        pelanggar = data.get('pelanggar')
        # print(siswa, pelanggar)
        result = kmeans.predict([[siswa, pelanggar]])
        print(result)
        return jsonify({'result': int(result[0])})

    now_jakarta = pendulum.now('Asia/Jakarta')
    start_of_day_jakarta = now_jakarta.start_of('day').in_timezone('UTC')
    end_of_day_jakarta = now_jakarta.end_of('day').in_timezone('UTC')

    # Query to count the number of students in each class and get the class name
    classes = db.session.query(
        Kelas.id,
        Kelas.nama, 
        func.count(Siswa.id).label('total_siswa'),
        func.sum(case((DataScan.pelanggaran == True, 1), else_=0)).label('total_pelanggaran')
    ).outerjoin(Siswa, Kelas.id == Siswa.id_kelas
    ).outerjoin(DataScan, and_(
        DataScan.id_siswa == Siswa.id,
        DataScan.created_at >= start_of_day_jakarta,
        DataScan.created_at <= end_of_day_jakarta
    )).group_by(Kelas.id).all()
    class_list = [{'id': cls.id, 'nama': cls.nama, 'total_siswa': cls.total_siswa, 'total_pelanggaran': cls.total_pelanggaran} for cls in classes]
    
    return render_template('clustering.html', classes=class_list)

@main.route('/edit_kelas/<int:kelas_id>', methods=['POST'])
def edit_kelas(kelas_id):
    kelas = Kelas.query.get_or_404(kelas_id)
    nama = request.form.get('nama')
    if not nama:
        flash('Nama tidak boleh kosong', 'danger')
    else:
        kelas.nama = nama
        db.session.commit()
        flash('Kelas updated successfully', 'success')
    return redirect(url_for('main.index'))

@main.route('/delete_kelas/<int:kelas_id>', methods=['POST'])
def delete_kelas(kelas_id):
    kelas = Kelas.query.get_or_404(kelas_id)
    db.session.delete(kelas)
    db.session.commit()
    flash('Kelas deleted successfully', 'success')
    return redirect(url_for('main.index'))

@main.route('/get_kelas/<int:kelas_id>', methods=['GET'])
def get_kelas(kelas_id):
    kelas = Kelas.query.get_or_404(kelas_id)
    return jsonify({'id': kelas.id, 'nama': kelas.nama})


@main.route('/siswa_kelas/<int:kelas_id>', methods=['GET'])
def get_siswa_in_kelas(kelas_id):
    # Get the current date in Jakarta timezone
    now_jakarta = pendulum.now('Asia/Jakarta')
    start_of_day_jakarta = now_jakarta.start_of('day')
    end_of_day_jakarta = now_jakarta.end_of('day')

    list_siswa = Siswa.query.filter_by(id_kelas=kelas_id).all()
    siswa_list = []

    for siswa in list_siswa:
        # Check for pelanggaran record for today
        pelanggaran_hari_ini = DataScan.query.filter_by(id_siswa=siswa.id).filter(
            DataScan.created_at >= start_of_day_jakarta,
            DataScan.created_at <= end_of_day_jakarta
        ).first()

        if pelanggaran_hari_ini:
            pelanggaran_status = 1 if pelanggaran_hari_ini.pelanggaran else 0
        else:
            pelanggaran_status = -1

        siswa_list.append({
            'id': siswa.id,
            'absensi': siswa.absensi,
            'nama': siswa.nama,
            'pelanggaran': pelanggaran_status
        })

    return render_template('siswa.html', siswas=siswa_list, kelas_id=kelas_id)

@main.route('/add_siswa', methods=['POST'])
def add_siswa():
    absensi = request.form.get('absensi')
    nama = request.form.get('nama')
    id_kelas = request.form.get('kelas_id')
    if not absensi or not nama:
        flash('Absensi dan Nama tidak boleh kosong', 'danger')
    else:
        new_siswa = Siswa(absensi=absensi, nama=nama, id_kelas=id_kelas)
        db.session.add(new_siswa)
        db.session.commit()
        flash('Siswa added successfully', 'success')
    return redirect(url_for('main.get_siswa_in_kelas', kelas_id=id_kelas))

@main.route('/edit_siswa/<int:siswa_id>', methods=['POST'])
def edit_siswa(siswa_id):
    siswa = Siswa.query.get_or_404(siswa_id)
    absensi = request.form.get('absensi')
    nama = request.form.get('nama')
    if not absensi or not nama:
        flash('Absensi dan Nama tidak boleh kosong', 'danger')
    else:
        siswa.absensi = absensi
        siswa.nama = nama
        db.session.commit()
        flash('Siswa updated successfully', 'success')
    return redirect(url_for('main.get_siswa_in_kelas', kelas_id=siswa.id_kelas))

@main.route('/delete_siswa/<int:siswa_id>', methods=['POST'])
def delete_siswa(siswa_id):
    siswa = Siswa.query.get_or_404(siswa_id)
    id_kelas = siswa.id_kelas
    db.session.delete(siswa)
    db.session.commit()
    flash('Siswa deleted successfully', 'success')
    return redirect(url_for('main.get_siswa_in_kelas', kelas_id=id_kelas))

@main.route('/add_pelanggaran',methods=['POST'])
def add_pelanggaran():
    data = request.get_json()
    id_siswa = data.get('siswa_id')
    pelanggaran = bool(int(data.get('status')))
    now_jakarta = pendulum.now('Asia/Jakarta')
    now_utc = now_jakarta.in_timezone('UTC')

    # Check if there is a record for today in Jakarta timezone
    start_of_day_utc = now_jakarta.start_of('day').in_timezone('UTC')
    end_of_day_utc = now_jakarta.end_of('day').in_timezone('UTC')

    pelanggaran_hari_ini = DataScan.query.filter_by(id_siswa=id_siswa).filter(
        DataScan.created_at >= start_of_day_utc,
        DataScan.created_at <= end_of_day_utc
    ).first()
    if pelanggaran_hari_ini:
        print("Pelanggaran already exists for today")
        # flash('Pelanggaran already exists for today', 'danger')
        return {'status': 'failed'}
    else:
        new_data_scan = DataScan(id_siswa=id_siswa, pelanggaran=pelanggaran)
        db.session.add(new_data_scan)
        db.session.commit()
        return {'status': 'success'}
            

    