/**
 * @license Copyright (c) 2003-2013, CKSource - Frederico Knabben. All rights reserved.
 * For licensing, see LICENSE.html or http://ckeditor.com/license
 */

// tentativa de permitir tags video e source: não funcionou 10/10/2013
CKEDITOR.config.allowedContentRules = true; 

CKEDITOR.editorConfig = function( config ) {
	
	// %REMOVE_START%
	// The configuration options below are needed when running CKEditor from source files.
	config.plugins = 'dialogui,dialog,about,a11yhelp,dialogadvtab,basicstyles,bidi,blockquote,clipboard,button,panelbutton,panel,floatpanel,colorbutton,colordialog,templates,menu,contextmenu,div,resize,toolbar,elementspath,enterkey,entities,popup,filebrowser,find,fakeobjects,flash,floatingspace,listblock,richcombo,font,forms,format,horizontalrule,htmlwriter,iframe,wysiwygarea,image,indent,indentblock,indentlist,smiley,justify,link,list,liststyle,magicline,maximize,newpage,pagebreak,pastetext,pastefromword,preview,print,removeformat,save,selectall,showblocks,showborders,sourcearea,specialchar,menubutton,scayt,stylescombo,tab,table,tabletools,undo,wsc,youtube,iframedialog,eqneditor';
	config.skin = 'moonocolor';
	// %REMOVE_END%

	// Define changes to default configuration here. For example:
	// config.language = 'fr';
	// config.uiColor = '#AADC6E';
	
	config.width='100%';
	config.height=500;
};

CKEDITOR.URLRelative = function(field) {
    // remove caracteres do inicio do texto em value de 'field' caso o texto
    // seja igual ao hostname atual (c/s protocolo c/s 'www.', c/s porta)
    var url=field.getValue(), hostName = window.location.hostname;
    if (hostName.substr(0,4)=='www.') hostName=hostName.substr(4);
    var hostUrl = url.toLowerCase().match(/^(https?:\/\/)?(www\.)?([0-9a-z_\.\-]+)(:[0-9]+)?/);
    var hostTest = (!hostUrl)?null:hostUrl[3];
    if (hostName==hostTest) {
        field.allowOnChange=false;
        field.setValue(url.substr(hostUrl[0].length));
        field.allowOnChange=true;
    }
    return field.getValue();
};

