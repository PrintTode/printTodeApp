from flask import Flask, request, jsonify
import sqlite3
import base64
import os

app = Flask(__name__)

# Inisialisasi database print jobs
def init_print_jobs_db():
    with sqlite3.connect('print_jobs.db') as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS print_jobs (
                print_job_id TEXT PRIMARY KEY,
                computer_id TEXT NOT NULL,
                printer_id TEXT NOT NULL,
                file_content TEXT NOT NULL,
                status TEXT DEFAULT 'pending'
            )
        ''')
        conn.commit()

# Inisialisasi database printer
def init_printers_db():
    with sqlite3.connect('printers.db') as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS printers (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL
            )
        ''')
        conn.commit()

@app.route('/print_jobs', methods=['POST'])
def create_print_job():
    data = request.json
    print_job_id = data.get('print_job_id')
    computer_id = data.get('computer_id')
    printer_id = data.get('printer_id')
    file_content = data.get('file_content')
    
    if not print_job_id or not computer_id or not printer_id or not file_content:
        return jsonify({'message': 'Invalid data'}), 400
    
    with sqlite3.connect('print_jobs.db') as conn:
        c = conn.cursor()
        c.execute('''
            INSERT OR REPLACE INTO print_jobs (print_job_id, computer_id, printer_id, file_content) 
            VALUES (?, ?, ?, ?)
        ''', (print_job_id, computer_id, printer_id, file_content))
        conn.commit()
    
    return jsonify({'message': 'Print job created successfully'}), 200

@app.route('/print_jobs/<print_job_id>', methods=['GET'])
def get_print_job(print_job_id):
    with sqlite3.connect('print_jobs.db') as conn:
        c = conn.cursor()
        c.execute('SELECT computer_id, printer_id, file_content, status FROM print_jobs WHERE print_job_id = ?', (print_job_id,))
        job = c.fetchone()
    
    if not job:
        return jsonify({'message': 'Print job not found'}), 404
    
    return jsonify({
        'computer_id': job[0],
        'printer_id': job[1],
        'file_content': job[2],
        'status': job[3]
    }), 200

@app.route('/print_jobs/<print_job_id>', methods=['POST'])
def update_print_job_status(print_job_id):
    data = request.json
    status = data.get('status')
    
    if status not in ['pending', 'completed', 'failed']:
        return jsonify({'message': 'Invalid status'}), 400
    
    with sqlite3.connect('print_jobs.db') as conn:
        c = conn.cursor()
        c.execute('UPDATE print_jobs SET status = ? WHERE print_job_id = ?', (status, print_job_id))
        conn.commit()
    
    return jsonify({'message': 'Print job status updated successfully'}), 200

@app.route('/printers', methods=['POST'])
def add_or_update_printer():
    data = request.json
    printer_id = data.get('id')
    printer_name = data.get('name')
    
    if not printer_id or not printer_name:
        return jsonify({'message': 'Invalid data'}), 400
    
    with sqlite3.connect('printers.db') as conn:
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO printers (id, name) VALUES (?, ?)', (printer_id, printer_name))
        conn.commit()
    
    return jsonify({'message': 'Printer added or updated successfully'}), 200

if __name__ == '__main__':
    init_print_jobs_db()
    init_printers_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
