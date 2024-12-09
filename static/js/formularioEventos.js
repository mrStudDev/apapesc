document.addEventListener("DOMContentLoaded", function() {
  const telefoneInputs = document.querySelectorAll('[oninput="mascaraTelefone(this)"]');
  telefoneInputs.forEach(input => {
    input.addEventListener('input', function() {
      mascaraTelefone(input);
    });
  });

  const cpfInputs = document.querySelectorAll('[oninput="mascaraCPF(this)"]');
  cpfInputs.forEach(input => {
    input.addEventListener('input', function() {
      mascaraCPF(input);
    });
  });

  const cepInputs = document.querySelectorAll('[oninput="mascaraCEP(this)"]');
  cepInputs.forEach(input => {
    input.addEventListener('input', function() {
      mascaraCEP(input);
    });
  });
});
