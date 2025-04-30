//Funcion para añadir comentario
document.getElementById('comentarioForm').addEventListener('submit', function (e) {
  e.preventDefault();

  const form = e.target;
  const formData = new FormData(form);
  formData.append('tipo_objeto', '{{ mediafile.tipo_objeto }}');  // <<< AGREGAS ESTO

  fetch("{% url 'index:ajax_add_comment' mediafile.id %}", {
    method: 'POST',
    headers: {
      'X-CSRFToken': '{{ csrf_token }}'
    },
    body: formData
  })
    .then(response => response.json())
    .then(data => {
      if (!data.error) {
        const nuevoComentario = `
    <div class="card mb-3 shadow-sm border-start border-5 border-primary">
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-center mb-2">
          <a href="#" class="fw-bold text-decoration-none text-primary">${data.usuario}</a>
          <small class="text-muted">${data.fecha}</small>
        </div>
        <p class="mb-0">${data.texto}</p>
      </div>
    </div>
  `;
        document.getElementById("comentariosContainer").insertAdjacentHTML('afterbegin', nuevoComentario);

        form.reset();
      } else {
        alert('Hubo un error: ' + data.error);
      }
    })
    .catch(err => alert("Error al enviar el comentario."));
});
//Funcion para añadir comentario



