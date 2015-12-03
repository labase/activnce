<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title>Teste Wisconsin</title>
<style type="text/css" media="screen">
@import "${tg.url('/static/css/telaTeste.css')}";
</style>
</head>
<body>
    <p>A carta:</p>
    <div class="carta puxada ${cartaPuxada.color}">
        <img src="${cartaPuxada.img}" alt="${cartaPuxada.pegaAtributosCarta()}"
             title="${cartaPuxada.pegaAtributosCarta()}" />
        <img py:for="item in range(cartaPuxada.num-1)"
             src="${cartaPuxada.img}" alt=" "
             title=" " />
    </div>
    <p>Combina com qual das cartas abaixo? Tecle ENTER no link desejado.</p>
    <ul>
        <li py:for="(indice, carta) in enumerate(cartasEstimulo)">
            <a href="/resultadoTestaCartas?opcao=${indice}">
                <div class="carta ${carta.color}">
                    <img src="${carta.img}" alt="${carta.pegaAtributosCarta()}"
                         title="${carta.pegaAtributosCarta()}" />
                    <img py:for="item in range(carta.num-1)"
                         src="${carta.img}" alt=" "
                         title=" " />
                </div>
            </a>
        </li>
    </ul>
    <br />
</body>
</html>
