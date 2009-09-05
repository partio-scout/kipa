function enterToTab(formRef, focusAny) /*2843295374657068656E204368616C6D657273*/
{
 for(var i=0, e=formRef.elements, len=e.length, hasNext=true; i<len && hasNext; i++)
  if( e[i].type && /^text|password|file/.test( e[i].type ) )
  {
    for(var j=i+1; j<len &&  (!e[j].type || /submit|reset/.test(e[j].type)||( focusAny ? /hidden/.test(e[j].type): !/^text|password|file/.test(e[j].type)) ); j++)
    ;
    hasNext = j!=len;
   
    e[i].onkeypress=(function(index, notLast)
    {
      return function()
      {
       var ta=false, k=(arguments[0]?arguments[0].which:window.event.keyCode )!=13;
       
       if(!k && !(ta=(this.type=='textarea'&&this.value.length>0)) && notLast)
        this.form.elements[index].focus(); 
     
       return k||ta;   
      }
    })(j, hasNext);  
  } 
}