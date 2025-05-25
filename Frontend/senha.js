function validateLogin() {
    var nome = document.getElementById("nome").value;
    var senha = document.getElementById("senha").value;
    
    if (nome === "admin" && senha === "adm123") {
        
    window.location.href = "admin.html";
    } else {
        alert("Nome de usuário ou senha incorretos!");
    }
}

document.getElementById("loginButton").addEventListener("click", validateLogin);