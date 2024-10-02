document.addEventListener('DOMContentLoaded', function() {
    // Seleccionar todos los campos 'servicio' del formulario inline
    document.querySelectorAll('select[name$="-servicio"]').forEach(function(servicioSelect) {
        servicioSelect.addEventListener('change', function() {
            const selectedOption = servicioSelect.options[servicioSelect.selectedIndex];
            const categoriaNombre = selectedOption.getAttribute('data-categoria');  // Leer la categoría desde el servicio

            // Obtener el campo de hora correspondiente en el mismo formulario inline
            const horaFieldName = servicioSelect.name.replace('servicio', 'hora');
            const horaSelect = document.querySelector(`select[name="${horaFieldName}"]`);

            // Limpiar las opciones de hora antes de llenarlas
            horaSelect.innerHTML = '';

            // Asignar horarios dinámicamente según la categoría del servicio seleccionado
            if (categoriaNombre === 'Cabañas') {
                horaSelect.innerHTML += '<option value="16:00">16:00</option>';
            } else if (categoriaNombre === 'Tinas') {
                horaSelect.innerHTML += '<option value="14:00">14:00</option>';
                horaSelect.innerHTML += '<option value="14:30">14:30</option>';
                horaSelect.innerHTML += '<option value="17:00">17:00</option>';
                horaSelect.innerHTML += '<option value="19:00">19:00</option>';
                horaSelect.innerHTML += '<option value="19:30">19:30</option>';
                horaSelect.innerHTML += '<option value="21:30">21:30</option>';
                horaSelect.innerHTML += '<option value="22:00">22:00</option>';
            } else if (categoriaNombre === 'Masajes') {
                horaSelect.innerHTML += '<option value="13:00">13:00</option>';
                horaSelect.innerHTML += '<option value="14:15">14:15</option>';
                horaSelect.innerHTML += '<option value="15:30">15:30</option>';
                horaSelect.innerHTML += '<option value="16:45">16:45</option>';
                horaSelect.innerHTML += '<option value="18:00">18:00</option>';
                horaSelect.innerHTML += '<option value="19:15">19:15</option>';
                horaSelect.innerHTML += '<option value="20:30">20:30</option>';
            } else {
                horaSelect.innerHTML += '<option value="">Seleccione un horario</option>';
            }
        });
    });
});
