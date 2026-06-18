(function () {
    'use strict';

    const $ = (sel, ctx) => (ctx || document).querySelector(sel);
    let ultimoConteoRegistros = 0;
    let pollingActivo = true;

    function obtenerJsonConTimeout(url, timeoutMs) {
        timeoutMs = timeoutMs || 15000;
        const controlador = new AbortController();
        const timer = setTimeout(function () { controlador.abort(); }, timeoutMs);
        return fetch(url, { signal: controlador.signal })
            .then(function (r) { clearTimeout(timer); return r.json(); })
            .catch(function (err) {
                clearTimeout(timer);
                throw err;
            });
    }

    function formatearHoras(h) {
        const m = Math.round(h * 60);
        return Math.floor(m / 60) + 'h ' + (m % 60) + 'm';
    }

    function enlaceEmpleado(pk, nombre) {
        return '<a href="/asistencia/empleado/' + pk + '/" class="text-decoration-none text-reset">' + nombre + '</a>';
    }

    function actualizarReloj() {
        const c = $('#reloj');
        if (c) c.textContent = new Date().toLocaleString('es-MX');
    }
    setInterval(actualizarReloj, 1000);
    actualizarReloj();

    /* ============= Empleados sidebar ============= */
    obtenerJsonConTimeout('/asistencia/api/empleados/')
        .then(function (d) {
            var el = $('#listaEmpleados');
            var ec = $('#contadorEmpleados');
            if (el && d.empleados) {
                el.innerHTML = d.empleados.map(function (e) {
                    return '<a href="/asistencia/empleado/' + e.id + '/" class="badge bg-secondary text-decoration-none">' + e.id_visual + ' — ' + e.nombre + '</a>';
                }).join('');
            }
            if (ec) ec.textContent = d.empleados ? d.empleados.length : 0;
        })
        .catch(function () {
            var el = $('#listaEmpleados');
            if (el) el.innerHTML = '<span class="text-danger small">Error al cargar empleados</span>';
        });

    /* ============= Hoy - Registros recientes ============= */
    function renderizarRegistrosRecientes(registros) {
        const body = $('#cuerpoReciente');
        if (!body) return;
        if (!registros.length) {
            body.innerHTML = '<tr><td colspan="4" class="text-secondary text-center py-3">Sin registros a\u00FAn</td></tr>';
            return;
        }
        body.innerHTML = registros.map(function (s, i) {
            var cls = (i === 0 && ultimoConteoRegistros > 0 && registros.length > ultimoConteoRegistros) ? 'new-scan' : '';
            return '<tr class="' + cls + '">' +
                '<td><span class="badge bg-secondary font-monospace">' + s.id + '</span></td>' +
                '<td>' + enlaceEmpleado(s.empleado_pk, s.nombre) + '</td>' +
                '<td><strong>' + s.hora + '</strong></td>' +
                '<td class="text-secondary small">' + s.fecha + '</td>' +
                '</tr>';
        }).join('');
    }

    function mostrarBadgeNuevo() {
        const badge = $('#badgeNuevo');
        if (badge) {
            badge.classList.remove('d-none');
            setTimeout(function () { badge.classList.add('d-none'); }, 3000);
        }
    }

    function consultarRegistrosRecientes() {
        if (!pollingActivo) return;
        obtenerJsonConTimeout('/asistencia/api/registros-recientes/')
            .then(function (d) {
                var count = d.total || 0;
                if (count > ultimoConteoRegistros && ultimoConteoRegistros > 0) {
                    mostrarBadgeNuevo();
                }
                ultimoConteoRegistros = count;
                renderizarRegistrosRecientes(d.registros || []);
                var lu = $('#ultimaActualizacion');
                if (lu) lu.textContent = d.registros.length ? d.registros[0].hora + ' \u00B7 ' + new Date().toLocaleTimeString('es-MX') : 'Esperando...';
            })
            .catch(function () {})
            .finally(function () {
                if (pollingActivo) setTimeout(consultarRegistrosRecientes, 5000);
            });
    }

    function consultarEstadisticas() {
        if (!pollingActivo) return;
        obtenerJsonConTimeout('/asistencia/api/estado-sincronizacion/')
            .then(function (d) {
                var dot = $('#puntoEstado');
                if (dot) {
                    dot.style.color = d.ultimo_registro ? '#198754' : '#ffc107';
                    dot.textContent = '\u25CF';
                }
                if (d.ultima_sincronizacion) {
                    var lt = $('#ultimaSincronizacion');
                    if (lt) lt.textContent = new Date(d.ultima_sincronizacion).toLocaleString('es-MX');
                }
                if (d.ultimo_registro) {
                    var ls = $('#ultimoRegistro');
                    if (ls) ls.textContent = new Date(d.ultimo_registro).toLocaleString('es-MX');
                }
                var ts = $('#totalRegistros');
                if (ts) ts.textContent = d.total_registros;
                var st = $('#registrosHoy');
                if (st) st.textContent = d.registros_hoy;
            })
            .catch(function () {})
            .finally(function () {
                if (pollingActivo) setTimeout(consultarEstadisticas, 10000);
            });
    }

    window.sincronizarAhora = function () {
        var lt = $('#ultimaSincronizacion');
        var btn = document.querySelector('.btn-outline-info');
        if (lt) lt.textContent = 'Sincronizando...';
        if (btn) btn.disabled = true;
        pollingActivo = false;
        obtenerJsonConTimeout('/asistencia/api/sincronizar-dispositivo/', 60000)
            .then(function (d) {
                var msg = d.asistencia
                    ? (d.asistencia.nuevos + ' nuevos, ' + d.asistencia.omitidos + ' existentes')
                    : 'Error';
                if (lt) lt.textContent = '\u2713 ' + msg;
            })
            .catch(function () { if (lt) lt.textContent = '\u2717 Error'; })
            .finally(function () {
                if (btn) btn.disabled = false;
                pollingActivo = true;
                consultarRegistrosRecientes();
                consultarEstadisticas();
            });
    };

    consultarRegistrosRecientes();
    consultarEstadisticas();

})();
