// static/js/municipio_select.js

document.addEventListener('DOMContentLoaded', function() {
  const municipioSedeSelect = document.getElementById('id_municipio_sede');
  const novoMunicipioSedeContainer = document.getElementById('novo-municipio-sede-container');

  function toggleNovoMunicipioSede() {
    const selectedOption = municipioSedeSelect.options[municipioSedeSelect.selectedIndex];
    if (selectedOption.value === '-1') {
      novoMunicipioSedeContainer.style.display = 'block';
    } else {
      novoMunicipioSedeContainer.style.display = 'none';
    }
  }

  municipioSedeSelect.addEventListener('change', toggleNovoMunicipioSede);

  // Chame a função inicialmente para definir o estado correto
  toggleNovoMunicipioSede();
});
