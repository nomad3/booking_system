document.addEventListener('DOMContentLoaded', function () {
    const servicioFields = document.querySelectorAll('select[name$="-servicio"]');
    
    servicioFields.forEach(function(servicioField) {
        servicioField.addEventListener('change', function () {
            const servicioId = this.value;
            const horaField = this.closest('tr').querySelector('select[name$="-hora"]');

            // Limpia el campo de hora antes de cargar los nuevos horarios
            horaField.innerHTML = '<option value="">Seleccione un horario</option>';

            if (servicioId) {
                // Aquí se deben definir los horarios por categoría de servicio
                const horariosPorCategoria = {
                    1: ['16:00', '17:00'], // Ejemplo para ID de servicio 1 (Cabañas)
                    2: ['14:00', '14:30', '17:00', '19:00', '21:30'], // Ejemplo para ID de servicio 2 (Tinas)
                    3: ['13:00', '14:15', '15:30', '18:00', '20:30'], // Ejemplo para ID de servicio 3 (Masajes)
                };

                // Obtén la categoría de horarios para este servicio
                const horarios = horariosPorCategoria[servicioId];

                if (horarios) {
                    // Cargar los horarios en el campo de hora
                    horarios.forEach(function (hora) {
                        const option = document.createElement('option');
                        option.value = hora;
                        option.text = hora;
                        horaField.appendChild(option);
                    });
                } else {
                    // Si no hay horarios disponibles para este servicio
                    horaField.innerHTML = '<option value="">No hay horarios disponibles</option>';
                }
            }
        });
    });
});
