(function () {
    'use strict';

    const $ = (sel, ctx) => (ctx || document).querySelector(sel);
    let ultimoConteoRegistros = 0;

    function formatearHoras(h) {
        const m = Math.round(h * 60);
        return Math.floor(m / 60) + 'h ' + (m % 60) + 'm';
    }

    function enlaceEmpleado(pk, name) {
        return '<a href="/employee/' + pk + '/" class="text-decoration-none text-reset">' + name + '</a>';
    }

    function actualizarReloj() {
        const c = $('#clock');
        if (c) c.textContent = new Date().toLocaleString('es-MX');
    }
    setInterval(actualizarReloj, 1000);
    actualizarReloj();

    function cargarRegistrosPorFecha(dateStr) {
        const tbody = $('#historyBody');
        tbody.innerHTML = '<tr><td colspan="4" class="text-secondary text-center py-3">Cargando...</td></tr>';
        fetch('/api/scans-by-date/?date=' + dateStr)
            .then(function (r) { return r.json(); })
            .then(function (d) {
                var info = $('#historyInfo');
                if (info) info.textContent = d.total + ' registro(s) encontrados el ' + dateStr;
                if (d.error) {
                    tbody.innerHTML = '<tr><td colspan="4" class="text-danger text-center py-3">' + d.error + '</td></tr>';
                    return;
                }
                if (!d.scans.length) {
                    tbody.innerHTML = '<tr><td colspan="4" class="text-secondary text-center py-3">Sin registros en esta fecha</td></tr>';
                    return;
                }
                tbody.innerHTML = d.scans.map(function (s) {
                    return '<tr>' +
                        '<td><span class="badge bg-secondary font-monospace">' + s.id + '</span></td>' +
                        '<td>' + enlaceEmpleado(s.employee_pk, s.name) + '</td>' +
                        '<td><strong>' + s.time + '</strong></td>' +
                        '<td class="small text-secondary">' + s.device + '</td>' +
                        '</tr>';
                }).join('');
            })
            .catch(function () {
                tbody.innerHTML = '<tr><td colspan="4" class="text-danger text-center py-3">Error al cargar datos</td></tr>';
            });
    }

    var historyBtn = $('#loadHistoryBtn');
    var historyDate = $('#historyDate');
    if (historyBtn && historyDate) {
        fetch('/api/available-dates/')
            .then(function (r) { return r.json(); })
            .then(function (d) {
                historyDate.innerHTML = '';
                d.dates.forEach(function (ds) {
                    var opt = document.createElement('option');
                    opt.value = ds;
                    var parts = ds.split('-');
                    var dObj = new Date(parts[0], parts[1] - 1, parts[2]);
                    opt.textContent = dObj.toLocaleDateString('es-MX', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
                    historyDate.appendChild(opt);
                });
                if (d.dates.length) {
                    historyDate.value = d.dates[0];
                    cargarRegistrosPorFecha(d.dates[0]);
                }
            });
        historyBtn.addEventListener('click', function () {
            if (historyDate.value) cargarRegistrosPorFecha(historyDate.value);
        });
        historyDate.addEventListener('change', function () {
            if (this.value) cargarRegistrosPorFecha(this.value);
        });
    }

    fetch('/api/employees/')
        .then(function (r) { return r.json(); })
        .then(function (d) {
            var el = $('#employeeList');
            var ec = $('#empCount');
            if (el && d.employees) {
                el.innerHTML = d.employees.map(function (e) {
                    return '<a href="/employee/' + e.id + '/" class="badge bg-secondary text-decoration-none">' + e.display_id + ' — ' + e.name + '</a>';
                }).join('');
            }
            if (ec) ec.textContent = d.employees ? d.employees.length : 0;
        });

    const dropZone = $('#dropZone');
    const fileInput = $('#fileInput');
    const submitBtn = $('#submitBtn');
    const uploadForm = $('#uploadForm');

    if (!dropZone) return;

    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('dragover'); });
    dropZone.addEventListener('dragleave', () => { dropZone.classList.remove('dragover'); });
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) { fileInput.files = e.dataTransfer.files; alSeleccionarArchivo(e.dataTransfer.files[0]); }
    });
    fileInput.addEventListener('change', () => { if (fileInput.files.length) alSeleccionarArchivo(fileInput.files[0]); });

    function alSeleccionarArchivo(f) {
        $('#dropContent').classList.add('d-none');
        $('#fileInfo').classList.remove('d-none');
        $('#fileName').textContent = f.name;
        const sz = ['Bytes', 'KB', 'MB'];
        const i = Math.floor(Math.log(f.size) / Math.log(1024));
        $('#fileSize').textContent = (f.size / Math.pow(1024, i)).toFixed(1) + ' ' + sz[i];
        dropZone.classList.add('has-file');
        submitBtn.disabled = false;
    }

    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!fileInput.files.length) return;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Procesando...';
        const fd = new FormData(uploadForm);
        fd.set('file', fileInput.files[0]);
        try {
            const r = await fetch('/upload/', { method: 'POST', body: fd });
            const d = await r.json();
            if (!r.ok) { alert('Error: ' + (d.error || 'Error')); reiniciarSubida(); return; }
            mostrarResultados(d);
        } catch (err) { alert('Error: ' + err.message); reiniciarSubida(); }
    });

    window.reiniciarSubida = function () {
        const sec = $('#resultSection');
        if (sec) sec.classList.add('d-none');
        $('#dropContent').classList.remove('d-none');
        $('#fileInfo').classList.add('d-none');
        dropZone.classList.remove('has-file');
        fileInput.value = '';
        submitBtn.disabled = true;
        submitBtn.textContent = 'Procesar archivo';
        window.scrollTo(0, 0);
    };

    function mostrarResultados(data) {
        const { results, totals, unmatched, total_employees, total_records } = data;
        const sec = $('#resultSection');
        sec.classList.remove('d-none');
        $('#resultTitle').textContent = total_employees + ' empleados · ' + total_records + ' registros';
        const totH = totals.reduce((s, t) => s + t.total_hours, 0);
        $('#summaryBar').innerHTML = `
            <div class="col-md-3 col-6"><div class="card border-primary text-center py-2"><div class="text-primary fw-bold fs-4">${total_employees}</div><small class="text-secondary">Empleados</small></div></div>
            <div class="col-md-3 col-6"><div class="card border-success text-center py-2"><div class="text-success fw-bold fs-4">${total_records}</div><small class="text-secondary">Registros</small></div></div>
            <div class="col-md-3 col-6"><div class="card border-info text-center py-2"><div class="text-info fw-bold fs-4">${formatearHoras(totH)}</div><small class="text-secondary">Total horas</small></div></div>
            <div class="col-md-3 col-6"><div class="card border-warning text-center py-2"><div class="text-warning fw-bold fs-4">${unmatched.length}</div><small class="text-secondary">Sin registro</small></div></div>
        `;
        $('#detailBody').innerHTML = results.map(r => `
            <tr><td><span class="badge bg-secondary font-monospace">${r.id}</span></td><td>${enlaceEmpleado(r.pk, r.name)}</td><td>${r.date}</td><td>${r.first_scan}</td><td>${r.last_scan}</td><td><span class="badge bg-info text-dark">${formatearHoras(r.hours)}</span></td></tr>
        `).join('');
        $('#summaryBody').innerHTML = totals.map(t => `
            <tr><td><span class="badge bg-secondary font-monospace">${t.id}</span></td><td>${enlaceEmpleado(t.pk, t.name)}</td><td>${t.days} día(s)</td><td><span class="badge bg-success">${formatearHoras(t.total_hours)}</span></td></tr>
        `).join('');
        const um = $('#unmatchedSection');
        if (unmatched.length) {
            um.classList.remove('d-none');
            $('#unmatchedList').innerHTML = unmatched.map(u => `<span class="badge bg-secondary">${u.id} — ${u.name}</span>`).join(' ');
        } else { um.classList.add('d-none'); }
        sec.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function renderizarRegistrosRecientes(scans) {
        const body = $('#recentBody');
        if (!scans.length) {
            body.innerHTML = '<tr><td colspan="4" class="text-secondary text-center py-3">Sin registros aún</td></tr>';
            return;
        }
        body.innerHTML = scans.map((s, i) => `
            <tr class="${i === 0 && ultimoConteoRegistros > 0 && scans.length > ultimoConteoRegistros ? 'new-scan' : ''}">
                <td><span class="badge bg-secondary font-monospace">${s.id}</span></td>
                <td>${enlaceEmpleado(s.employee_pk, s.name)}</td>
                <td><strong>${s.time}</strong></td>
                <td class="text-secondary small">${s.date}</td>
            </tr>
        `).join('');
    }

    function mostrarBadgeNuevo() {
        const badge = $('#newScanBadge');
        if (badge) {
            badge.classList.remove('d-none');
            setTimeout(() => badge.classList.add('d-none'), 3000);
        }
    }

    function consultarRegistrosRecientes() {
        fetch('/api/recent-scans/')
            .then(r => r.json())
            .then(d => {
                const count = d.total || 0;
                if (count > ultimoConteoRegistros && ultimoConteoRegistros > 0) {
                    mostrarBadgeNuevo();
                }
                ultimoConteoRegistros = count;
                renderizarRegistrosRecientes(d.scans || []);
                const lu = $('#lastUpdate');
                if (lu) lu.textContent = d.scans.length ? d.scans[0].time + ' · ' + new Date().toLocaleTimeString('es-MX') : 'Esperando...';
            })
            .catch(() => {});
    }

    function consultarEstadisticas() {
        fetch('/api/sync-status/')
            .then(r => r.json())
            .then(d => {
                const dot = $('#deviceStatusDot');
                if (dot) {
                    dot.style.color = d.last_scan ? '#198754' : '#ffc107';
                    dot.textContent = '●';
                }
                if (d.last_sync) {
                    const lt = $('#lastSyncTime');
                    if (lt) lt.textContent = new Date(d.last_sync).toLocaleString('es-MX');
                }
                if (d.last_scan) {
                    const ls = $('#lastScanTime');
                    if (ls) ls.textContent = new Date(d.last_scan).toLocaleString('es-MX');
                }
                const ts = $('#totalScans');
                if (ts) ts.textContent = d.total_scans;
                const st = $('#scansToday');
                if (st) st.textContent = d.scans_today;
            })
            .catch(() => {});
    }

    window.sincronizarAhora = function () {
        const lt = $('#lastSyncTime');
        const btn = document.querySelector('.btn.btn-outline-info.btn-sm');
        if (lt) lt.textContent = 'Sincronizando...';
        if (btn) btn.disabled = true;
        fetch('/api/sync-device/')
            .then(r => r.json())
            .then(d => {
                const msg = d.asistencia
                    ? (d.asistencia.new + ' nuevos, ' + d.asistencia.skipped + ' existentes')
                    : 'Error';
                if (lt) lt.textContent = '✓ ' + msg;
                setTimeout(() => { consultarRegistrosRecientes(); consultarEstadisticas(); }, 1000);
            })
            .catch(() => { if (lt) lt.textContent = 'Error'; })
            .finally(() => { if (btn) btn.disabled = false; });
    };

    consultarRegistrosRecientes();
    consultarEstadisticas();
    setInterval(consultarRegistrosRecientes, 5000);
    setInterval(consultarEstadisticas, 10000);

})();
