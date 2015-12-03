
var canRating = false;
var rating;

// mostra as estrelinhas da avaliacao conforme posicao do mouse
function overRating(n) {
   if (canRating)
      document.getElementById("imgRating").src = "/static/imagens/avalia/estrelas_"+n+".png";
}

// define e habilita a avaliacao (marca a estrela correpondente quando setado)
function setRating(n) {
   if (n!='') {
      document.getElementById("imgRating").src = "/static/imagens/avalia/estrelas_"+n+".png"
      document.getElementById("slideRating").style.visibility = "visible";
      document.getElementById("slideConfirm").style.visibility = "hidden";
      canRating = (n=='0');
   }
}

// envia pedido via http para gravar avalicao feita
function sendRating(n) {
   var  xmlhttp = (window.XMLHttpRequest) ? new XMLHttpRequest() : new ActiveXObject("Microsoft.XMLHTTP");
   xmlhttp.onreadystatechange = function() {
      if (xmlhttp.readyState==4 && xmlhttp.status==200) {
         setRating(xmlhttp.responseText);
      }
   }
   
   xmlhttp.open("GET","/rating/new/"+escopo+"/"+objeto+"?tipo="+tipo+"&nota="+n,true);
   xmlhttp.send();
}

// mostra menu de confirmacao da avaliacao apos ser clicada uma estrela
function waitRating(n) {
   if (canRating) {
      canRating = false;
      document.getElementById("slideConfirm").style.visibility = "visible";
      document.getElementById("textConfirm").innerHTML = "Deseja avaliar este artefato com "+n+" estrela"+((n>1)?"s":"")+"?";
      rating = n;
   }
}

// acao de cancelar no menu de confirmacao da avalicao
function cancelRating() {
   canRating = true;
   document.getElementById("slideConfirm").style.visibility = "hidden";
   overRating(0);
}

// acao de confirma no menu de confirmacao da avalicao
function confirmRating() {
   sendRating(rating);
}