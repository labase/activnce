
  function getFontSize(min,max,val) {
    return Math.round((120.0*(1.0+(1.5*val-max/2)/max)));
  }
 
  function generateCloud(tags, link, logarithmic) {
    var min = 10000000000;
    var max = 0;
    var tagcount;
    var lines = new Array();

    for(var key in tags) {
      tagcount = parseFloat(tags[key])

      lines[lines.length] = [tagcount, key];
      if(tagcount > max) 
        max = tagcount;
      if(tagcount < min)
        min = tagcount;
    }
	
	/* ordenação alfabética */
    lines.sort(function (a,b) {
                 var A = a[1].toLowerCase();
                 var B = b[1].toLowerCase();
                 return A>B ? 1 : (A<B ? -1 : 0);
                });
                
    /* ordenação pela frequencia
    lines.sort(function (a,b) {
                 var A = a[0]
                 var B = b[0]
                 return A>B ? -1 : (A<B ? 1 : 0);
                });
    */
                
    var html = "<style type='text/css'>#jscloud a:hover { text-decoration: underline; }</style> <div id='jscloud'>";
    if(logarithmic) {
      max = Math.log(max);
      min = Math.log(min);
    }
    for(var i=0;i<lines.length;i++) {
      var val = lines[i][0];
      if(logarithmic) val = Math.log(val);
      var fsize = getFontSize(min,max,val);
      html += " <a href='"+link+encodeURIComponent(lines[i][1])+"' style='font-size:"+fsize+"%;' title='"+lines[i][0]+"'>"+lines[i][1]+"</a> ";
    }
    html += "</div>";

    return html
  }
