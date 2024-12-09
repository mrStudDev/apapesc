function mascaraCEP(input) {
  console.log("mascaraCEP chamada. Valor atual:", input.value);
  let valor = input.value.replace(/\D/g, ''); // Remove caracteres não numéricos
  if (valor.length > 8) valor = valor.slice(0, 8); // Limita a 8 caracteres

  if (valor.length > 5) {
      input.value = `${valor.slice(0, 5)}-${valor.slice(5)}`; // Aplica a máscara "00000-000"
  } else {
      input.value = valor; // Exibe apenas os números digitados
  }
}


