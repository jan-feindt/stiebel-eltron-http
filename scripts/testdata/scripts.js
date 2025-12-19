// JavaScript Document
$(document).ready(function(){
  if(typeof uhrzeit == 'function') uhrzeit();
  
	$("#content div.edit div.green,#buehne div.buehne div.green,#buehne div.buehne div.edit").bind("click", function(e){
	 	closeAllBoxes();
	 	
	 	var blackDiv = $(this).parent().parent().children("div.black");
    	 	
	 	if(blackDiv.css("display") == "none"){
	 		blackDiv.fadeIn("fast");
	 		$('body').bind('click', function(e) {
			 	closeAllBoxes();
		  		$(this).unbind(e);
			});
			e.stopPropagation();
	 		blackDiv.bind('click', function(e) { e.stopPropagation(); });
	 	}		
	});

	$("div.dropdown").bind("click", function(e){
	 	var blackDiv = $(this).children("div.black");

	 	if(blackDiv.css("display") == "none"){
	 		$(this).children("img.dropdown").attr("src","../pics/icon_edit_dropdown_close.png");
	 		blackDiv.fadeIn("fast");
	 		$('body').bind('click', function(e) {
			 	closeAllBoxes();
		  		$(this).unbind(e);
			});
			e.stopPropagation();
	 		blackDiv.bind('click', function(e) {
			 	closeAllBoxes();
			 	e.stopPropagation(); 
			});
	 	}
		
	});
  
  $("div.help_txt_box_fehlerliste").parent("td").bind("click", function(e){
    closeAllBoxes();
    var hlpobj = $(this).children("div.help_txt_box_fehlerliste");
    if( hlpobj.css( "display" ) == "none" ){
      $(hlpobj).css("width",$(this).width() + 18);
      $(hlpobj).show("fast");
      $('body').bind('click', function(e) {
			 	closeAllBoxes();
		  		$(this).unbind(e);
			});
      e.stopPropagation();
    }
  });
	
	$("#nav").children("div.nav").bind("mouseover", function(e){
		closeAllBoxes();
	});
	
	$(".edit_black").bind("mouseover", function(){
	 	$(this).attr("src","../pics/icon_edit_close_active.gif");
	});
	$(".edit_black").bind("mouseout", function(){
	 	$(this).attr("src","../pics/icon_edit_close.gif");
	});
	$(".edit_black_big").bind("mouseover", function(){
	 	$(this).attr("src","../pics/icon_edit_close_big_active.gif");
	});
	$(".edit_black_big").bind("mouseout", function(){
	 	$(this).attr("src","../pics/icon_edit_close_big.gif");
	});
	
	//Änderungen darstellen
	$('label.bool').click(function(event) {
		var $ich = $(this);
		var $act = $ich;
		var $radio = $(this).prev();
		//weiter im programm 
		var klasse = $ich.attr("class");
		var name = $ich.prev().attr("name");
		//Beide Buttons aktualisieren
		$("[name="+name+"] + label").each(function() {
			//Grafik aktualisieren
			var bild = $(this).css("background-image");
			if ($ich.attr("class")==$(this).attr("class")) {
				bild = bild.replace(/off\./, "on.");
			} else {
				//Änderung?
				if ($(this).prev().attr("checked")) {
					bild = bild.replace(/on\./, "off.");
					//Wir haben etwas geändert!
					valueChanged = true;
				}
			}
			$(this).css("background-image",bild);
  		});
		//Radio-Button status ändern
		$ich.prev().attr("checked","checked");
	});
	
	
	$(".tabs").each(function(){
		var tabNav = $(this).children(".tab_nav").children(".tab_nav_entry");
		var tabPanel = $(this).children(".tab_panel");
		
		tabPanel.each(function(){
			var nextStep = $(this).find("a.next_step");
			var panelIndex = tabPanel.index($(this));
			var nextIndex = panelIndex+1;
			nextStep.bind("click",function(){
			    //alert(nextIndex);
				tabNav.removeClass("selected");
				tabNav.eq(panelIndex).addClass("completed");
				tabNav.eq(nextIndex).addClass("selected");
				tabPanel.hide();
				tabPanel.eq(nextIndex).show();
			});
		});
		
		
		//dies noch auskommentieren, ist nur zur schnelleren Navigation für die Entwicklungsphase
		tabNav.bind("click",function(){
			tabNav.removeClass("selected");
			$(this).addClass("selected");
			tabPanel.hide();
			tabPanel.eq(tabNav.index($(this))).show();
		});
		//
		
		
	});
	
  if($("div#netzwerk")){ netzwerk() }
	
	$("div#netzwerk input[type=checkbox]").click(function(){ netzwerk() });
	
	$("div#netzwerk input[type=text]").not(".excludeNumberValidate").bind("blur",
  		function () {
			
			validateNetworkInputFields(this)
  		}
	);
	
	// LFR
	if($("div#netzwerk_sma_energy_meter")){ refreshNetworkSmaEnergyMeterPage() }
	
	$("div#netzwerk_sma_energy_meter input[type=checkbox]").click(function(){ refreshNetworkSmaEnergyMeterPage() });
	
	$("div#netzwerk_sma_energy_meter input[type=text]").not(".excludeNumberValidate").bind("blur",
  		function () {
			
			validateNetworkInputFields(this)
  		}
	);
	// LFR
	
	$("div.button").bind("mouseover mouseout",function(){
		$(this).toggleClass("button_hover");
	});
  $("div.button2").bind("mouseover mouseout",function(){
		$(this).toggleClass("button2_hover");
	});
	
  $('body').bind("click",function(e){
		$('div.select_box_entries').each(function(){
			$(this).prev().removeClass("select_box_active");
			if (!$(this).hasClass('none')) {
				if (!$(this).siblings('input.select_value').val()) $(this).siblings('div.select_box_button').children('a.select').text($(this).siblings('input.select_default').val());
				else $(this).siblings('div.select_box_button').children('a.select').text($(this).siblings('input.select_value').val());
				$(this).toggleClass('none');
			}
		});
	});

	$('a.select').each(function(){
		$(this).bind("click",function(e){
			e.stopPropagation();
			if ($(this).parent().siblings('div.select_box_entries').hasClass('none')) {
				if ($(this).text() != $(this).parent().siblings('input.select_default').val()) $(this).text($(this).parent().siblings('input.select_default').val());
			}
			$(this).parent().siblings('div.select_box_entries').toggleClass('none');
			$(this).parent().toggleClass('select_box_active');
		})
	});
	$('a.select_entry').each(function(){
		$(this).bind("click",function(e){
			e.stopPropagation();
			$(this).parent().siblings('input.select_value').val($(this).text());
			$(this).parent().siblings('div.select_box_button').children('a.select').text($(this).text());
			$(this).parent().toggleClass('none');
			$(this).parent().siblings('div.select_box_button').removeClass('select_box_active');
		})
	});
	
	
   $(".toggle_list").each(function(){
      var toggleList = $(this);
     	var toggleLinks = toggleList.find("a.toggle");
     	var toggleText = toggleList.find("div.toggle_text");
     	var showAll = toggleList.children("a.show_all");
     	var hideAll = toggleList.children("a.hide_all");
     	
     	// Alle Aufklappeinträge schliessen
		toggleText.hide();
     	showAll.show();
     	
    	toggleLinks.bind("click",function(){
        	var link = $(this);
        	link.next().toggle();
        	link.toggleClass("opened");
        	return false;
     	});
     	showAll.bind("click",function(){
        	toggleText.show();
        	toggleLinks.addClass("opened");
        	showAll.hide();
        	hideAll.show();
        	return false;
     	});
		  hideAll.bind("click",function(){
        	toggleText.hide();
        	toggleLinks.removeClass("opened");
        	hideAll.hide();
        	showAll.show();
        	return false;
     	});
   });

  // OTTO //
  if(typeof jsvalues != "undefined")
	  for(var i in jsvalues)
      if(typeof jsvalues[i] != "undefined")
        document.getElementById(jsvalues[i]['id']).value = jsvalues[i]['val'];
  // OTTO //
	
});

$('document').ready(function(){
	$(".ialigned").vAlign("div");
});

(function ($) {
	$.fn.vAlign = function(container) {
		return this.each(function(i){
			if(container == null) {
				container = 'div';
			}
			var pel = $(this).children(container + ":first");
			var el = pel.children(container + ":first");
			var elh = $(el).height(); //new element height
			if (elh) {
				var ph = $(this).height(); //parent height
				//Funktioniert hier nicht: Immer Höhe des Icons nehmen!
				ph = 11;
				var nh = (ph - elh) / 2; //new height to apply
				var oldmargin = $(pel).css('margin-top');
				$(el).css('margin-top', nh);
			}
		});
	};
})(jQuery);

// OTTO -->
function netzwerk() 
{
  //alert("ich bin in der netzwerk fkt");
  $("input.ebene1,input.ebene2,input.ebene3").attr('disabled', true);
  $("div.ebene1,div.ebene2,div.ebene3").addClass("off");
  if(!$("input#netzwerk_dhcp").attr('checked'))
  {
      $("input.ebene1").removeAttr('disabled');
      $("div.ebene1").removeClass("off");
   // if($("input#netzwerk_gateway").attr('checked')){
      $("input.ebene2").removeAttr('disabled');
      $("div.ebene2").removeClass("off");
      //if($("input#netzwerk_dns-server").attr('checked')){
      $("input.ebene3").removeAttr('disabled');
      $("div.ebene3").removeClass("off");
		
      //}
    //}
  }
   if($("input#netzwerk_proxy").attr('checked'))
   {
       //alert("proxy gesetzt");
	   if(document.getElementById("proxy"))
	   {
		  var mydiv = document.getElementById("proxy");
          mydiv.style.display = 'block';
	   }
   }
   
   
  if(!$("input#netzwerk_proxy").attr('checked'))
   {
      //alert("proxy nicht gesetzt");
        if(document.getElementById("proxy"))
		{
		  var mydiv = document.getElementById("proxy");
          mydiv.style.display = 'none';
		}
		
   }
}
// <-- OTTO

// LFR
function refreshNetworkSmaEnergyMeterPage() {
	
	if($("input#netzwerk_sma_energy_meter_checkbox").attr('checked'))
	{
		if(document.getElementById("netzwerk_sma_energy_meter_settings"))
		{
			var settingsForm = document.getElementById("netzwerk_sma_energy_meter_settings");
			settingsForm.style.display = 'block';
		}
	}
	else
	{
		if(document.getElementById("netzwerk_sma_energy_meter_settings"))
		{
			var settingsForm = document.getElementById("netzwerk_sma_energy_meter_settings");
			settingsForm.style.display = 'none';
		}
	}
}

// LFR
function validateNetworkInputFields(thisObject) {
	
	$(thisObject).attr('value', parseInt($(thisObject).attr('value')));
	
	if($(thisObject).hasClass("portNumberValidate")) {
		
		if($(thisObject).attr('value') > 65535) {
			
			$(thisObject).attr('value', 65535);
  		}
		
	} else {
		
		if($(thisObject).attr('value') > 255) {
			
			$(thisObject).attr('value', 255);
		}
	}
	
	if($(thisObject).attr('value') < 0) {
		
		$(thisObject).attr('value', 0);
	}
	
	if($(thisObject).attr('value') == "NaN") {
		
		$(thisObject).attr('value', "");
	}
}
// LFR

//Alle Boxen auf der Seite schließen wenn neue geöffnet werden
function closeAllBoxes() {
 	var $elems = $("#buehne div.buehne, #content div.edit, #content div.dropdown");
	$elems.each(function() {
		$(this).children("div.black").fadeOut("fast");
	});
	//Krücke
	$("#content div.dropdown").children("img.dropdown").attr("src","../pics/icon_edit_dropdown.png");
  $("#subsubnav").slideUp('fast');
  $("div.help_txt_box_fehlerliste").each(function(){$(this).hide("fast")});
}

function getValue(id, datatype) {
	var val = "";
	var input = eval("document.forms['werte']."+id);
	//var validcode = getValidcode(datatype);
	if (input) {
		if (input.tagName=="SELECT") {
			var index = input.selectedIndex;
			val = input.options[index].value;
		} else if (input.tagName=="RADIO") {
			var index = input.selectedIndex;
			val = input.options[index].value;
		} else if (input.tagName=="INPUT") {
			val = input.value;
		}
		if (datatype!='string' && val!==undefined && val!="") {   
			var tmp = val;
			console.log("getValue:"+ " " + val);
			var american = tmp.replace(/,/, "\.");
			
			//Dezimalzahlen "amerikanisieren"
			/*var floating = val.match(/^(-)?(\d+)?([,.])(\d+)?$/);
			if ((datatype=="float" || datatype=="double") && floating) {
				if (floating[2]==undefined || floating[2]=="") tmp = "0"+tmp;
				if (floating[4]==undefined || floating[4]=="") tmp += "0";
				var american = tmp.replace(/,/, "\.");
				//console.log("american" + american);
				if (parseFloat(american)!="" && !isNaN(parseFloat(american))) {
					//console.log("Wert vorher" + tmp);
					//Nachdem parsen verschwindet das Komma
				}
			}*/
		}
	}
		console.log("getValue nachher:"+ " " + american);
		return american;
	
	//	return val  /*= val.replace(",", ".") */;
}

function setValue(id, val, otto) {
	console.log("setValue Wert ist" + val);
	
	var input = eval("document.forms['werte']."+id);
	if (input) {
		if(otto)
		{   console.log("otto");
			
        	// OTTO hinzugefuegt
			var european = val.replace(/^(-)?(.*\d)\.(\d.*)?$/g, "$1$2,$3");      // OTTO hinzugefuegt
			val = val;                                                       // OTTO hinzugefuegt
		}
		else
		{                                                                  // OTTO hinzugefuegt
      var tester = /^(-)?(\d+)\.(\d+)$/
  		var floating = tester.test(val);
		
		console.log("Floating ist" + floating);
  		if (floating) {
  			//Wir haben etwas geändert!
  			valueChanged = true;
  			if (typeof val != "number") val = Number(val);
			console.log("setValue Der neue Wert ist"+ val)
  
  			var datatype = getDatatype(val);
			console.log("Dtentyp des Wertes ist"+datatype);
  	      	if (datatype == "double") {
  	          	val = val.toFixed(2);
  	        } else if (datatype == "float") {
  	            val = val.toFixed(1);
				console.log("toFixed"+val);
  	        }
            
  			var european = val.replace(/^(-)?(.*\d)\.(\d.*)?$/g, "$1$2,$3");
			console.log("european"+european);
  			val = val;
		}
	}                                                         // OTTO hinzugefuegt
  	input.value = val;
	console.log("kein floating"+val);
  	//Wir haben etwas geändert!
  	valueChanged = true;
	}
}

var values = new Array();
var valueChanged = false;
var errorBrain = new Array();

function getValidcode(datatype) {
	if (datatype=='double') return '(-)?(\\d+)?(\\.)?(\\d)?(\\d)?';
	else if (datatype=='float') return '(-)?(\\d+)?(\\.)?(\\d)?';
	else if (datatype=='int') return '(-)?(\\d+)?';
	else return '.*';
}
function reminder(id) {
	console.log("reminder");
	//onkeydown = vorher!
	if (id!="") {
		//merken
		values[id] = getValue(id,'');
	}
}

function validate(id, datatype, min, max) {
	console.log("validate");
	if (id!="") {
		//onkeyup = nachher!
		var $cal = $("#cal"+id);
		var error = false;
		var val = getValue(id, datatype);	
		//Eingabe gelöscht?
  		if (val==""){
        $cal.addClass("fehler");
        error=true;
      }
	  	//Eingabe Negativ? Ist jetzt erlaubt!
  		//if (val<"0") error=true;
		
		//Wenn das Feld leer ist können wir auch nicht validieren - "Entfernen" gedrückt?
		if (val!="") {
			console.log("Feld ist leer")
			var goon = raw_validate(id, datatype, val);			
			if (goon) {
				if (!error && datatype!="string" && (min!="" || max!="")) {
					//Zahl?
					if (!isNaN(val)) {
						if (min!="") {
							var minval = min;
							if (parseFloat(min)!="" && !isNaN(parseFloat(min))) minval = parseFloat(min);
							else if (
							(min)!="" && !isNaN(parseInt(min))) minval = parseInt(min);
							if (val < minval) {
								error = true;
							}
						}
						if (max!="") {
							var maxval = max;
							if (parseFloat(max)!="" && !isNaN(parseFloat(max))) maxval = parseFloat(max);
							else if (parseInt(max)!="" && !isNaN(parseInt(max))) maxval = parseInt(max);
							if (val > maxval) {
								error = true;
							}
						}
					}
				}
				if (error) {
					$cal.addClass("fehler");
			    /*
			    	setValue(id, val);
			    	errorBrain[id] = 1;
          */
					//alert("Fehler: "+id+"="+val);
					return false;
				} else {
					$cal.removeClass("fehler");
			    	errorBrain[id] = 0;
					setValue(id, val);
				}
			   
				//Wir haben etwas geändert!
				valueChanged = true;
			}
		}
	}
	return true;
}

function raw_validate(id, datatype, val) {
	console.log("raw validate");
	var $cal = $("#cal"+id);
	var error = false;
	if (id!="" && val!="") {
		if (datatype!="") {
			//gültiger Wert?
			var validcode = getValidcode(datatype);
			var v = eval("/^"+validcode+"$/");
			if (!v.test(val)) error = true;
		}
	}
	if (error) {
		$cal.addClass("fehler");
		setValue(id, values[id]);
		//alert("Fehler: "+id+"="+val);
		return false;
	} else {
		$cal.removeClass("fehler");
		setValue(id, val);
	}

	//Wir haben etwas geändert!
	valueChanged = true;
	return true;
}


$(document).ready(function(){
	console.log("document ready");
	var focusStorage = {};

	$("input.edit").each(function(){
	
		$(this).bind("focus", function(){
			var inputID = this.id;
			if(typeof valSettings !== 'undefined') {
				focusStorage[inputID] = getValue(inputID ,valSettings[inputID]['type']);
				console.log("Element"+ " " + focusStorage[inputID]);
			}
		});

		$(this).bind("blur", function(){
			var inputID = this.id;
			if(typeof valSettings === 'undefined') {
				return true;
			} else {
				if(focusStorage[inputID] != getValue(inputID ,valSettings[inputID]['type'])) {
					return validate(inputID ,valSettings[inputID]['type'],valSettings[inputID]['min'],valSettings[inputID]['max']);
				} else {
					return true;
				}
			}
		});
	
		$(this).bind("keyup", function(e){
			console.log("keyup");
			var kCode = e.keyCode;
		  	var inputID = this.id;
			//Überpruefen welche taste gedruckt wurde (9=tab)
		  	if(kCode != 8 && kCode !=46 && kCode !=9)
			{
				if(typeof valSettings === 'undefined') 
				{
					console.log("valSettings undefined");
					return true;
				} else 
				  {
					 var val = getValue(inputID, valSettings[inputID]['type']);
					 console.log("keyup Wert ist:"+ val);
					 return raw_validate(inputID,valSettings[inputID]['type'],val);
				  }
			}
		});
		$(this).bind("keydown", function(){
			reminder(this.id);
		});
			

	});
});



function change(id, what, min, max, step, geh) {
	console.log("change");
	console.log("change step ist:"+ step)
	console.log("change what ist:"+ what)
	console.log("change geh ist:"+ what)
	var val = getValue(id,'');
	console.log("change der alte Wert" + val);
	var tmp = ''+step;
	var floating = tmp.match(/\d\.\d/);
    var datatype = getDatatype(step);
	if (val==undefined || val=="") val = min;
  if( parseFloat(step)==0 ) step=1; // OTTO

	//Keine negativen Zahlen! Jetzt doch möglich!
	if (floating) {
		if (what=="+" && parseFloat(val)==0) val = 0;//val * -1;
	  if (what=="-" && parseFloat(val)==0) val = 0;//val * -1;
	}
	
	if (what=="+") {
		val = parseFloat(val) + parseFloat(step);
  } else if (what=="-") {
  	val = parseFloat(val) - parseFloat(step);
 	}
  
  var stepcheck = parseFloat(step);
  console.log("stepcheck"+stepcheck);
  												// OTTO hinzugefuegt
  // for(i=0;1>stepcheck;i++) stepcheck *= 10;   // OTTO hinzugefuegt
  // 09.09.2021, LFR:
  // https://redmine.stiebel-eltron.com/redmine/issues/24042#note-11
  var stepcheckFactor = 1;
  for(i = 0; 1 > stepcheck; i++)
  {
    stepcheckFactor *= 10;
    stepcheck *= 10;
  }
  // console.log("stepcheckFactor: " +stepcheckFactor);
  // console.log("stepcheck: " +stepcheck);
  // LFR
  
  if( stepcheck > 1 ){                        // OTTO hinzugefuegt
    var floatstep = parseFloat(step);
	console.log("change floatstep ist" +floatstep);
    
    // 09.09.2021, LFR:
    integerValue = _round(val * stepcheckFactor, datatype);
    integerStep = _round(step * stepcheckFactor, datatype);
    // console.log("integerValue: " +integerValue);
    // console.log("integerStep: " +integerStep);
    // LFR
    
    // if( val%floatstep ){
    // 09.09.2021, LFR:
    if( integerValue % integerStep ) {
    // LFR
      console.log("integerValue % integerStep: " +integerValue % integerStep); // LFR
      // console.log("val%floatstep: " +val%floatstep); // LFR
      var solldiff;
      if (what=="+") {
            // console.log("val: " +val); // LFR
            solldiff = ( val % floatstep );
            // console.log("solldiff: " +solldiff); // LFR
        val -= solldiff;
        // console.log("val - solldiff: " +val); // LFR
      } else if (what=="-") {
        // console.log("val: " +val); // LFR
      	solldiff = floatstep - ( val % floatstep );
        // console.log("solldiff: " +solldiff); // LFR
        val += solldiff;
        // console.log("val + solldiff: " +val); // LFR
     	}
    }
  }
  // OTTO ende
  
	val = _round(val, datatype);
	if (val > max) val = max;
	if (val < min) val = min;
  
  // historischer Code, nkopplungid['min'] => 'MAXIMALTEMPERATUR' kommt nirgends mehr vor
  /*
  // namenskopplung // OTTO
  if( typeof nkopplungid != "undefined" ){
  if( 'val'+nkopplungid['min'] == id ){
    var nkid = 'val'+nkopplungid['max'];
    var nkmaxval = getValue( nkid, '');
    if( nkmaxval > val ){
      setValue( nkid, val.toFixed(i), geh );
    }
  }else if( 'val'+nkopplungid['max'] == id ){
    var nkid = 'val'+nkopplungid['min'];
    var nkmaxval = getValue( nkid, '');
    if( nkmaxval < val ){
      setValue( nkid, val.toFixed(i), geh );
    }
  }}
  */

/* OTTO Rausgenommen
  setValue(id, val);
*/ 
	setValue(id, val.toFixed(i), geh);         // OTTO hinzugefuegt
  if(!geh){                                  // OTTO hinzugefuegt
	  validate(id,datatype,min,max);
  }else{
    $('#cal'+id).removeClass("fehler");
  }
  
  document.onmouseup = function(){geh = false;clearTimeout(change.to)} //OTTO hinzugefuegt
  if(geh) change.to = setTimeout(function(){change(id, what, min, max, step, geh);},250); //OTTO hinzugefuegt
  console.log("change der neue Wert" + val);
}

var saveChangeRunning = false;

function saveChange(form,id,otto)
{
	//alert(form[0].value); // for debugging
	
	
	if (saveChangeRunning)
		return;

	saveChangeRunning = true;
		
	var params = "?msg=";
	var page = "./confirm.php";
	var error = false;
	var dataString = '';

	//Bei Fehlern können wir nicht abspeichern
	for (bid in errorBrain) {
		//Noch ein Fehler gespeichert?
		if (errorBrain[bid]==1)
		{
			if (!error) params += "Ungültige Angaben können nicht gespeichert werden, bitte angezeigte Fehler korrigieren!";
			error = true;
		}
	}
	//Fortsetzen?
	if (!error)
	{
		var success = false;
		var warning = false;
		if (id=='')
		{
			//Array speichern
			if(otto)
				var data = $("#welcome_form").serializeArray();
			else
				var data = $("#werte").serializeArray();
			dataString = JSON.stringify(data);
				
		}
		else
		{
			//Einzelnen Wert speichern
			var val = getValue(id,'');
			if (val)
			{
				var output = eval("document.getElementById(id+'info')");
				if (output)
				{
					output.value = val;
					dataString = '[{"name":"'+id+'","value":"'+val+'"}]';
				}
			}
			hide(id);
		}
		if (dataString!='')
		{
			if(otto)
				var seite = "./ersteinst.php";
			else
				var seite = "./save.php";

			 //console.log(dataString);				// for debugging

			$.post(seite, {data: dataString}, function(answer)
			{
			//alert(answer); // for debugging
			//console.log(answer);
				
				var results = JSON.parse(answer);
				
				//Erfolg?
				if (results['success']==true)
					success = true;
				else if (results['warning']==true)
				{
					success = true;
					warning = true;
				}
				else
				{
					//Fehler übergeben?
					if (results['errors'])
					{
						var errors = results['errors'];
						for (webID in errors)
						{
							var errormsg = errors[webID];
							//Fehler bei Feld webID!
							var $cal = $("#calval"+webID);
							$cal.addClass("fehler");
	    					errorBrain['val'+webID] = 1;
	    					//Fehlermeldung ausgeben => muss später der Infotext wiederhergestellt werden?
							$cal.children("div.green").children("p").html(errormsg);
						}
					}
				}
				if (results['message']!=undefined && results['message']!="")
					params += escape(results['message']);
				if (otto && results['url']!="" && results['url']!=undefined)
					params += "&amp;"+"url="+results['url'];    // OTTO
	
				//Was passiert nun?
				if (!success)
					page = "./error.php";
				else
					if (warning)
						page = "./warning.php";
				params += "&amp;KeepThis=true&amp;TB_iframe=true&amp;height=140&amp;width=420";
				//Meldung
				
				tb_show('',page+params);
				if (!otto)
					form.target=$('#TB_iframeContent').attr('name');
			  	
			  	//Alle Änderungen sind gesichert
				if (success)
					valueChanged = false;
					
				saveChangeRunning = false;
			}, 'text');
		} else
		{
			error = true;
			params += "Es wurde kein zu sichernder Wert gefunden!";
		}
	}
	if (error)
	{
		var errorShown = false;
	  	//Dashboard? Meldung anzeigen!
	 	var $containerDiv = $("#"+id+"edit");
		if ($containerDiv)
		{
		 	var msgDiv = $containerDiv.children("div.dashboardmsg");
			if (msgDiv)
			{
				msgDiv.css("display","block");
				errorShown = true;
				setTimeout(function(){msgDiv.css("display","none")},6000);
			}
		}
		//Nicht doppelt anzeigen
		if (errorShown)
		{
			page = "./error.php";
			params += "&amp;KeepThis=true&amp;TB_iframe=true&amp;height=140&amp;width=420";
			//Meldung
			tb_show('',page+params);
		  	form.target=$('#TB_iframeContent').attr('name');
		}
		saveChangeRunning = false;
	}
	else
	{
	  	//Dashboard? Meldung ausblenden!
	 	var $containerDiv = $("#"+id+"edit");
		if ($containerDiv)
		{
		 	var msgDiv = $containerDiv.children("div.dashboardmsg");
			if (msgDiv)
				msgDiv.css("display","none");
		}
		closeAllBoxes();
	}
}

function _round(val, datatype) {
	var decimals = 0;
	if (datatype=="float") decimals = 1;
	else if (datatype=="double") decimals = 2;
	return Math.round(val * Math.pow(10,decimals))/Math.pow(10,decimals);
}
function getDatatype(step) {
	var datatype = "int";
	var test = ''+step;
	if (test.indexOf(".") > 0) {
		var tmp = test.substr(test.indexOf(".")+1);
		var decimals = tmp.length;

		if (decimals == 1) datatype = "float";
		else if (decimals == 2) datatype = "double";
	}
	return datatype;
}

function show(id) {
	var $elem = $("#"+id+"edit");
	if ($elem) {
	}
}
function hide(id) {
	var $elem = $("#"+id+"edit");
	if ($elem) {
		$elem.children("div.black").fadeOut("fast");
	}
}

function reset($me) {
 	//ausblenden
	$me.children("div.black").fadeOut("fast");

	//zurücksetzen
	var parentid = $me.attr("id");
	if (parentid) {
		var index = (parentid+'').indexOf('edit');
		if (index > 0) {
			var name = parentid.substring(0,index);
			var $info = $("#"+name+"info");
			var $edit = $("#"+name);
			if ($info && $edit) $edit.attr("value",$info.attr("value"));
		}
	}
}

function checkChanges(f) {
	var params = "KeepThis=true&amp;TB_iframe=true&amp;height=160&amp;width=420";
	if (valueChanged && f!="") {
		var page = "./warning.php?";
		var msg = "msg="+"txt_HTML_INFOTEXT21"+"&amp;";
    //encodeURI("Die geänderten Einstellungen wurden noch nicht gespeichert. Beim Klick auf &bdquo;OK&ldquo; verlassen Sie diese Seite, ohne dass die Änderungen wirksam werden.")+"&amp;";
		var url = "url="+f+"&amp;";
	
		//Meldung
		tb_show('',page+msg+url+params);
		return false;
  	}

	return true;
}

function saveValues(f) 
{
	saveChange(f,'');
	return false;
}

function tabbing(id, type) {
	if (type=="radio") {
		var $radios = $("#"+id);
		//alert(($radios.size()));
	}
}

function setCookie(name, value) {
	var expiration = new Date();
	var sevenDays = expiration.getTime() + (7 * 24 * 60 * 60 * 1000);
	expiration.setTime(sevenDays);
	var curCookie = name + "=" + escape(value) + ";expires=" + escape(expiration.toGMTString()) + ";path=/;";
	document.cookie = curCookie;
}

function getCookie(name) {
	var dc = document.cookie;
	var prefix = name + "=";
	var begin = dc.indexOf("; " + prefix);
	if (begin == -1) {
		begin = dc.indexOf(prefix);
		if (begin != 0) return null;
	} else {
		begin += 2;
	}
	var end = document.cookie.indexOf(";", begin);
	if (end == -1) end = dc.length;
	return unescape(dc.substring(begin + prefix.length, end));
}

function clearField (thisfield, placeholder) {
	if (thisfield.value == placeholder) { thisfield.value = ''}
}

/* Dashboard */
$(document).ready(function(){
	$("#tabs a div").bind("click", function(){
	 	closeAllBoxes();

		var newtabid = $(this).attr("id");
		var newtabname = $(this).attr("name");
		var newtabindex = newtabid.substr(3);

	 	var $tabs = $(this).parent().parent().children("a").children("div");
	 	$tabs.each(function(index) {
 			var tabid = $(this).attr("id");
 			var tabindex = tabid.substr(3);
	 		if (newtabindex==tabindex) {
	 			$(this).attr("class","on");
	 		} else {
	 			$(this).attr("class","off");
	 		}
  		});
  
	 	var newclass = "dia"+newtabindex;
		var $container = $(this).parent().parent().parent().attr("class",newclass);
		showChart(newtabindex,newtabname);
	});
});
	
function showChart(id) {
	//tabula rasa
	$("#chart").html("");
  
	if (id==1) {
		plot1 = $.jqplot('chart', [charts[id]['max'], charts[id]['mittel'], charts[id]['min']], {
      legend: {show:true, location: 'ne',yoffset:-12},
      seriesDefaults:{fillToZero: true},
     	grid: {
             drawGridLines: true,        // wether to draw lines across the grid or not.
             gridLineColor: '#b9baba',    // *Color of the grid lines.
             background: '#fff',      // CSS color spec for background color of grid.
             borderColor: '',     // CSS color spec for border around grid.
             borderWidth: 0,           // pixel width of border around grid.
             shadow: false               // draw a shadow for grid.
         },
         series:[
             {label:temp_linien_beschreibung['MAX']}, 
             {label:temp_linien_beschreibung['MITTEL']},
             {label:temp_linien_beschreibung['MIN']}
         ],
         seriesColors: [ "#ecf3e1", marke_color1, "#8f9092" ],
     	axes:{xaxis:{renderer:$.jqplot.CategoryAxisRenderer, tickOptions:{showGridline:false}}, yaxis:{min:minValues[id], max:maxValues[id], numberTicks:nrTicks[id], tickOptions:{formatString:'%.0f'}}}
	  });
    $('table.jqplot-table-legend').css('z-index','1');
    $('table.jqplot-table-legend').draggable({containment : 'parent'});
	} else if (id==2) {
		plot2 = $.jqplot('chart', [charts[id]['line']], {
      seriesDefaults:{renderer:$.jqplot.BarRenderer, rendererOptions:{barPadding:10, barMargin:10, barWidth:18}, color:marke_color2, shadow : false},
      legend: {show:false, location: 'nw'},
        grid: {
          drawGridLines: true,        // wether to draw lines across the grid or not.
          gridLineColor: '#b9baba',    // *Color of the grid lines.
          background: '#fff',       // CSS color spec for background color of grid.
          borderColor: '',            // CSS color spec for border around grid.
          borderWidth: 0,           // pixel width of border around grid.
          shadow: false               // draw a shadow for grid.
        },
      axes:{xaxis:{renderer:$.jqplot.CategoryAxisRenderer, tickOptions:{showGridline:false}}, yaxis:{min:minValues[id], max:maxValues[id], numberTicks:nrTicks[id], tickOptions:{formatString:'%.0f'}}}
	  });
	} else if (id==3) {
		plot3 = $.jqplot('chart', [charts[id]['line']], {
      seriesDefaults:{renderer:$.jqplot.BarRenderer, rendererOptions:{barPadding:10, barMargin:10, barWidth:18}, color:marke_color2, shadow : false},
      legend: {show:false, location: 'nw'},
        grid: {
          drawGridLines: true,        // wether to draw lines across the grid or not.
          gridLineColor: '#b9baba',    // *Color of the grid lines.
          background: '#fff',      // CSS color spec for background color of grid.
          borderColor: '',     // CSS color spec for border around grid.
          borderWidth: 0,           // pixel width of border around grid.
          shadow: false               // draw a shadow for grid.
       },
       axes:{xaxis:{renderer:$.jqplot.CategoryAxisRenderer, tickOptions:{showGridline:false}}, yaxis:{min:minValues[id], max:maxValues[id], numberTicks:nrTicks[id], tickOptions:{formatString:'%.0f'}}}
		});
	} 
	else if (id==4) 
	{
		if (charts[id]!==undefined && charts[id]['xy'].length > 0)
		{
		  plot4 = $.jqplot('chart', [charts[id]['xy']], {
			seriesDefaults: {
			},
			grid: {
				drawGridLines: true, 
				gridLineColor: '#b9baba',
				background: '#fff',
				borderColor: '',
				borderWidth: 0,
				shadow: false 
			},
			axes: {
				xaxis: { 
					renderer:$.jqplot.DateAxisRenderer, 
					tickOptions: {
						formatString: em_hourformat,
						showGridline : true,
					},
					tickInterval: "3 hour",
					min: "06:00",
					max: "21:00"
				}, 
				yaxis: { 
					renderer:$.jqplot.CategoryAxisRenderer, 
          ticks: em_ticks,
					tickOptions: {
						showGridline : true
					},
				}
			},
			seriesColors: [marke_color2],
		  });
		}
	}
	else if (id==5) 
	{
		if (charts[id]!==undefined && charts[id]['line'].length > 0)
		{
  		 plot5 = $.jqplot('chart', [charts[id]['line']], {
		   seriesDefaults:{renderer:$.jqplot.BarRenderer, rendererOptions:{barPadding:10, barMargin:10, barWidth:18}, color:marke_color2, shadow : false},
          legend: {show:false, location: 'nw'},
		   grid: {
			  drawGridLines: true,    
			  gridLineColor: '#b9baba', 
			  background: '#fff', 
			  borderColor: '', 
			  borderWidth: 0, 
			  shadow: false 
		  },
		  axes:{
			  xaxis:{renderer:$.jqplot.CategoryAxisRenderer, tickOptions:{showGridline:false}}, 
			  yaxis:{min:0, tickOptions:{formatString:'%.0f'}}}
		 });
		}
	}
}
//  Funktion zum Runden X = Wert N = Stellen 

function  round(x, n)
{
  var a = Math.pow(10, n);
  return (Math.round(x / a) * a);
}

//__ OTTO __//

function tb_show_parms(width,height){
  if(!width) width=420;
  if(!height) height=140;
  return 'KeepThis=true&amp;TB_iframe=true&amp;height='+height+'&amp;width='+width;
}

$(document).ready(function(){
  $('#neustarten').click(function(){ tb_show('','reboot.php?val=hi&amp;'+tb_show_parms()) });
  
  // LFR/MKE
  
  // $('#ext_con_em_meter_btn_suchen').click(function(){ tb_show('','external_connections/meter/btn_search_em_meter.php?val=hi&amp;'+tb_show_parms()) });
  // $('#ext_con_em_meter_btn_verbinden').click(function(){ tb_show('','external_connections/meter/btn_connect_em_meter.php?val=hi&amp;'+tb_show_parms()) });
  // $('#ext_con_em_meter_btn_pruefen').click(function(){ tb_show('','external_connections/meter/btn_check_em_meter.php?val=hi&amp;'+tb_show_parms()) });
  // $('#ext_con_em_meter_btn_blockieren').click(function(){ tb_show('','external_connections/meter/btn_lock_em_meter.php?val=hi&amp;'+tb_show_parms()) });
  // $('#ext_con_em_meter_btn_deaktivieren').click(function(){ tb_show('','external_connections/meter/btn_lock_em_meter.php?val=hi&amp;'+tb_show_parms()) });
  // $('#ext_con_em_meter_btn_freischalten').click(function(){ tb_show('','external_connections/meter/btn_unlock_em_meter.php?val=hi&amp;'+tb_show_parms()) });
  // $('#ext_con_em_meter_btn_aktivieren').click(function(){ tb_show('','external_connections/meter/btn_unlock_em_meter.php?val=hi&amp;'+tb_show_parms()) });
  // $('#ext_con_em_meter_btn_trennen').click(function(){ tb_show('','external_connections/meter/btn_disconnect_em_meter.php?val=hi&amp;'+tb_show_parms()) });
  // $('#ext_con_em_meter_btn_loeschen').click(function(){ tb_show('','external_connections/meter/btn_disconnect_em_meter.php?val=hi&amp;'+tb_show_parms()) });
  
  $('#ext_con_thermia_btn_suchen').click(function(){ tb_show('','ext_con_thermia_btn_search.php?val=hi&amp;'+tb_show_parms()) });
  $('#ext_con_thermia_btn_verbinden').click(function(){ tb_show('','ext_con_thermia_btn_connect.php?val=hi&amp;'+tb_show_parms()) });
  $('#ext_con_thermia_btn_loeschen').click(function(){ tb_show('','ext_con_thermia_btn_delete.php?val=hi&amp;'+tb_show_parms()) });
  
  // LFR/MKE
});

function set_portal_con() { 
  tb_remove();
  setTimeout(function(){
    tb_show('','./create_portal_connection.php?'+tb_show_parms(691,500)+'&amp;tb_top_id=TB_title_create_connection_top&amp;tb_bottom_id=TB_title_create_connection_bottom');
  },300);
}

function cre_port_con(e){
  tb_remove();
  var seite='./save_portal_connection.php';
  setTimeout(function(){
    $.post(seite, {data: e}, function(results) {
      if(results['status']) tb_show('','./confirm.php?msg='+results['msg']+'&amp;url=.&amp;'+tb_show_parms());
      else                  tb_show('','./error.php?msg='+results['msg']+'&amp;'+tb_show_parms());
    })
  },300);
}

function set_potalpw(pw) { // OTTO
  tb_remove();
  var params = "?msg="+pw;
	var page = "./input.php";
	params += "&amp;"+tb_show_parms();
	//Meldung
  setTimeout(function(){tb_show('',page+params);},300);
}

function htmlreplace( id ){
  $.post( 'htmlreplace.php', { "id" : id }, function( answer ){
    $( '#'+id ).html( answer );
  }, 'text' );
}

// presentation7 -- START -->

var inputoldval = Array();
var pre7defaultval = 36864;

function pre7on( id, prio ){
  if( $('#chval'+id).css( 'display' ) != 'block' || prio === true ){
    $("#aval" + id).val( $( "#radioval" + id + "1" ).attr( "alt" ) );
    $( "#radioval" + id + "0" ).attr( "checked", false );
    $('#chval' + id ).css( 'display', 'block' );
    $('#calval' + id ).css( 'height', '140px' ).children( '.green' ).css( 'height', '140px' );
    $('#valueunit' + id ).css( 'display', 'block' );
    //$('#radioval'+id+'off').next().css("background-image", function(){ return $(this).css("background-image").replace(/on\./, "off.") } );
    //$('#radioval'+id+'on').next().css("background-image", function(){ return $(this).css("background-image").replace(/off\./, "on.") } );
    if( !inputoldval[id] ){
      $('#val'+id).val( valSettings['val'+id]['min'] );
    }else{
      $('#val'+id).val( inputoldval[id] );
    }
  }
}
function pre7off( id, prio ){
  if( $('#chval'+id).css( 'display' ) != 'none' || prio === true  ){
    $("#aval" + id).val( $( "#radioval" + id + "0" ).attr( "alt" ) );
    $( "#radioval" + id + "1" ).attr( "checked", false );
    $('#chval'+id).css( 'display', 'none' );
    $('#valueunit'+id).css( 'display', 'none' );
    $('#calval'+id).css( 'height', '72px' ).children( '.green' ).css( 'height', '72px' );
    //$('#radioval'+id+'off').next().css("background-image", function(){ return $(this).css("background-image").replace(/off\./, "on.") } );
    //$('#radioval'+id+'on').next().css("background-image", function(){ return $(this).css("background-image").replace(/on\./, "off.") } );
    inputoldval[id] = $('#val'+id).val();
    $('#val'+id).val( pre7defaultval );
  }
}

// <-- END -- presentation7

function save(werte)
{
	var element = document.getElementById("save");

	element.onclick ="document.forms['werte'].onsubmit()";

}

/*******************************************************************************
 * JavaScript-Handling fuer  Frondend-Funktionalitaet. 
 * Betrifft Seiten bei welchen die entsprechenden Daten von Javascript geladen 
 * und in die entsprechenden DOM-Elemente geschrieben werden.
 *
 * Author: P.Berendes (TRE-IU)
 * Changelog: 
 * 2024-02-08: Creation of Functions (EEBus)
 * 2024-04-04: Adding loader for Reboot Device (EEBus)
 * 2024-10-24: Erweiterung für Leistungssteuerungsmodul (WCCI) 
******************************************************************************/

var eebus_device_id = null;
var eebus_device_ip = null;
var eebus_device_ski = null;

/**
 * Diese Funktion sorgt dafür das bei den entsprechenden Seiten, bei denen die 
 * Daten durch Javascript geladen und gesetzt werden die notwendigen Funktionen
 * aufgerunfen werden.
 */
$( document ).ready(function() {
	refresh_timer_ms = 60000;
	if ($( "#eebus_op_state" ).length) {
		//console.log("EEBUS-Site OP-State Loaded");
		eeBUS_loadOPState();
		setInterval(function(){ 
			eeBUS_loadOPState();
		}, refresh_timer_ms);
	}
	if($( "#eebus_trusted_devices" ).length){
		closeAllBoxes();	
		//console.log("EEBUS-Site Trusted Loaded");
		//eeBUS_loadPreTrusts();
		eebus_load_trusts();
		setInterval(function(){ 
			//eeBUS_loadPreTrusts();
			eebus_load_trusts();
			eeBus_updateAAASelection();
		}, 5000);
	}

});

/**
 * Funktion die Dazu genutzt wird um eion Session Token aus dem DOM-Tree zu
 * extrahieren und dann in die Backend-Calls zu platzieren...
 */
function getSessionToken(){
	/**
	 * Lödt von der Webseite das Session-Token und gibt dieses als String zurück.
	 * Das Session-Token muss als Authentification bei Backend-Call mitgegeben 
	 * werden.
	 * Ist das Token nicht vorhanden wird ein leerer String zurück gegeben.
	 */
	if ($( "#sessionToken" ).length){
		return $( "#sessionToken" ).text();
	} else {
		return "";
	}
}

/**
 * Wenn man variable Labels hat, deren Ausprägung erst im Front-End bestimmt
 * werden kann, dann kann man aus entsprechenden DOM-Elementen mit dieser 
 * Funktion den Anzuzeigenen Text extrahieren.
 */
function getLangString(id){
	myDivObj = document.getElementById(id);
	if ( myDivObj ) { 
		return myDivObj.innerHTML; 
	}else{
		return "";
	}
}

/*******************************************************************************
 * Funktionen, welche für die EEBus Funktionalitäten genutzt werden müssen.
 * Betrifft vor allem die PageType 200 und 210. 
******************************************************************************/
function eeBUS_checkRebootRequired(){
  	/*****************************************************************************
   	* Prüfung ob ein Neustart des Gerätes notwendig ist
   	* MSG_DIV: EEBUS_REBOOTREQUIRED 
   	****************************************************************************/
	var seite = window.location.protocol + "//" + window.location.host + "/external_connections/eebus/ext_con_eebus_rebootRequired.php";
	seite = seite + "?sessionToken=" + getSessionToken();
	var promise =	$.ajax({
		url: seite,
		dataType: 'json',
		timeout: 5000,
		success: function( data ) {
			if ( data['rebootRequired'] == true ){
				$('#EEBUS_REBOOTREQUIRED').show();
			}else{
				$('#EEBUS_REBOOTREQUIRED').hide();
			}
		},
		error: function( data ) {
			$('#EEBUS_REBOOTREQUIRED').hide();
		}
	});
}

function eeBUS_loadOPState(){
	/**
	 * Lädt den updateState vom PHP-Backend herunter und füllt diese in die 
	 * entsprechenden Felder von pt32.php. 
	 */
	
	eeBUS_checkRebootRequired();

	var limitationActive = getLangString("NICHT_AKTIV_TEXT");
	var failsafeActive = getLangString("NICHT_AKTIV_TEXT");
	var limitValue = ""; 
	var limitMinutes = "";  

	var seite = window.location.protocol + "//" + window.location.host + "/external_connections/eebus/ext_con_eebus_operatingState.php";
	seite = seite + "?sessionToken=" + getSessionToken();
	
  	var promise =	$.ajax({
    	url: seite,
    	dataType: 'json',
		timeout: 5000,
    	success: function( data ) {
			if (data['limitActive'] == true){
				limitationActive = getLangString("AKTIV_TEXT");
				limitMinutes = data['limitMinutes'] ;
				limitValue =   data['limitValue'] ;
			}
			if (data['failsafeActive'] == true){ 
			  failsafeActive = getLangString("AKTIV_TEXT");
			  limitationActive = getLangString("AKTIV_TEXT");
			  limitMinutes = data['failsafeMinutes'] ;
			  limitValue =   data['failsafeValue'] ;
			}
			console.log(data)
			$('#eebus_info_state').html(data['state']);
			$('#eebus_info_lpcmode').html(data['lpcMode']);
			$('#eebus_info_ownski').html(data['ownSki']);
			$('#eebus_info_limitationactive').html(limitationActive);
			$('#eebus_info_limitationminutes').html(limitMinutes);
			$('#eebus_info_limitationvalue').html(limitValue);
			$('#eebus_info_failsafeactive').html(failsafeActive);
			$('#EEBUS_OPERATING_MSG').hide();
    	},
    	error: function( data ) {
			$('#EEBUS_OPERATING_MSG').show();
			$('#eebus_info_state').html(getLangString("txt_ERROR"));
			$('#eebus_info_lpcmode').html(getLangString("txt_ERROR"));
			$('#eebus_info_ownski').html(getLangString("txt_ERROR"));
			$('#eebus_info_limitationactive').html(getLangString("txt_ERROR"));
			$('#eebus_info_limitationminutes').html(getLangString("txt_ERROR"));
			$('#eebus_info_limitationvalue').html(getLangString("txt_ERROR"));
			$('#eebus_info_failsafeactive').html(getLangString("txt_ERROR"));
    	}
  	});
}

function eeBUS_deleteTrustedSki(id, type){
	//console.log("eeBUS_deleteTrustedSki: Must delete ID: "+ id);
	if (type == 0){
		var seite = window.location.protocol + "//" + window.location.host + "/external_connections/eebus/ext_con_eebus_trusts.php";
	}else{
		var seite = window.location.protocol + "//" + window.location.host + "/external_connections/eebus/ext_con_eebus_trustedDevices.php";
	}
	console.log(seite);
	
	var sendData = {};
	sendData['id'] = id;
	sendData['sessionToken'] = getSessionToken();
	$.ajax({
    url: seite,
    type: 'DELETE',
		contentType: "application/json",
		dataType: 'json',
		data: JSON.stringify(sendData),
		timeout: 5000,
    success: function(result) {
			$('#EEBUS_OPERATING_MSG').hide();
			eebus_load_trusts();
		},
		error: function( data ){
			$('#EEBUS_OPERATING_MSG').show();
			eebus_load_trusts();
		}
	});
}

function eebus_load_trusts(){
	/**
	 * Lädt die in der Anwendung hinterlegten Vertrauensstellungen (manuell und 
	 * Benutzerauthentifizierung) und präsentiert diese in einer einzelnen Liste...
	*/
	console.log("Load trusts");
	list_of_trusts = [];
	// Laden der Daten (manuell)
	var seite = window.location.protocol + "//" + window.location.host + "/external_connections/eebus/ext_con_eebus_trusts.php";
	seite = seite + "?sessionToken=" + getSessionToken();
	
	// https://stackoverflow.com/questions/5976142/variable-scope-question-in-my-jquery
	$.ajax({
		async: false,
		cache: false,
    url: seite,
    type: 'GET',
		contentType: "application/json",
		dataType: 'json',
		timeout: 5000,
    success: function(data) {
			//console.log(JSON.stringify(data));
			//console.log("ext_con_eebus_trusts" + JSON.stringify(data[0]['ski']));
			data.forEach(trust => {
				tmp = {};
				tmp['id'] = trust['id'];
				tmp['ski'] = trust['ski'];
				tmp['description'] = trust['description'];
				tmp['type'] = 'manual';
				list_of_trusts.push(tmp);
			})
    },
		error: function( data ){
			$('#EEBUS_OPERATING_MSG').show();
			return;
		}
	});

	$('#EEBUS_OPERATING_MSG').hide();
	var tempDom = ""; // Temporäres DOM-Element um den Inhalt zusammenzubauen.
	var bgcolor = "even";  // Steuerung Zeilenhintergrund
	if (list_of_trusts.length > 0){
		list_of_trusts.forEach((value) => {
			
			tempDom += '<tr class="' + bgcolor + '">';
			tempDom +=   '<td class="key">' + value['ski'] + ' / ' + value['description'] + '</td>';
			tempDom +=   '<td id="eebus_trustedski_' + value['id'] + ' / ' + value['description'] + '">';
			if (value['type'] == 'manual'){
				tempDom +=     '<div class="button3 right" onClick="window.parent.eeBUS_deleteTrustedSki(`' + value['id'] + '`, 0);">';
			}else{
				tempDom +=     '<div class="button3 right" onClick="window.parent.eeBUS_deleteTrustedSki(`' + value['id'] + '`, 1);">';
			}
			tempDom +=       '<div class="but3_right right">';
			tempDom +=       '</div>';
			tempDom +=       '<div class="but3_middle">DEL';
			tempDom +=       '</div>';
			tempDom +=     '</div>';
			tempDom +=   '</td>';
			tempDom += '</tr>';
			// Alterniere Spaltenhintergrundfarbe
			if (bgcolor == "even"){
				bgcolor = "odd";
			}else{
				bgcolor = "even";
			}
		});
	}else{
		tempDom += '<tr class="even">';
		tempDom +=   '<td class="key">' + getLangString("NO_DEVICE") + '</td>';
		tempDom += '</tr>';

	}
	$('#eebus_table_body_trusted_skis').html(tempDom);
	$('#EEBUS_OPERATING_MSG').hide();
	
}

function eeBUS_savePreTrust(){

	/* Backend-Caller für EEBus um neuen PreTrust hinzuzufügen...*/
	/* Liest die beiden DOM Elemente eebus_txt_ski und eebus_txt_description aus 
		und fügt diese Elemente dann in die Datenbank ein...*/
	tb_remove();
	var inputError = false;
	var skiToAdd = $( "#eebus_txt_ski" ).val();
	var descriptionToAdd = $( "#eebus_txt_description" ).val();
	var seite='/external_connections/eebus/ext_con_eebus_trusts.php';

	//23B2CFF91883EA84FAD1EAE78B6D6E05209C232B

	if (skiToAdd.length != 40) {
		$( '#EEBUS_INVALID_INPUT' ).show();
		//console.log("eeBUS_savePreTrust: Input Validation Error -> SKI: " + $( "#eebus_txt_ski" ).length);	
		inputError = true;
		return;
	}

	if (descriptionToAdd.length > 128) {
		//console.log("eeBUS_savePreTrust: Input Validation Error -> Description");
		$( '#EEBUS_INVALID_INPUT' ).show();
		inputError = true;
		return;
	}
	
	if (!inputError){
		$( '#EEBUS_INVALID_INPUT' ).hide();
	}

	var sendData = {ski: skiToAdd, description: descriptionToAdd, sessionToken: getSessionToken()};
	$.ajax({
    url: seite,
    type: 'POST',
		//contentType: "application/json",
		dataType: 'html',
		data: sendData,
		timeout: 5000,
    success: function(result) {
			//console.log("eeBUS_addTrustedSki: Send DELETE: " + sendData);
			$('#EEBUS_OPERATING_MSG').hide();
			$( "#eebus_txt_ski" ).val("");
			$( "#eebus_txt_description" ).val("");
			eebus_load_trusts();
			
    },
		error: function( data ){
			$('#EEBUS_OPERATING_MSG').show();
			eebus_load_trusts();
			//console.log("Add Trust error: " + sendData);
		}
	});
}  

function eeBus_updateAAASelection(){
	/* Lädt den aktuellen Zustand ob AAA und aktualisiert die Anzeige*/
	var seite = window.location.protocol + "//" + window.location.host + "/external_connections/eebus/ext_con_eebus_autoAcceptAuthentification.php";
	seite = seite + "?sessionToken=" + getSessionToken();
	
	// https://stackoverflow.com/questions/5976142/variable-scope-question-in-my-jquery
	$.ajax({
		async: false,
		cache: false,
    url: seite,
    type: 'GET',
		contentType: "application/json",
		dataType: 'json',
		timeout: 5000,
    success: function(data) {
			console.log(data["enabled"]);
			//console.log("ext_con_eebus_trusts" + JSON.stringify(data[0]['ski']));
			if(data["enabled"] === true) {
				$('#eeBus_aaa_state').attr('readonly', false);
				$('#eeBus_aaa_state').val(getLangString("txt_HTML_EIN_TEXT"));
				$('#eeBus_aaa_state').attr('readonly', true);
			}else{
				$('#eeBus_aaa_state').attr('readonly', false);
				$('#eeBus_aaa_state').val(getLangString("txt_HTML_AUS_TEXT"));
				$('#eeBus_aaa_state').attr('readonly', true);
			}
    },
		error: function( data ){
			$('#EEBUS_OPERATING_MSG').show();
			return;
		}
	});
}

// Auswahl wenn Dropdown Wert geklickt wurde...
function eeBUS_activateAAA(){
	var sendData = {sessionToken: getSessionToken()};
	var seite = window.location.protocol + "//" + window.location.host + "/external_connections/eebus/ext_con_eebus_autoAcceptAuthentification.php";
	$.ajax({
		async: false,
		cache: false,
    	url: seite,
    	type: 'POST',
		//contentType: "application/json",
		dataType: 'html',
		data: sendData,
		timeout: 5000,
	});
	eeBus_updateAAASelection();
	closeAllBoxes();
}

function eeBUS_deactivateAAA(){
	var sendData = {sessionToken: getSessionToken()};
	var seite = window.location.protocol + "//" + window.location.host + "/external_connections/eebus/ext_con_eebus_autoAcceptAuthentification.php";
	$.ajax({
		async: false,
		cache: false,
    url: seite,
    type: 'DELETE',
		//contentType: "application/json",
		dataType: 'html',
		data: sendData,
		timeout: 5000,
	});
	eeBus_updateAAASelection();
	closeAllBoxes();
}

function eeBUS_openLog(){
	var seite = window.location.protocol + "//" + window.location.host + "/external_connections/eebus/ext_con_eebus_getLog.php";
	seite = seite + "?sessionToken=" + getSessionToken();
	window.open(seite,'_blank');
}

