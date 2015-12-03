

function loadXMLNoticiaSistema() {
	registry_id = "Priv_Global_Admin";
	
	// faz requisição assíncrona do xml com notícias de um registry_id
	// chamado no control-panel de community.
    if (window.XMLHttpRequest){
        // code for IE7+, Firefox, Chrome, Opera, Safari
        xmlhttp=new XMLHttpRequest();
    }
    else {
        // code for IE6, IE5
        xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
    }
    xmlhttp.onreadystatechange = function() {
        var txt="";
      
        if (xmlhttp.readyState==4 && xmlhttp.status==200){
        
            // interpreta o XML com as notícias deste registry_id
            x=xmlhttp.responseXML.documentElement.getElementsByTagName("noticia");
            if (x.length>0) {
                for (i=0;i<x.length;i++){
                    xx=x[i].getElementsByTagName("titulo");
                    dd=x[i].getElementsByTagName("dt_publicacao");
                    TAM_STR_MSG = 80
                    txtNoticia = xx[0].firstChild.nodeValue.substr(0, TAM_STR_MSG);
           			if (xx[0].firstChild.nodeValue.length > TAM_STR_MSG) txtNoticia += "...";
                               
                    txt=txt + dd[0].firstChild.nodeValue + " - <a href='" + x[i].getAttribute("url") + "'>" + txtNoticia + "</a><br/>";
                }

            }
		    showNoticiaSistema(txt);

        }   //controlPanelMSG ??????
    }
    xmlhttp.open("GET","/noticia/xml/"+registry_id, true);
    xmlhttp.send();
}


function showNoticiaSistema(txt){
    if (txt) {
        id = document.getElementById("controlPanelMSG");
        id.style.padding = "5px 15px";
        id.innerHTML = txt;
    }
}



// Monta popup com notícias de uma comunidade
// Inclui notificação de usuários online no Chat

   
function loadXMLNoticia(registry_id) {
	// faz requisição assíncrona do xml com notícias de um registry_id
	// chamado no control-panel de community.
    if (window.XMLHttpRequest){
        // code for IE7+, Firefox, Chrome, Opera, Safari
        xmlhttp=new XMLHttpRequest();
    }
    else {
        // code for IE6, IE5
        xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
    }
    xmlhttp.onreadystatechange = function() {
        var txt="";
      
        if (xmlhttp.readyState==4 && xmlhttp.status==200){
        
            // interpreta o XML com as notícias deste registry_id
            x=xmlhttp.responseXML.documentElement.getElementsByTagName("noticia");
            if (x.length>0) {
                for (i=0;i<x.length;i++){
                    xx=x[i].getElementsByTagName("titulo");
                    dd=x[i].getElementsByTagName("dt_publicacao");
                    txt=txt + dd[0].firstChild.nodeValue + " - <a href='" + x[i].getAttribute("url") + "'>" + xx[0].firstChild.nodeValue + "</a><br/>";
                }

            }
		    showPopupNoticia(registry_id, registry_id, txt);

        }
    }
    xmlhttp.open("GET","/noticia/xml/"+registry_id, true);
    xmlhttp.send();
}

String.prototype.reverse = function () {
    return this.split('').reverse().join('');
};

String.prototype.replaceLast = function (what, replacement) {
    return this.reverse().replace(new RegExp(what.reverse()), replacement.reverse()).reverse();
};

function showPopupNoticia(registry_id, chat_name, txt){
	// Verifica se há usuários online no chat neste momento, acrescentando uma notificação no popup de notícias
	// e exibindo o popup de notícias.
	// Chamado diretamente no control-panel de member e ao exibir página home de member.
	// Ou chamado indiretamente de loadXMLNoticias para acrescentar a informação de usuários no chat na 
	// lista de notícias (que vem no parâmetro txt).
	// Se o chat é de uma comunidade, registry_id==chat_name.
	// Se o chat é entre 2 pessoas, registry_id sou eu e chat_name é a pessoa falando comigo.
	
	header = txt ? "<p style='font-size: 12pt; font-weight: bold;'>Notícias</p>" : "";
	if (usuarios_no_chat.length>0){
		// pega nomes de, no máximo, 3 usuários no chat
	    user_names = usuarios_no_chat.slice(0,3).join(", ")
		user_names = user_names.replaceLast(', ', ' e ');

		// inclui data se há outras notícias
		if (txt) {
		    var hoje = new Date();
		    var dia = hoje.getDate();
		    if (dia < 10) dia = "0" + dia;
		    var mes = hoje.getMonth()+1;
		    if (mes < 10) mes = "0" + mes;
			txt +=  dia + "/" + mes + " - "
		}
		
		// monta o link para o chat
	    txt += "<a href='/chat/" + chat_name + "'>" + user_names 
     	if (usuarios_no_chat.length-3>0){
     		txt += " mais " + usuarios_no_chat.length-3 + " usuários "
     	}
     	txt += (usuarios_no_chat.length==1) ? " está" : " estão";
     	txt += " online no chat"
     	
     	if (registry_id==chat_name)	txt += " de " + registry_id 
     	txt += "</a>.<br/>"
	    
	}
	if (txt) {
		txt = header + txt;
		TINY.box.show({html:txt,width:600,height:400});
	}   
}
                
                
                