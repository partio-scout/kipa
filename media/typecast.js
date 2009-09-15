/*
Typecast 1.4 (release)
by Ara Pehlivanian (http://arapehlivanian.com)

This work is licensed under a Creative Commons Licence
http://creativecommons.org/licenses/by-nd/2.5/
*/

var Typecast = {
	InitMask : false,
	InitSuggest : false,
	
	Init : function(){
		this.Parse(document.body.getElementsByTagName("input"));
		this.Behaviours.Mask.Init();
		this.Behaviours.Suggest.Init();
	},
	
	Parse : function(nodes){
		
		for(var i=0; i<nodes.length; i++){
			var node = nodes[i];

			if(node.type=="text" && node.className && node.className.indexOf("TC") != -1){
				if(!node.id) Typecast.Utils.GenerateID(node);
				
				var behaviourName = (node.className.indexOf("[") != -1) ? node.className.substring(node.className.indexOf("TC")+2, node.className.indexOf("[")) : node.className.substring(node.className.indexOf("TC")+2, node.className.length);
				
				Typecast["Init" + behaviourName] = true;
				Typecast.Behaviours[behaviourName].InitField(node);

				node.onfocus = Typecast.Behaviours[behaviourName].Run;
				node.onkeyup = Typecast.Behaviours[behaviourName].KeyHandler;
				node.onkeydown = Typecast.Behaviours[behaviourName].KeyHandler;
				node.onblur = Typecast.Behaviours[behaviourName].Stop;
				node.onmouseup = Typecast.Behaviours[behaviourName].MouseUp;
			}
		}
	},
	
	Behaviours : {
		Mask : {
			Init : function(){
			},
			
			InitField : function(field){
				var fieldData = [];
				if(!eval("Typecast.Config.Data.Mask.Masks." + field.id)){
					fieldData = field.className.substring(field.className.indexOf("[")+1, field.className.indexOf("]"))
				}else{
					fieldData = eval("Typecast.Config.Data.Mask.Masks." + field.id);
				}
				Typecast.Behaviours.Mask.ParseFieldData(field, fieldData);
				field.value = field.DefaultText.join("");
			},
			
			Run : function(e){
				e = (!e) ? window.event : e;
			},
			
			Stop : function(){
			},
			
			KeyHandler : function(e){
				e = (!e) ? window.event : e;
				var mask = Typecast.Behaviours.Mask;
				
				mask.CursorManager.TabbedInSetPosition(this);
				
				//Backspace
				if(e.keyCode==8 && e.type=="keydown" && this.AllowInsert){
					var preBackspaceCursorPosition = Typecast.Behaviours.Mask.CursorManager.GetPosition(this)[0];
					mask.CursorManager.Move(this, -1);
					var postBackspaceCursorPosition = Typecast.Behaviours.Mask.CursorManager.GetPosition(this)[0];
					
					if(preBackspaceCursorPosition != postBackspaceCursorPosition) mask.DataManager.RemoveCharacterByShiftLeft(this);
					mask.Render(this);
				}
				
				//Tab
				if(e.keyCode==9 && e.type=="keydown"){
					return
				}
				
				//Enter
				else if(e.keyCode==13 && e.type=="keyup"){
					return
				}
				
				//Esc
				else if(e.keyCode==27 && e.type=="keyup"){
				}
				
				//End
				else if(e.keyCode==35 && e.type=="keydown"){
					var startIdx = Typecast.Behaviours.Mask.MaskManager.FindNearestMaskCharacter(this, this.DataIndex[this.DataIndex.length-1], 1);
					Typecast.Behaviours.Mask.CursorManager.SetPosition(this, startIdx);
				}

				//Home
				else if(e.keyCode==36 && e.type=="keydown"){
					Typecast.Behaviours.Mask.CursorManager.SetPosition(this, this.MaskIndex[0]);
				}
				
				//Left or Up
				else if(e.keyCode==37 && e.type=="keydown" || e.keyCode==38 && e.type=="keydown"){
					mask.CursorManager.Move(this, -1);
				}
				
				//Right or Down
				else if(e.keyCode==39 && e.type=="keydown" || e.keyCode==40 && e.type=="keydown"){
					mask.CursorManager.Move(this, 1);
				}
				
				//Insert
				else if(e.keyCode==45 && e.type=="keydown" && this.AllowInsert){
					mask.CursorManager.ToggleInsert(this);
				}
				
				//Delete
				else if(e.keyCode==46 && e.type=="keydown"){
					if(this.InsertActive){
						mask.DataManager.RemoveCharacterByShiftLeft(this);
					}else{
						mask.DataManager.RemoveCharacterByOverwrite(this);
					}
					mask.Render(this);
				}
				
				//Numeric Characters
				else if((mask.MaskManager.CurrentMaskCharacter(this) == Typecast.Config.Settings.Mask.MaskCharacters.Numeric) && (e.keyCode>=48 && e.keyCode<=57 && e.type=="keydown" || e.keyCode>=96 && e.keyCode<=105 && e.type=="keydown")){
					var keycode = parseInt(e.keyCode);
					keycode = (keycode>=96 && keycode<=105) ? keycode-48 : keycode;

					mask.DataManager.AddData(this, String.fromCharCode(keycode));
					mask.Render(this);
					mask.CursorManager.Move(this, 1);
				}
				
				//Alpha Characters 65 - 90
				else if((mask.MaskManager.CurrentMaskCharacter(this) == Typecast.Config.Settings.Mask.MaskCharacters.Alpha) && (e.keyCode>=65 && e.keyCode<=90 && e.type=="keydown")){
					mask.DataManager.AddData(this, String.fromCharCode(e.keyCode));
					mask.Render(this);
					mask.CursorManager.Move(this, 1);
				}
				
				//Refresh
				else if(e.keyCode==116 && e.type=="keydown"){
					return
				}
				
				else{
				}
				return false
			},
			
			MouseUp : function(e){
				e = (!e) ? window.event : e;
				var cursorPosition = Typecast.Behaviours.Mask.CursorManager.GetPosition(this)[0];
				var startIdx = Typecast.Behaviours.Mask.MaskManager.FindNearestMaskCharacter(this, cursorPosition, 0);
				Typecast.Behaviours.Mask.CursorManager.SetPosition(this, startIdx);
			},
			
			ParseFieldData : function(field, fieldData){
				fieldData = fieldData.split(Typecast.Config.Settings.Mask.FieldDataSeparator);
				field.Data = [];
				field.DataIndex = [];
				field.DefaultText = (fieldData[1]) ? fieldData[1].split("") : fieldData[0].split(""); //if default text isn't provided use mask
				field.Mask = this.MaskManager.ParseMask(fieldData[0]);
				field.MaskIndex = this.MaskManager.ParseMaskIndex(field.Mask);
				field.CursorPersistance = [];
				field.InsertActive = (this.MaskManager.IsComplexMask(field)) ? false : true;
				field.HighlightChar = (this.MaskManager.IsComplexMask(field)) ? true : false;
				field.AllowInsert = (this.MaskManager.IsComplexMask(field)) ? false : true;
			},
			
			MaskManager : {
				ParseMask : function(mask){
					var arr = [];
					var maskCharacters = Typecast.Config.Settings.Mask.MaskCharacters;
					for(var i=0; i<mask.length; i++){
						for(maskCharacter in maskCharacters){
							char = eval("maskCharacters." + maskCharacter);
							if(mask.substring(i, i+1) == char){
								arr[i] = char;
							}
						}
					}
					return arr
				},
				
				ParseMaskIndex : function(mask){
					var arr = [];
					for(var i=0; i<mask.length; i++){
						if(mask[i] != null) arr[arr.length] = i;
					}
					return arr;
				},
				
				CurrentMaskCharacter : function(field){
					var cursorPosition = Typecast.Behaviours.Mask.CursorManager.GetPosition(field)[0];
					return field.Mask[cursorPosition];
				},
				
				FindNearestMaskCharacter : function(field, cursorPosition, dir){
					var nearestMaskCharacter = (field.DataIndex.length > 0) ? cursorPosition : field.MaskIndex[0];
					
					switch(dir){
						case -1:
							for(var i=field.DataIndex.length-1; i>-1; i--){
								if(field.DataIndex[i] < cursorPosition){
									nearestMaskCharacter = field.DataIndex[i];
									break;
								}
							}
						break;
						case 0:
							for(var i=0; i<field.DataIndex.length; i++){
								if(field.MaskIndex[i] >= cursorPosition){
									nearestMaskCharacter = field.MaskIndex[i];
									break;
								}else{
									nearestMaskCharacter = field.MaskIndex[field.DataIndex.length];
								}
							}							
						break;
						case 1:
							for(var i=0; i<field.DataIndex.length; i++){
								if(field.DataIndex[i] > cursorPosition){
									nearestMaskCharacter = field.DataIndex[i];
									break;
								}
							}
							if(cursorPosition == field.MaskIndex[field.MaskIndex.length-1]) nearestMaskCharacter = cursorPosition + 1;
							else if(cursorPosition == field.DataIndex[field.DataIndex.length-1]) nearestMaskCharacter = field.MaskIndex[field.DataIndex.length];
						break;
					}
					return nearestMaskCharacter
				},
				
				IsComplexMask : function(field){//reports if mask contains mixed mask characters... can't perform "insert" if true
					var isComplex = false;
					var previousMaskChar = "";
					for(var i=0; i<field.MaskIndex.length; i++){
						var currentMaskChar = field.Mask[field.MaskIndex[i]];
						if(currentMaskChar != previousMaskChar && previousMaskChar != ""){
							isComplex = true;
						}
						previousMaskChar = currentMaskChar;
					}
					return isComplex
				}
			},
			
			CursorManager : {
				Move : function(field, dir){
					var cursorPosition = this.GetPosition(field)[0];
					var startIdx = Typecast.Behaviours.Mask.MaskManager.FindNearestMaskCharacter(field, cursorPosition, dir);
					this.SetPosition(field, startIdx);
				},
				GetPosition : function(field){
					var arr = [0,0];
					if(field.selectionStart && field.selectionEnd){
						arr[0] = field.selectionStart;
						arr[1] = field.selectionEnd;
					}
					else if(document.selection){
						var range = field.createTextRange();
						range.setEndPoint("EndToStart", document.selection.createRange());
						arr[0] = range.text.length;
						arr[1] = document.selection.createRange().text.length;
					}
					return arr
				},
				SetPosition : function(field, startIdx){
					var endIdx = startIdx + ((field.HighlightChar) ? 1 : 0);
					Typecast.Utils.PartialSelect(field, startIdx, endIdx);
				},
				TabbedInSetPosition : function(field){
					var mask = Typecast.Behaviours.Mask;
					
					if(mask.MaskManager.CurrentMaskCharacter(field) == undefined){
						var startIdx = null;
						if(field.DataIndex.length > 0 && field.DataIndex.length != field.MaskIndex.length){
							startIdx = field.MaskIndex[field.DataIndex.length];
						}
						else if(field.DataIndex.length == field.MaskIndex.length){
							startIdx = field.DataIndex[field.DataIndex.length-1] + 1;
						}
						else{
							startIdx = field.MaskIndex[0];
						}
						this.SetPosition(field, startIdx);
					}
				},
				PersistPosition : function(field){
					field.CursorPersistance = this.GetPosition(field);
				},
				RestorePosition : function(field){
					this.SetPosition(field, field.CursorPersistance[0]);
				},
				ToggleInsert : function(field){
					if(field.InsertActive){
						field.InsertActive = false;
						field.HighlightChar = true;
					}else{
						field.InsertActive = true;
						field.HighlightChar = false;
					}
					var startIdx = this.GetPosition(field)[0];
					this.SetPosition(field, startIdx);
				}
			},
			
			DataManager : {
				AddData : function(field, char){
					var cursorPosition = Typecast.Behaviours.Mask.CursorManager.GetPosition(field)[0];
					if(field.InsertActive){
						this.InsertCharacter(field, char);
					}else{
						this.OverwriteCharacter(field, char, cursorPosition);
					}
					this.UpdateDataIndex(field);
				},
				InsertCharacter : function(field, char){
					var lastCharacterPosition = field.MaskIndex[field.MaskIndex.length-1];
					var currentCharacterPosition = this.CurrentDataIndexPosition(field);
					for(var i=lastCharacterPosition; i>=currentCharacterPosition; i--){
						field.Data[field.MaskIndex[i+1]] = field.Data[field.MaskIndex[i]];
					}
					field.Data[field.MaskIndex[currentCharacterPosition]] = char;
				},
				OverwriteCharacter : function(field, char, cursorPosition){
					field.Data[cursorPosition] = char;
				},
				RemoveCharacterByOverwrite : function(field){
					var currentCharacterPosition = this.CurrentDataIndexPosition(field);
					if(currentCharacterPosition != null){
						field.Data[field.DataIndex[currentCharacterPosition]] = "";
					}
				},
				RemoveCharacterByShiftLeft : function(field){
					var lastCharacterPosition = field.DataIndex[field.DataIndex.length-1];
					var currentCharacterPosition = this.CurrentDataIndexPosition(field);
					var cursorPosition = Typecast.Behaviours.Mask.CursorManager.GetPosition(field)[0];
					
					if(currentCharacterPosition != null && lastCharacterPosition >= cursorPosition){
						for(var i=currentCharacterPosition; i<=lastCharacterPosition; i++){
							field.Data[field.DataIndex[i]] = field.Data[field.DataIndex[i+1]];
						}
						field.Data.length = field.Data.length-1;
						this.UpdateDataIndex(field);
					}
				},
				UpdateDataIndex : function(field){
					field.DataIndex.length = 0;
					for(var i=0; i<field.Data.length; i++){
						if(field.Data[i] != undefined) field.DataIndex[field.DataIndex.length] = i;
					}
				},
				CurrentDataIndexPosition : function(field){
					var cursorPosition = Typecast.Behaviours.Mask.CursorManager.GetPosition(field)[0];
					var currentDataIndexPosition = null;
					for(var i=0; i<field.MaskIndex.length; i++){
						if(field.MaskIndex[i] == cursorPosition){
							currentDataIndexPosition = i;
							break;
						}
					}
					return currentDataIndexPosition
				}				
			},
			
			Render : function(field){
				this.CursorManager.PersistPosition(field);
				var composite = [];
				for(var i=0; i<field.Mask.length; i++){
					composite[i] = field.Mask[i];
					if(field.DefaultText[i]) composite[i] = field.DefaultText[i];
					if(field.Data[i]) composite[i] = field.Data[i];
				}
				field.value = composite.join("")
				
				this.CursorManager.RestorePosition(field);
			}
		},
		
		Suggest : {
			FieldID : null,
			OutputAreaVisible : false,
			InputValueBackup : null,
			ResultSet : [],
			ResultSetIndex : -1,
			
			Init: function(){
				this.CreateOutputArea();
			},
			
			InitField : function(field){
			},
			
			Run : function(e){
				e = (!e) ? window.event : e;
				var suggest = Typecast.Behaviours.Suggest;
				this.autocomplete = (Typecast.Config.Settings.Suggest.BrowserAutoComplete) ? "on" : "off"; //Reference: http://web.archive.org/web/20031203134351/http://devedge.netscape.com/viewsource/2003/form-autocompletion/
				suggest.FieldID = this.id;
			},
			
			Stop : function(e){
				e = (!e) ? window.event : e;
				var suggest = Typecast.Behaviours.Suggest;
				
				suggest.HideOutputArea();
				suggest.InputValueBackup = null;
				suggest.ResultSet.length = 0;
				suggest.ClearOutputAreaContents();
			},
			
			KeyHandler : function(e){
				e = (!e) ? window.event : e;
				var suggest = Typecast.Behaviours.Suggest;
				
				//Tab
				if(e.keyCode==9 && e.type=="keyup"){
					return
				}
				
				//Enter
				else if(e.keyCode==13 && e.type=="keyup"){
					suggest.InputValueBackup = this.value;
					suggest.HideOutputArea();
					suggest.PartialSelect(this, this.value.length);
					return
				}
				
				//Shift
				else if(e.keyCode==16 && e.type=="keyup"){
					return false
				}
				
				//Esc
				else if(e.keyCode==27 && e.type=="keyup"){
					suggest.RevertInputValue(this);
					suggest.HideOutputArea();
					return
				}
				
				//Up
				else if(e.keyCode==38 && e.type=="keydown"){
					if(suggest.ResultSet.length==0 && this.value.length > 0){
						suggest.LookUp(this);
						suggest.Render(this);
						suggest.InputValueBackup = this.value;
					}
					suggest.MoveResultSetIndex(-1);
					suggest.SuggestInputValue(this);
					//return false
				}
				
				//Down
				else if(e.keyCode==40 && e.type=="keydown"){
					if(suggest.ResultSet.length==0 && this.value.length > 0){
						suggest.LookUp(this);
						suggest.Render(this);
						suggest.InputValueBackup = this.value;
					}
					suggest.MoveResultSetIndex(1);
					suggest.SuggestInputValue(this);
					//return false
				}
				
				//Everything else
				else if(e.type=="keyup" && e.keyCode!=37 && e.keyCode!=38 && e.keyCode!=39 && e.keyCode!=40){
					suggest.LookUp(this);
					suggest.Render(this);
					suggest.InputValueBackup = this.value;
					if(e.keyCode!=8){
						suggest.AutoComplete(this);
					}
				}
			},
			
			MouseUp : function(e){
				e = (!e) ? window.event : e;
				return
			},
			
			LookUp : function(field){
				field = (!field) ? document.getElementById(this.FieldID) : field;
				var dictionaries = Typecast.Config.Data.Suggest.Dictionaries;
				var dictionary = (eval("dictionaries." + field.id)) ? eval("dictionaries." + field.id) : dictionaries.Default;
				dictionary.sort();
				var query = Typecast.Utils.CaseSensitize(field.value);

				this.ResultSet.length = 0;
				
				for(var i=0; i<dictionary.length; i++){
					if(Typecast.Utils.FindIn(dictionary[i], query) > -1){
						this.ResultSet[this.ResultSet.length] = dictionary[i];
					}
				}
			},
			
			Render : function(field){
				field = (!field) ? document.getElementById(this.FieldID) : field;
				if (this.ResultSet.length == 0) {
					this.HideOutputArea();
					return
				}
				
				var outputArea = document.getElementById(Typecast.Config.Settings.Suggest.OutputAreaID);
				this.ClearOutputAreaContents();
				
				var ul = document.createElement("ul");
					ul.id = "Suggestions";

				for(var i=0; i<this.ResultSet.length && i<Typecast.Config.Settings.Suggest.ResultLimit; i++){
					var li = document.createElement("li");
					li.id = i;
					li.onmouseover = this.MouseOver;
					li.onmouseout = this.MouseOut;
					
					var result = this.BuildHighlightedResult(this.ResultSet[i], field.value);
					
					li.appendChild(result);
					ul.appendChild(li);
				}
				
				outputArea.appendChild(ul);
				this.ShowOutputArea(field);
			},
			
			SuggestInputValue : function(field){
				if(this.ResultSetIndex == -1) return
				field = (!field) ? document.getElementById(this.FieldID) : field;
				
				if(this.ResultSetIndex>=0){	//arrow
					field.value = this.ResultSet[this.ResultSetIndex];
				}else{ //typing
					field.value += this.ResultSet[this.ResultSetIndex].substring(field.value.length, this.ResultSet[this.ResultSetIndex].length);
				}
			},
			
			AutoComplete : function(field){
				if(!Typecast.Config.Settings.Suggest.MatchFromStart) return;
				field = (!field) ? document.getElementById(this.FieldID) : field;
				var startIdx = field.value.length;
				
				if(this.ResultSet.length > 0){
					field.value += this.ResultSet[0].substring(field.value.length, this.ResultSet[0].length);
					this.PartialSelect(field, startIdx);
				}
			},
			
			PartialSelect : function(field, startIdx){
				if(!Typecast.Config.Settings.Suggest.MatchFromStart) return;
				field = (!field) ? document.getElementById(this.FieldID) : field;

				Typecast.Utils.PartialSelect(field, startIdx, field.value.length);
			},
			
			RevertInputValue : function(field){
				field = (!field) ? document.getElementById(this.FieldID) : field;
				field.value = (field.value == this.InputValueBackup) ? "" : this.InputValueBackup;
			},
			
			MoveResultSetIndex : function(dir){
				if(!this.OutputAreaVisible) return;
				if(this.ResultSet.length == 0) return;
				if(this.ResultSetIndex == -1 && dir == -1) return //Lower Bound Test
				if(this.ResultSetIndex == this.ResultSet.length-1 && dir == 1) return //Upper Bound Test
				if(this.ResultSetIndex == Typecast.Config.Settings.Suggest.ResultLimit-1 && dir == 1) return //User Defined Upper Bound Test
				
				var outputArea = document.getElementById(Typecast.Config.Settings.Suggest.OutputAreaID);
				
				if(outputArea && this.ResultSetIndex != -1) outputArea.childNodes[0].childNodes[this.ResultSetIndex].className = "";
				
				this.ResultSetIndex += dir;
				
				if(outputArea && this.ResultSetIndex == -1) this.RevertInputValue();
				if(outputArea && this.ResultSetIndex != -1) outputArea.childNodes[0].childNodes[this.ResultSetIndex].className = "selected";
			},
			
			MouseOver : function(e){
				e = (!e) ? window.event : e;
				this.className = "selected";
				Typecast.Behaviours.Suggest.ResultSetIndex = parseInt(this.id);
				Typecast.Behaviours.Suggest.SuggestInputValue();
			},
			
			MouseOut : function(e){
				e = (!e) ? window.event : e;
				this.className = "";
			},
			
			CreateOutputArea : function(){
				var sid = Typecast.Config.Settings.Suggest.OutputAreaID;
				var outputAreaExists = (document.getElementById(sid)) ? true : false;
				
				if(!outputAreaExists){
					var outputArea = document.createElement("div");
					outputArea.id = sid;
				}else{
					var outputArea = document.getElementById(sid);
				}
				outputArea.style.display = "none";
				outputArea.style.position = "absolute";
				this.OutputAreaVisible = false;
				document.body.appendChild(outputArea);
			},
			
			ShowOutputArea : function(field){
				field = (!field) ? document.getElementById(this.FieldID) : field;
				if(this.OutputAreaVisible) return
				if(field.value == "") return
				
				var outputArea = document.getElementById(Typecast.Config.Settings.Suggest.OutputAreaID);
				var xy = Typecast.Utils.GetXY(field);
				
				if(outputArea){
					if(Typecast.Config.Settings.Suggest.IEForceRelative && document.all) outputArea.parentNode.style.position = "relative";
					outputArea.style.display = "block";
					outputArea.style.left = xy[0] + "px";
					outputArea.style.top = xy[1] + field.offsetHeight + "px";
					outputArea.style.width = field.offsetWidth + "px";
				}else{
					Typecast.Behaviours.Suggest.LookUp(this);
					Typecast.Behaviours.Suggest.Render(this);
				}
				this.OutputAreaVisible = true;
			},
			
			HideOutputArea : function(){
				if(!this.OutputAreaVisible) return
				this.ResultSetIndex = -1;
				document.getElementById(Typecast.Config.Settings.Suggest.OutputAreaID).style.display = "none";
				this.OutputAreaVisible = false;
			},
			
			ClearOutputAreaContents : function(){
				var sid = Typecast.Config.Settings.Suggest.OutputAreaID;
				var outputArea = document.getElementById(sid);
				
				if(outputArea && outputArea.childNodes.length > 0) outputArea.removeChild(outputArea.childNodes[0]);
			},
			
			BuildHighlightedResult : function(str, fragment){
				var csStr = Typecast.Utils.CaseSensitize(str);
				var csFragment = Typecast.Utils.CaseSensitize(fragment);
				var span = document.createElement("span");
				var lhs = document.createTextNode(str.substring(0, csStr.indexOf(csFragment)));
				var strong = document.createElement("strong");
				var highlight = document.createTextNode(str.substring(csStr.indexOf(csFragment), csStr.indexOf(csFragment) + csFragment.length));
				var rhs = document.createTextNode(str.substring(csStr.indexOf(csFragment) + csFragment.length, csStr.length));
				
				strong.appendChild(highlight);
				span.appendChild(lhs);
				span.appendChild(strong);
				span.appendChild(rhs);
				
				return span
			}
		}
	},
	
	Utils : {
		FindClass : function(findClass, parentClass){
			parentClass = (!parentClass) ? 'Typecast' : parentClass;
			for(var i in eval(parentClass)){
				if(i == findClass){
					return i;
				}else{
					var found = Typecast.Utils.FindClass(findClass, parentClass + "." + i);
					// if something was found send it back up the tree
					// if the parentClass contains no dots it's the rootClass and should also be tacked on and returned
					if(found) return (parentClass.indexOf(".") == -1) ? parentClass + "." + i + "." + found : i + "." + found;
				}
			}
		},
		
		GenerateID : function(obj){
			dt = new Date();
			obj.id = "GenID" + dt.getTime();
			return obj
		},
		
		FindIn : function(str, fragment){
			if(!fragment || fragment.length <= 0) return -1
			var csStrIdx = this.CaseSensitize(str).indexOf(fragment);
			var matchFromStart = Typecast.Config.Settings.Suggest.MatchFromStart;
			
			if(matchFromStart && csStrIdx==0 ) {return csStrIdx}
			else if(!matchFromStart && csStrIdx!=-1) {return csStrIdx}
			else {return -1}
		},
		
		CaseSensitize : function(str){
			var isCaseSensitive = Typecast.Config.Settings.Suggest.isCaseSensitive;
			return (isCaseSensitive) ? str : str.toLowerCase();
		},
		
		GetXY : function(obj){
			var x=0;
			var y=0;
			while(obj.offsetParent){
				x+=obj.offsetLeft;
				y+=obj.offsetTop;
				obj = obj.offsetParent;
			}
			return [x,y]
		},
		
		PartialSelect : function(field, startIdx, endIdx){
			if(field.createTextRange){
				var fld= field.createTextRange();
				fld.moveStart("character", startIdx);
				fld.moveEnd("character", endIdx - field.value.length);
				fld.select();
			}else if(field.setSelectionRange){
				field.setSelectionRange(startIdx, endIdx);
			}
		}		
	}
}