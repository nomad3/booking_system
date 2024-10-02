document.addEventListener('DOMContentLoaded', function() {
    // Escuchar cambios en todos los campos 'servicio' del formulario inline
    document.querySelectorAll('select[name$="-servicio"]').forEach(function(servicioSelect) {
        servicioSelect.addEventListener('change', function() {
            const servicioId = servicioSelect.value;  // Leer el ID del servicio seleccionado
            console.log("Servicio cambiado, ID seleccionado:", servicioId);

            // Buscar el campo de hora en el mismo formulario inline
            const inlineForm = servicioSelect.closest('.inline-related');  // Encuentra el contenedor del formulario inline
            const horaSelect = inlineForm.querySelector('select[name$="-hora"]');  // Encuentra el campo de hora correspondiente

            if (!horaSelect) {
                console.error("No se pudo encontrar el campo de hora correspondiente");
                return;  // Salir si no se encuentra el campo de hora
            }

            console.log("Campo de hora encontrado:", horaSelect);

            // Limpiar las opciones de hora antes de llenarlas
            horaSelect.innerHTML = '';

            // Asignar horarios dinámicamente según el ID del servicio seleccionado
            if (servicioId == '1') {  // ID para Cabañas
                horaSelect.innerHTML += '<option value="16:00">16:00</option>';
            } else if (servicioId == '2') {  // ID para Tinas
                horaSelect.innerHTML += '<option value="14:00">14:00</option>';
                horaSelect.innerHTML += '<option value="14:30">14:30</option>';
                horaSelect.innerHTML += '<option value="17:00">17:00</option>';
                horaSelect.innerHTML += '<option value="19:00">19:00</option>';
                horaSelect.innerHTML += '<option value="19:30">19:30</option>';
                horaSelect.innerHTML += '<option value="21:30">21:30</option>';
                horaSelect.innerHTML += '<option value="22:00">22:00</option>';
            } else if (servicioId == '3') {  // ID para Masajes
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

            console.log("Opciones de horario actualizadas:", horaSelect.innerHTML);
        });
    });
});
