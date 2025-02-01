function mascaraTelefone(input) {
  let valor = input.value.replace(/\D/g, ''); // Remove não-números
  if (valor.length > 11) valor = valor.slice(0, 11);

  if (valor.length > 10) {
    input.value = `(${valor.slice(0, 2)})${valor.slice(2, 7)}-${valor.slice(7)}`;
  } else if (valor.length > 5) {
    input.value = `(${valor.slice(0, 2)})${valor.slice(2, 6)}-${valor.slice(6)}`;
  } else if (valor.length > 2) {
    input.value = `(${valor.slice(0, 2)})${valor.slice(2)}`;
  } else {
    input.value = valor;
  }
}
