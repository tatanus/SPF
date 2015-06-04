
// Client sniffing
var isGecko	= (navigator.userAgent.indexOf("Gecko") != -1);
var isFirefox   = (navigator.userAgent.toLowerCase().indexOf("firefox") != -1);
var isNav	= (navigator.appName.indexOf("Netscape") != -1);
var isIE	= (navigator.appName.indexOf("Microsoft") != -1);
var isMac	= (navigator.appVersion.indexOf("Macintosh") >= 0);
var isUx	= (navigator.appVersion.indexOf("X11") >= 0);

var browserName = navigator.appName;

// Browser version
var gVersion = GetVersion();

//
//	Returns the URL to the custom stylesheet for the client
//
function GetCSS() 
{
	var sCSS = "ds";

	// Customize for Windows IE or Mac IE 5 and up
	if (isIE) {
		if ((!isMac) || (gVersion >= 5))
			sCSS += "/_ie.css";
		else
			sCSS += "/.css";
	}	
	// Customize for Mozilla
	// TODO: Should this change to isGecko?
	else if ((isNav) && (gVersion >= 5)) {
		sCSS += "/_nav.css";
	}
	else {
		sCSS += "/.css";
	}
	return (sCSS);
}


//
//	Includes the current stylesheet in the HTML
//
function WriteCSS() 
{
 	var sCSS = GetCSS();
       	if (sCSS.length > 0) document.write("<link rel=\"stylesheet\" href=\"/dana-na/css/" + sCSS + "\">");
}
// Add a CSS based on theme
function WriteThemeCSS(theme) 
{
	var sCSS = GetCSS();
	if ( (typeof(theme) != "undefined") && (theme != "")) {
		var str = "<link rel=\"stylesheet\" href=\"/dana-na/css/" + "../themes/" + theme + "/" + sCSS + "\">" ;
		if (sCSS.length > 0) document.write(str);
	}
	else {
		if (sCSS.length > 0) document.write("<link rel=\"stylesheet\" href=\"/dana-na/css/" + sCSS + "\">");
	}
}

function WriteVanillaCSS()
{	
	var path = "";
	var args = WriteVanillaCSS.arguments;
	var nNumArgs = args.length;
	if (nNumArgs > 0) {
		path = args[0];
	} 
	WriteCSS(null, false, path);
}

// Get the browser version.  Digs into appVersion for IE, since MS doesn't 
// understand what version numbers are for. Otherwise just parses the appVersion.
function GetVersion() {
	var s = navigator.appVersion;
	var n = s.indexOf("MSIE");
	var v = 0;

	// Grab the first number appearing after "MSIE"
	if (n != -1) {
		v = parseFloat(s.substr(n + 4));
	}
	else {
		v = parseFloat(s);
	}
	return v;
}

function GetGeckoVersion() {
	// Gecko version is YYYYMMDD format following GeckoProductToken.
	// See: http://www.mozilla.org/build/revised-user-agent-strings.html
	var s = navigator.userAgent;
	var nStart = s.indexOf("Gecko/");
	var nVersion = null;
	
	if (nStart != -1) {
		nStart += 6;
		s = s.substring(nStart, nStart+8);
		nVersion = parseInt(s);
	}
	return nVersion;
}



//
//	This function handles the situation when the user selects a separator in a drop down list.  It assumes
//	that a separator will never be the first item in the list.  If the item is a separator, the selectedIndex
//	is adjusted up by one, and the function returns true.  Otherwise it returns false.  It is up to the calling
//	function to check the return value and respond accordingly.
//
function HandleSeparator(cmb,nDefaultIndex) {
	var opt = cmb.options[cmb.selectedIndex];
	var bWeHandled = false;
	if (IsSeparator(cmb)) {
		if (nDefaultIndex == -1)
			cmb.selectedIndex--;
		else
			cmb.selectedIndex = nDefaultIndex;
			
		bWeHandled = true;
	}
	return bWeHandled;
}
function IsSeparator(cmb) {
	return (cmb.options[cmb.selectedIndex].text == "--");
}

//
// DOM-related functions
//
// Returns the first parentNode of element elm with the given tagName. Null if
// no parent has that tagName.
function GetContainingElementByTagName(elm, sContainerTagName) {
	var tagName;
	var elmID;

	elm = elm.parentNode;

	do {
		tagName = elm.tagName;
		tagName = tagName.toLowerCase();
		elmID = elm.id;
		if (tagName == sContainerTagName) {
			return elm;
		}
		else {
			elm = elm.parentNode;
		}
	} while ((elm != null) && (typeof(elm.tagName) != "undefined"));

	return null;

}


//
// Handles select/unselect all behavior for list checkboxes.
// Takes an array of the checkboxes.
//
function SelectAll(chkArray){
	var nNumChecked = 0;
	var nCount = GetNumSelectCheckboxes(chkArray);
	var n;
		
	if (nCount == 1) {
		// if one item, toggle it
		chkArray.checked = !(chkArray.checked);
	}
	else if (nCount > 1) {
		// if more than one item, go through the array and check any checkbox
		// that isn't checked
		for (n = 0; n < nCount; n++) {
			var chk = chkArray[n];
			if (!chk.checked) {
				chk.checked = true;
			}
			else {
				nNumChecked++;
			}
		}
	
		// if it turns out that all the checkboxes were already checked,
		// uncheck all the checkboxes
		if (nNumChecked == nCount) {
			for (n = 0; n < nCount; n++) {
				chkArray[n].checked = false;
			}
		}
	}
}

function UnselectAll(chkArray) {
	var nCount = GetNumSelectCheckboxes(chkArray);
	//alert(nCount);
	if (nCount == 1) {
		chkArray.checked = false;
	}
	else if (nCount > 1) {
		for (var n = 0; n < nCount; n++) {
			chkArray[n].checked = false;
		}
	}
}


function GetNumSelected(chkArray) {
	var nNumChecked = 0;
	var nCount = GetNumSelectCheckboxes(chkArray);

	if (nCount == 1) {
		if (chkArray.checked) {
			nNumChecked++;
		}
	}
	else if (nCount > 1) {
		// count the number of checked checkboxes
		for (var n = 0; n < nCount; n++) {
			if (chkArray[n].checked) {
				nNumChecked++;
			}
		}
	}
	return nNumChecked;
}

function GetNumSelectCheckboxes(chkArray) {
	var nCount = 0;
	// if the array isn't null
	if (chkArray && (typeof(chkArray) != "undefined")) {
		// if the array actually IS an array
		if (chkArray.length) {
			nCount = chkArray.length;
		}
		else {
			nCount = 1;
		}
	}
	return nCount;
}


//
// HTML EVENT FUNCTIONS
// The following code coordinates certain event handling functions.
// Specifically, it allows clients to register KeyDown event handlers and
// Click event handlers, so different features can hook into these user
// interactions.  It also defines a standardized event object for keyboard
// events and mouse events, helping to encapsulate some vexing browser
// differences.
//
// Note that pages MUST go through the registration functions...they should
// not simply hook their own event handler.  The whole point of this is to
// make it easier for clients to hook these events without stepping on other
// features ability to also do so.
//
// Finally, registered event handlers are called in the order they were
// registered, and if a handler explicitly returns false, then no other
// event handlers will be called.
//
var gOnloadHandlers = null;
var gKeyDownHandlers = null;
var gClickHandlers = null;

function ClearOnloadHandlers() {
	gOnloadHandlers = null;
}
function AddOnloadHandler(cbk) {
	if (gOnloadHandlers == null) {
		gOnloadHandlers = new Array();
	}
	var nNumHandlers = gOnloadHandlers.length;
	gOnloadHandlers[nNumHandlers] = cbk;
}


function GDocumentOnKeyDown(evt) {
	var bStopProcessing = false;
	var rv = true;
	
	// If there are keydown handlers and we have a valid event
	if (gKeyDownHandlers != null) {
        var e = new StdKeyEvent(evt);
		
		if ((e != null) &&
			(e.keyCode != 16) && // Don't report keydown for shift modifier key
			(e.keyCode != 17) && // Don't report keydown for ctrl modifier key
			(e.keyCode != 18)) { // Don't report keydown for alt modifier key
	
			var f;
			var nNumHandlers = gKeyDownHandlers.length;

			// Call all registered handlers
			for (var n=0; ((n < nNumHandlers) && !bStopProcessing); n++) {
				f = gKeyDownHandlers[n];
				rv = f(e);
				if ((typeof rv == "boolean") && (rv == false)) {
					bStopProcessing = true;
				}				
			}
		}
	}
	return rv;
}


function ClearKeyDownHandlers() {
	gKeyDownHandlers = null;
}
function AddKeyDownHandler(cbk) {
	if (gKeyDownHandlers == null) {
		gKeyDownHandlers = new Array();
	}
	var nNumHandlers = gKeyDownHandlers.length;
	gKeyDownHandlers[nNumHandlers] = cbk;
}

// Calls registered event handlers in the order they were registered,
// until encountering one that explicitly returns false, at which point
// it considers the event handled and returns false.  If no handler
// returns false, it returns the last return value.
function GDocumentOnClick(evt) {
	var bStopProcessing = false;
	var rv = true;
	
	//alert("GDocumentOnClick()");
	// If there are click handlers and we have a valid event
	if (gClickHandlers != null) {
        var e = new StdMouseEvent(evt);
		//alert(gClickHandlers.length + " click handlers");
		
		if (e != null) {
			var f;
			var nNumHandlers = gClickHandlers.length;

			// Call registered event handlers in the order they were registered, 
			for (var n=0; ((n < nNumHandlers) && !bStopProcessing); n++) {
				f = gClickHandlers[n];
				rv = f(e);
				if ((typeof rv == "boolean") && (rv == false)) {
					bStopProcessing = true;
				}				
			}
		}
	}
	return rv;
}

// Added 2004/2/11 to make it easier for clients to cancel events. Primarily useful for
// click events. Ordinarily could just return false to cancel a default action, such as
// navigating when clicking on a hyperlink, but now we have a global Click handler, which
// throws a wrench in the simple method.  Thus, we need an explicit way to cancel an event,
// and here it is.
function CancelEvent(evt) {
	// for IE
	if (typeof evt.cancelBubble != "undefined") {
		evt.cancelBubble = true;
		evt.returnValue = false;
	}
	// for W3C/Mozilla
	else if (typeof evt.stopPropagation != "undefined") {
		evt.stopPropagation();
	}
	// so handlers can just return our return value.
	return false;
}

function ClearClickHandlers() {
	gClickHandlers = null;
}
function AddClickHandler(cbk) {
	if (gClickHandlers == null) {
		gClickHandlers = new Array();
	}
	var nNumHandlers = gClickHandlers.length;
	gClickHandlers[nNumHandlers] = cbk;
}




/*
	Some wrappers to hide browser differences for event objects
*/

function StdKeyEvent(e) {

	if (e) {
		this.event = e;
	}
	else if (window.event) { 
		this.event = window.event; 
		e = this.event;
	}
	else {
		return null;
	}

	if (e.srcElement && e.keyCode) {
		this.target = e.srcElement;
		this.keyCode = e.keyCode;
	}
	else if (e.target && e.which) {
		this.target = e.target;
		this.keyCode = e.which;
	}
	else {
		return null;
	}

	if (typeof e.shiftKey != "undefined") {
		this.altKey = e.altKey;
		this.ctrlKey = e.ctrlKey;
		this.shiftKey = e.shiftKey;
	}
	else if (typeof e.modifiers != "undefined") {
		this.altKey = e.modifiers & Event.ALT_MASK;
		this.ctrlKey = e.modifiers & Event.CONTROL_MASK;
		this.shiftKey = e.modifiers & Event.SHIFT_MASK;
	}
	else {
		return null;
	}
/*
	if (typeof e.cancelBubble != "undefined") {
		this.stopPropagation = new Function("this.event.cancelBubble = true;");
	}
	else if (typeof e.stopPropagation != "undefined") {
		this.stopPropagation = new Function("this.event.stopPropagation();");
	}
	else {
		this.stopPropagation = null;
	}*/
}

function StdMouseEvent(e) {

	if (e) {
		this.event = e;
	}
	else if (window.event) { 
		this.event = window.event; 
		e = this.event;
	}
	else {
		return null;
	}

	if (e.srcElement) {
		this.target = e.srcElement;
	}
	else if (e.target) {
		this.target = e.target;
	}
	else {
		return null;
	}

	if (!e.pageX) {
		e.pageX = e.clientX + document.body.scrollLeft;
		e.pageY = e.clientY + document.body.scrollTop;
	}

/*	if (typeof e.cancelBubble != "undefined") {
		this.stopPropagation = new Function("this.event.cancelBubble = true;");
	}
	else if (typeof e.stopPropagation != "undefined") {
		this.stopPropagation = new Function("this.event.stopPropagation();");
	}
	else {
		this.stopPropagation = null;
	}

	if (typeof e.shiftKey != "undefined") {     Dbg("ie");
		this.altKey = e.altKey;
		this.ctrlKey = e.ctrlKey;
		this.shiftKey = e.shiftKey;
	}
	else if (typeof e.modifiers != "undefined") {   Dbg("nn");
		this.altKey = e.modifiers & Event.ALT_MASK;
		this.ctrlKey = e.modifiers & Event.CONTROL_MASK;
		this.shiftKey = e.modifiers & Event.SHIFT_MASK;
	}
	else {  Dbg("unknown");
		return null;
	}*/
}


function Dbg(s) {
 //   alert(s);
}

function DbgObject(o) {
	var n = 0;
	var s = o.toString();
	for (p in o) {
		s += p + " = " + o[p];
		n++;
		if ((n % 5) == 0) {
			s += "\n";
		}
		else {
			s += "  ";
		}
	}
	alert(s);
	
}

// ====================================================
// Begin functions for listbox sort and move
// ====================================================

// -------------------------------------------------------------------
// hasOptions(obj)
//  Utility function to determine if a select object has an options array
// -------------------------------------------------------------------
function hasOptions(obj) {
        if (obj!=null && obj.options!=null) { return true; }
        return false;
        }

// -------------------------------------------------------------------
// selectUnselectMatchingOptions(select_object,regex,select/unselect,true/false)
//  This is a general function used by the select functions below, to
//  avoid code duplication
// -------------------------------------------------------------------
function selectUnselectMatchingOptions(obj,regex,which,only) {
        if (window.RegExp) {
                if (which == "select") {
                        var selected1=true;
                        var selected2=false;
                        }
                else if (which == "unselect") {
                        var selected1=false;
                        var selected2=true;
                        }
                else {
                        return;
                        }
                var re = new RegExp(regex);
                if (!hasOptions(obj)) { return; }
                for (var i=0; i<obj.options.length; i++) {
                        if (re.test(obj.options[i].text)) {
                                obj.options[i].selected = selected1;
                                }
                        else {
                                if (only == true) {
                                        obj.options[i].selected = selected2;
                                        }
                                }
                        }
                }
        }
                
// -------------------------------------------------------------------
// selectMatchingOptions(select_object,regex)
//  This function selects all options that match the regular expression
//  passed in. Currently-selected options will not be changed.
// -------------------------------------------------------------------
function selectMatchingOptions(obj,regex) {
        selectUnselectMatchingOptions(obj,regex,"select",false);
        }
// -------------------------------------------------------------------
// selectOnlyMatchingOptions(select_object,regex)
//  This function selects all options that match the regular expression
//  passed in. Selected options that don't match will be un-selected.
// -------------------------------------------------------------------
function selectOnlyMatchingOptions(obj,regex) {
        selectUnselectMatchingOptions(obj,regex,"select",true);
        }
// -------------------------------------------------------------------
// unSelectMatchingOptions(select_object,regex)
//  This function Unselects all options that match the regular expression
//  passed in. 
// -------------------------------------------------------------------
function unSelectMatchingOptions(obj,regex) {
        selectUnselectMatchingOptions(obj,regex,"unselect",false);
        }
        
// -------------------------------------------------------------------
// sortSelect(select_object)
//   Pass this function a SELECT object and the options will be sorted
//   by their text (display) values
// -------------------------------------------------------------------
function sortSelect(obj) {
        var o = new Array();
        if (!hasOptions(obj)) { return; }
        for (var i=0; i<obj.options.length; i++) {
                o[o.length] = new Option( obj.options[i].text, obj.options[i].value, obj.options[i].defaultSelected, obj.options[i].selected) ;
                }
        if (o.length==0) { return; }
        o = o.sort( 
                function(a,b) { 
                        if ((a.text+"") < (b.text+"")) { return -1; }
                        if ((a.text+"") > (b.text+"")) { return 1; }
                        return 0;
                        } 
                );

        for (var i=0; i<o.length; i++) {
                obj.options[i] = new Option(o[i].text, o[i].value, o[i].defaultSelected, o[i].selected);
                }
        }

// -------------------------------------------------------------------
// selectAllOptions(select_object)
//  This function takes a select box and selects all options (in a 
//  multiple select object). This is used when passing values between
//  two select boxes. Select all options in the right box before 
//  submitting the form so the values will be sent to the server.
// -------------------------------------------------------------------
function selectAllOptions(obj) {
        if (!hasOptions(obj)) { return; }
        for (var i=0; i<obj.options.length; i++) {
                obj.options[i].selected = true;
                }
        }
        
// -------------------------------------------------------------------
// moveSelectedOptions(select_object,select_object[,autosort(true/false)[,regex]])
//  This function moves options between select boxes. Works best with
//  multi-select boxes to create the common Windows control effect.
//  Passes all selected values from the first object to the second
//  object and re-sorts each box.
//  If a third argument of 'false' is passed, then the lists are not
//  sorted after the move.
//  If a fourth string argument is passed, this will function as a
//  Regular Expression to match against the TEXT or the options. If 
//  the text of an option matches the pattern, it will NOT be moved.
//  It will be treated as an unmoveable option.
//  You can also put this into the <SELECT> object as follows:
//    onDblClick="moveSelectedOptions(this,this.form.target)
//  This way, when the user double-clicks on a value in one box, it
//  will be transferred to the other (in browsers that support the 
//  onDblClick() event handler).
// -------------------------------------------------------------------
function moveSelectedOptions(from,to) {
        // Unselect matching options, if required
        if (arguments.length>3) {
                var regex = arguments[3];
                if (regex != "") {
                        unSelectMatchingOptions(from,regex);
                        }
                }
        // Move them over
        if (!hasOptions(from)) { return; }
        for (var i=0; i<from.options.length; i++) {
                var o = from.options[i];
                if (o.selected) {
                        if (!hasOptions(to)) { var index = 0; } else { var index=to.options.length; }
                        to.options[index] = new Option( o.text, o.value, false, false);
                        }
                }
        // Delete them from original
        for (var i=(from.options.length-1); i>=0; i--) {
                var o = from.options[i];
                if (o.selected) {
                        from.options[i] = null;
                        }
                }
        if ((arguments.length<3) || (arguments[2]==true)) {
                sortSelect(from);
                sortSelect(to);
                }
        from.selectedIndex = -1;
        to.selectedIndex = -1;
        }

// -------------------------------------------------------------------
// copySelectedOptions(select_object,select_object[,autosort(true/false)])
//  This function copies options between select boxes instead of 
//  moving items. Duplicates in the target list are not allowed.
// -------------------------------------------------------------------
function copySelectedOptions(from,to) {
        var options = new Object();
        if (hasOptions(to)) {
                for (var i=0; i<to.options.length; i++) {
                        options[to.options[i].value] = to.options[i].text;
                        }
                }
        if (!hasOptions(from)) { return; }
        for (var i=0; i<from.options.length; i++) {
                var o = from.options[i];
                if (o.selected) {
                        if (options[o.value] == null || options[o.value] == "undefined" || options[o.value]!=o.text) {
                                if (!hasOptions(to)) { var index = 0; } else { var index=to.options.length; }
                                to.options[index] = new Option( o.text, o.value, false, false);
                                }
                        }
                }
        if ((arguments.length<3) || (arguments[2]==true)) {
                sortSelect(to);
                }
        from.selectedIndex = -1;
        to.selectedIndex = -1;
        }

// -------------------------------------------------------------------
// moveAllOptions(select_object,select_object[,autosort(true/false)[,regex]])
//  Move all options from one select box to another.
// -------------------------------------------------------------------
function moveAllOptions(from,to) {
        selectAllOptions(from);
        if (arguments.length==2) {
                moveSelectedOptions(from,to);
                }
        else if (arguments.length==3) {
                moveSelectedOptions(from,to,arguments[2]);
                }
        else if (arguments.length==4) {
                moveSelectedOptions(from,to,arguments[2],arguments[3]);
                }
        }

// -------------------------------------------------------------------
// copyAllOptions(select_object,select_object[,autosort(true/false)])
//  Copy all options from one select box to another, instead of
//  removing items. Duplicates in the target list are not allowed.
// -------------------------------------------------------------------
function copyAllOptions(from,to) {
        selectAllOptions(from);
        if (arguments.length==2) {
                copySelectedOptions(from,to);
                }
        else if (arguments.length==3) {
                copySelectedOptions(from,to,arguments[2]);
                }
        }

// -------------------------------------------------------------------
// swapOptions(select_object,option1,option2)
//  Swap positions of two options in a select list
// -------------------------------------------------------------------
function swapOptions(obj,i,j) {
        var o = obj.options;
        var i_selected = o[i].selected;
        var j_selected = o[j].selected;
        var temp = new Option(o[i].text, o[i].value, o[i].defaultSelected, o[i].selected);
        var temp2= new Option(o[j].text, o[j].value, o[j].defaultSelected, o[j].selected);
        o[i] = temp2;
        o[j] = temp;
        o[i].selected = j_selected;
        o[j].selected = i_selected;
        }
        
// -------------------------------------------------------------------
// moveOptionUp(select_object)
//  Move selected option in a select list up one
// -------------------------------------------------------------------
function moveOptionUp(obj) {
        if (!hasOptions(obj)) { return; }
        for (i=0; i<obj.options.length; i++) {
                if (obj.options[i].selected) {
                        if (i != 0 && !obj.options[i-1].selected) {
                                swapOptions(obj,i,i-1);
                                obj.options[i-1].selected = true;
                                }
                        }
                }
        }

// -------------------------------------------------------------------
// moveOptionDown(select_object)
//  Move selected option in a select list down one
// -------------------------------------------------------------------
function moveOptionDown(obj) {
        if (!hasOptions(obj)) { return; }
        for (i=obj.options.length-1; i>=0; i--) {
                if (obj.options[i].selected) {
                        if (i != (obj.options.length-1) && ! obj.options[i+1].selected) {
                                swapOptions(obj,i,i+1);
                                obj.options[i+1].selected = true;
                                }
                        }
                }
        }

// -------------------------------------------------------------------
// removeSelectedOptions(select_object)
//  Remove all selected options from a list
//  (Thanks to Gene Ninestein)
// -------------------------------------------------------------------
function removeSelectedOptions(from) { 
        if (!hasOptions(from)) { return; }
        for (var i=(from.options.length-1); i>=0; i--) { 
                var o=from.options[i]; 
                if (o.selected) { 
                        from.options[i] = null; 
                        } 
                } 
        from.selectedIndex = -1; 
        } 

// -------------------------------------------------------------------
// removeAllOptions(select_object)
//  Remove all options from a list
// -------------------------------------------------------------------
function removeAllOptions(from) { 
        if (!hasOptions(from)) { return; }
        for (var i=(from.options.length-1); i>=0; i--) { 
                from.options[i] = null; 
                } 
        from.selectedIndex = -1; 
        } 

// -------------------------------------------------------------------
// addOption(select_object,display_text,value,selected)
//  Add an option to a list
// -------------------------------------------------------------------
function addOption(obj,text,value,selected) {
        if (obj!=null && obj.options!=null) {
                obj.options[obj.options.length] = new Option(text, value, false, selected);
                }
        }



