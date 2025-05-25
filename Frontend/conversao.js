const precoInput = document.getElementById('preco');

  precoInput.addEventListener('input', function (e) {
    let value = e.target.value.replace(/\D/g, ''); 
    value = (parseInt(value) / 100).toFixed(2); 
    e.target.value = value
      .toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  });