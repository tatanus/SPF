// commonUtils.js
// Copyright (c) 2003 - 2010 Citrix Systems, Inc. All Rights Reserved.

function numbersonly(myfield, e) {
    var key;
    var keychar;

    if (window.event) {
        key = window.event.keyCode;
    } else if (e) {
        key = e.which;
    } else {
        return true;
    }
    keychar = String.fromCharCode(key);

    // control keys
    if ((key == null) || (key == 0) || (key == 8) ||
            (key == 9) || (key == 13) || (key == 27) ) {
        return true;
    }

    // numbers
    if ((("0123456789").indexOf(keychar) > -1)) {
        return true;
    }

    return false;
}



function putInTopFrame() {
    
}

function clearFormData(){
    var submittedForm = document.CitrixForm;
    for(i = 0; i < submittedForm.elements.length;i++){
         if (submittedForm.elements[i].name != "SESSION_TOKEN"){
              submittedForm.elements[i].value = "";
         }
    }
}



function isMainFrame(w) {
    var d = null;
   
    d = w.document;
        
    if (d != null) {
    
        return (d.getElementById('launchDiv') != null);
    
    } else {
        return false;
    }
}



var currWindow = null;
function findMainFrame(w) {
    try{
        if (isMainFrame(w)) {
            return w;
        }
    } catch (e) {
        // Caught a JavaScript exception. This may happen when attempting to
        // access a document object which has different origins to the current
        // document, e.g. resides on a different server especially when iframe is 
        // used, the parent and child window belongs to different domain or origin.
        return currWindow;
    }
    
    if (w.parent == w) {
        // This is the top frame - nowhere else to look
        return null;
    } else {
        // Search the parent of this frame
        currWindow = w;
        return findMainFrame(w.parent);
    }
}


function getTopFrame(w) {
    if (w != w.parent) {
        var doc = w.parent.document;
        var iframes = doc.getElementsByTagName('iframe');
        for (var i = 0; i < iframes.length; i++) {
            if (iframes[i].name.indexOf('timeoutFrame') == 0) {
                return w.parent;
            }
        }
    }

    return null;
}


function isPopupWindow(w) {
    var isPopup = false;

    try {
        // If a window and its opener have different origins (different host, port or protocol URL components)
        // Firefox throws a permission denied error when attempting to access properties on the opener.
        // This situation can arise if a customer creates an HTML page in one domain containing a link
        // to a WI site in a different domain.
        isPopup = (w.opener && w.opener!=null && !w.opener.closed && w.opener.parent != null);
    } catch (e) {}

    return isPopup;
}


function redirectToMainFrame(href) {
    // See if this frame, or one of its parents, is the main frame
    var mainFrame = findMainFrame(window);

    // If this is a pop-up window, search the hierarchy of its opener
    var isPopup = isPopupWindow(window);
    if ((mainFrame == null) && isPopup) {
        mainFrame = findMainFrame(window.opener);
    }

    // Fall back to the current frame as we have nowhere else to go
    if (mainFrame == null) {
        mainFrame = window;
    }

    // Use location.replace to prevent the current page from appearing in
    // the browser history and being accessible via the browser's Back button.
    mainFrame.location.replace(href);

    // If this window is a pop-up and we did not redirect it, close it
    var redirectedCurrentWindow = (mainFrame == window);
    if (isPopup && !redirectedCurrentWindow) {
        window.close();
    }
}


function isMatchedAttribute(element, attribute, attributeValue)
{
    if (attribute == "class")
    {
      var pattern = new RegExp("(^| )" + attributeValue + "( |$)");

      return pattern.test(element.className);
    }
    else if (attribute == "for")
    {
      if (element.getAttribute("htmlFor") || element.getAttribute("for"))
      {
        return element.htmlFor == attributeValue;
      }
    }
    else
    {
        return element.getAttribute(attribute) == attributeValue;
    }
}


function getFrameCursorPosition(event)
{
    if (typeof event == "undefined")
    {
        event = window.event;
    }

    var scrollingPosition = getFrameScrollingPosition();
    var cursorX = 0;
    var cursorY = 0;

    if (typeof event.pageX != "undefined" && typeof event.x != "undefined")
    {
        cursorX = event.pageX;
        cursorY = event.pageY;
    }
    else
    {
        cursorX = event.clientX + scrollingPosition[0];
        cursorY = event.clientY + scrollingPosition[1];
    }

    return [cursorX, cursorY];
}


function getEventTarget(event)
{
  var targetElement = null;

  if (typeof event.target != "undefined")
  {
    targetElement = event.target;
  }
  else
  {
    targetElement = event.srcElement;
  }

  return targetElement;
}


function attachEventHandler(target, eventType, functionRef, capture)
{
  if (typeof target.addEventListener != "undefined")
  {
    target.addEventListener(eventType, functionRef, capture);
  }
  else if (typeof target.attachEvent != "undefined")
  {
    target.attachEvent("on" + eventType, functionRef);
  }
  else
  {
    eventType = "on" + eventType;

    if (typeof target[eventType] == "function")
    {
      var oldHandler = target[eventType];

      target[eventType] = function()
      {
        oldHandler();

        return functionRef();
      }
    }
    else
    {
      target[eventType] = functionRef;
    }
  }

  return true;
}


function stopEventPropagation(e)
{
    e = e || event;/* get IE event (not passed) */
    e.stopPropagation ? e.stopPropagation() : e.cancelBubble = true;
}


function addFrameToDiv(divId, frameIdPrefix, frameSrc, frameTitle, clearDiv) {
    var container = document.getElementById(divId);

    if (container) {
        // Remove existing child elements if required
        while (clearDiv && container.hasChildNodes()) {
            container.removeChild(container.lastChild);
        }

        var iframe = document.createElement('IFRAME');

        iframe.id = frameIdPrefix + getFrameSuffix();
//        iframe.width = '0';
//        iframe.height = '0';
        iframe.name = frameIdPrefix + getFrameSuffix();
        iframe.src = frameSrc;
        iframe.title = frameTitle;
        container.appendChild(iframe);
    }
}

function newAjaxRequest() {
    try { return new XMLHttpRequest(); } catch(e) {}
    try { return new ActiveXObject("Msxml2.XMLHTTP"); } catch (e) {}
    try { return new ActiveXObject("Microsoft.XMLHTTP"); } catch (e) {}
    return null;
}

function assignDesktop(elt) {
    var req = newAjaxRequest();
    var href = elt.href;
    var ajaxUrl = href.replace('launcher.aspx', 'assignDesktop.aspx');

    if (req != null) {
        // Show the spinner icon and disable the app link to prevent the user from initiating
        // multiple simultaneous assignment requests for the same desktop. The link is not re-enabled
        // since the markup for the desktop is replaced (assignment succeeded) or the page is redirected
        // (assignment failed).
        disableAppLink(elt);

        setSpinnerVisible(elt.id, true);
	
        req.onreadystatechange = function() { handleDesktopAssignmentResponse(elt, req) };
        req.open("GET", ajaxUrl, true);
        req.send(null);
    } else {
        // If ajax is not available just launch the desktop without updating the UI.
        // (this situation would arise when using IE6 with ActiveX disabled.)
        // In this case the assignment is performed by the broker.
        // When there are multiple assign-on-first-use desktops within a group, the user
        // will need to press refresh (or log off/on) to see the updated desktop name and
        // assign additional desktops.
        addCurrentTimeToHref(elt, elt.href);
        launch(elt);
    }
}

function handleDesktopAssignmentResponse(elt, req)
{
    if (req.readyState != 4 || req.status != 200)  {
        return;
    }

    var json = eval('(' + req.responseText + ')');

    // A redirect URL is returned in the ajax response if the desktop assignment failed
    if (json.redirectUrl) {
        location.href = json.redirectUrl;
        return;
    }

    if (json.feedbackMessage) {
        setFeedback(json.feedbackMessage, 'Info');
    }

    var target = document.getElementById("desktop_" + elt.id)
    if (target) {
        var markup = unescapeHTML(json.markup);
        target.innerHTML = markup;

        // The original elt has now been replaced in the DOM (with updated markup for the element's desktop group).
        // The following line locates the corresponding replaced element, so that the launch() function can operate on
        // the 'live' element (e.g., to make it inactive) rather than the element that has been removed from the DOM.
        elt = document.getElementById(elt.id);

        
            // Update the layout since the page size may have changed. This is only needed for full graphics mode.
            updateLayout();
        
    }

    if (json.autoLaunch) {
        addCurrentTimeToHref(elt, elt.href);
        launch(elt);
    }
}


function unescapeHTML(markup) {
    markup = markup.replace(/&lt;/g, "<");
    markup = markup.replace(/&gt;/g, ">");
    markup = markup.replace(/&quot;/g, "\"");
    markup = markup.replace(/&#39;/g, "\'");
    markup = markup.replace(/&#37;/g, "%");
    markup = markup.replace(/&#59;/g, ";");
    markup = markup.replace(/&#40;/g, "(");
    markup = markup.replace(/&#41;/g, ")");
    markup = markup.replace(/&amp;/g, "&");
    markup = markup.replace(/&#43;/g, "+");

    return markup;
}


function nolaunch() { return false; }


function disableAppLink(elt)
{
    elt.classNameOrig = elt.className;
    elt.className = elt.className + " iconLinkLaunching";

    elt.onclickOrig = elt.onclick;
    elt.onclick = nolaunch;        
}


function enableAppLink(elt)
{
    elt.className = elt.classNameOrig;
    elt.onclick = elt.onclickOrig;        
}


function showDesktopLaunchingUI(elt) {
    var launchTimeout = 2 * 1000;

    if (launchTimeout > 0) {
        disableAppLink(elt);

        setSpinnerVisible(elt.id, true);
        setRestartPaneVisible(elt.id, true);
    }
    
    // Called before adding the frame to the div as otherwise it
    // breaks on Windows Mobile 6.1 (spinner never disappears).
    setTimeout(function() {
                   setRestartPaneVisible(elt.id, false);
                   setSpinnerVisible(elt.id, false);
                   updateDesktopIcon(elt.id, true);
                   enableAppLink(elt);
               }, launchTimeout);
}



function launch(elt) {
    showDesktopLaunchingUI(elt);
    autolaunch(elt.href);
}

function autolaunch(url) {
    addFrameToDiv('launchDiv',
                  'launchFrame',
                  url,
                  'The hidden frame for Web Interface resource access',
                  true);
}


function setSpinnerVisible(appId, show) {
    var mainframe = findMainFrame(window);
    var eltApp = mainframe.document.getElementById("spinner_" + appId);

    if (eltApp) {
        eltApp.src = (show) ? "../media/LaunchSpinner.gif" : "../media/Transparent16.gif";
    }

    // For desktops tab, show different spinner image.
    var eltDesktop = mainframe.document.getElementById("desktopSpinner_" + appId);    
    if (eltDesktop) {
        var spinnerClass = (show) ? "delayedImageSpinner" : "delayedImageNone";
        eltDesktop.className = spinnerClass;
        eltDesktop.classNameOnBlur = spinnerClass;
    }
}


function addDesktopRetryFrame(frameSrc) {
    setTimeout(function(){
        addFrameToDiv('retryPopulatorDiv',
                      'retryPopulatorFrame',
                      frameSrc,
                      'The hidden frame for the delayed launch functionality',
                      false);
    },1);
}




function indexOfElement(arrayToSearch, elementName) {
    for( var i =0; i<arrayToSearch.length; i++) {
        if(arrayToSearch[i] == elementName) {
           return i;
        }
    }
    return -1;
}



function maintainAccessibility(buttonId, displayInline) {
  if (isHighContrastEnabled()) {
      displayHighContrastButton(buttonId, displayInline);
  }
}


function isHighContrastEnabled() {
    var testDiv = document.createElement("div");
    testDiv.style.background = "url(../media/Error24.gif)";
    testDiv.style.display="none";
    document.body.appendChild(testDiv);
    // test for high contrast
    var backgroundImage = null;
    if (window.getComputedStyle) {
        var cStyle = getComputedStyle(testDiv, "");
        backgroundImage = cStyle.getPropertyValue("background-image");
    } else {
        backgroundImage = testDiv.currentStyle.backgroundImage;
    }
    if (backgroundImage != null && backgroundImage == "none" ) {
        return true;
    }
    return false;
}


function displayHighContrastButton(buttonId, displayInline) {
   var graphicButton = document.getElementById("graphic_"+buttonId);
   if (graphicButton != null) {
       graphicButton.style.display='none';
   }
   var highContrastButton = document.getElementById("highContrast_"+buttonId);
   if (highContrastButton != null) {
      if (displayInline) {
          // Currently search button needs to be displayed inline for better alignment.
          highContrastButton.style.display='inline';
      } else {
          highContrastButton.style.display='block';
      }
   }
}


function lgChangeTab(dropdown)
{
    location.href = dropdown.options[dropdown.selectedIndex].value;
}

function setRestartPaneVisible(desktopId, isVisible) {
    var container = document;
    var restartElt = container.getElementById("restart_" + desktopId);

    if (!restartElt) {
 	container = findMainFrame(window).document;
        restartElt = container.getElementById("restart_" + desktopId);
    }

    if (restartElt && restartElt.className != "restartLinkNotRestartable") {
        restartElt.className  = isVisible ? "restartLinkAlwaysShow" : "restartLinkShowOnFocus";
    }

    
}


function updateDesktopIcon(desktopId, isActive) {
    var screenElt = document.getElementById("screen_" + desktopId);
    if (!screenElt) {
        screenElt = findMainFrame(window).document.getElementById("screen_" + desktopId);
    }

    if (screenElt) {
        screenElt.className = isActive ? "desktopScreen activeDesktop" : "desktopScreen";
    }
}

function updateDelayedLaunchImage(desktopId, active) {
    var desktopIconElt = document.getElementById('desktopSpinner_' + desktopId);
    if (!desktopIconElt) {
        return;
    }

    if (active) {
        desktopIconElt.classNameOnBlur = desktopIconElt.className;
        
        if (desktopIconElt.className == "delayedImageNone") {
            setLaunchReadyIconRollOver(document, desktopId);
        }
    } else {
        desktopIconElt.className = desktopIconElt.classNameOnBlur;
    }
}

function updateDirectLaunchDisplay(elt, active) {
    var desktopId = null;
    if (elt.id.indexOf('screen_') == 0) {
        desktopId = elt.id.substring(7);
        updateDelayedLaunchImage(desktopId, active);
    }
}

function updateDesktopDisplay(elt, active) {
    elt.className = (active) ? "desktopResource desktopFocus" : "desktopResource";
    
    var desktopId = null;
    if (elt.id.indexOf('desktop_') == 0) {
        desktopId = elt.id.substring(8);
        updateDelayedLaunchImage(desktopId, active);
    }
}

function setLaunchReadyIconRollOver(doc, desktopId) {
    var spinnerNodeDesktopsTab = doc.getElementById('desktopSpinner_' + desktopId);
    if (spinnerNodeDesktopsTab) {
        spinnerNodeDesktopsTab.className = "delayedImagePlay";
    }
}

// Changes the launch spinner into an icon indicating the resource is ready to be manually launched
function setLaunchReadyIcon(doc, desktopId) {
    var spinnerNode = doc.getElementById('spinner_' + desktopId);
    if (spinnerNode) {
        spinnerNode.src = "../media/LaunchReady.gif";
    }
    
    var spinnerNodeDesktopsTab = doc.getElementById('desktopSpinner_' + desktopId);
    if (spinnerNodeDesktopsTab) {
        spinnerNodeDesktopsTab.className = "delayedImagePlay";
        spinnerNodeDesktopsTab.classNameOnBlur = "delayedImagePlay";
    }
}

function showRestart(id, isActive) {
    var el = document.getElementById("restartConfirmation_" + id);
    el.style.visibility = isActive ? "visible" : "hidden";
}
function getElementPosition(elt)
{
  var positionX = 0;
  var positionY = 0;

  while (elt != null)
  {
    positionX += elt.offsetLeft;
    positionY += elt.offsetTop;
    elt = elt.offsetParent;
  }

  return [positionX, positionY];
}


function getFrameViewportSize()
{
  var sizeX = 0;
  var sizeY = 0;

  if (typeof window.innerWidth != 'undefined')
  {
      sizeX = window.innerWidth;
      sizeY = window.innerHeight;
  }
  else if (typeof document.documentElement != 'undefined'
      && typeof document.documentElement.clientWidth != 'undefined'
      && document.documentElement.clientWidth != 0)
  {
      sizeX = document.documentElement.clientWidth;
      sizeY = document.documentElement.clientHeight;
  }
  else
  {
      sizeX = document.getElementsByTagName('body')[0].clientWidth;
      sizeY = document.getElementsByTagName('body')[0].clientHeight;
  }

  return [sizeX, sizeY];
}


function getFrameScrollingPosition()
{
  var scrollX = 0;
  var scrollY = 0;

  if (typeof window.pageYOffset != 'undefined')
  {
      scrollX = window.pageXOffset;
      scrollY = window.pageYOffset;
  }

  else if (typeof document.documentElement.scrollTop != 'undefined'
      && (document.documentElement.scrollTop > 0 ||
      document.documentElement.scrollLeft > 0))
  {
      scrollX = document.documentElement.scrollLeft;
      scrollY = document.documentElement.scrollTop;
  }

  else if (typeof document.body.scrollTop != 'undefined')
  {
      scrollX = document.body.scrollLeft;
      scrollY = document.body.scrollTop;
  }

  return [scrollX, scrollY];
}


function changeCloseImage(currentNode, isMouseHover) {
    for (var j = 0; j <currentNode.childNodes.length; j++) {
        var imgChildNode = currentNode.childNodes[j];
        if (imgChildNode.nodeName == "IMG") {
            if (isMouseHover) {
               imgChildNode.origSrc = imgChildNode.src;
               imgChildNode.src="../media/ActiveClose.gif";
            } else {
               imgChildNode.src= imgChildNode.origSrc;
            }
        }
    }
}

function getDefaultPopupShowDelay()
{
    return 500;
}


function getDefaultPopupHideDelay()
{
    return 200;
}


function getPopupId(associatedId)
{
    return "Popup_" + associatedId;
}


function show_popup_helper(associatedId)
{
    clearPopupTimer(associatedId);

    var popupId = getPopupId(associatedId);
    var popup = document.getElementById(popupId);
    var associated = document.getElementById(associatedId);

    
    if(!isPopupWanted(associatedId))
    {
        return;
    }

    
    var desiredPosition = popup.savedCursorPosition;
    var onScreenPosition;

    if(desiredPosition)
    {
        onScreenPosition = shuffle(popup, desiredPosition, 0, 10, 25);
    }
    else
    {
        
        desiredPosition = getElementPosition(associated);
        
        if (isMatchedAttribute(popup, "class", "rightAligned")) {
            onScreenPosition = shuffle(popup, desiredPosition, associated.offsetWidth, 0, 0);
        } else {
            onScreenPosition = shuffle(popup, desiredPosition, 0, 0, associated.offsetHeight);
        }
    }

    popup.style.left = onScreenPosition[0] + 'px';
    popup.style.top = onScreenPosition[1] + 'px';

    
}


shuffle.margin = 25;


function shuffle(popup, originalPosition, offsetRight, offsetAbove, offsetBelow)
{
    // Make a copy of the originalPosition
    var position = [originalPosition[0], originalPosition[1]];

    viewPortSize = getFrameViewportSize();
    scollingPos = getFrameScrollingPosition();

    
    var rightmost = position[0] + offsetRight + popup.offsetWidth;
    var rightmostVisible = scollingPos[0] + viewPortSize[0] - shuffle.margin;
    if( rightmost > rightmostVisible )
    {
        position[0] = rightmostVisible - popup.offsetWidth;
    }

    
    var leftmost = position[0] + offsetRight;
    var leftmostVisible = scollingPos[0] + shuffle.margin;
    if (leftmost < leftmostVisible) {
        position[0] = leftmostVisible;
    } else {
        position[0] = leftmost;
    }

    
    var bottommost = position[1] + popup.offsetHeight + offsetBelow;
    var bottommostVisible = scollingPos[1] + viewPortSize[1] - shuffle.margin;
    if( bottommost > bottommostVisible )
    {
        
        var topmost = position[1] - popup.offsetHeight - offsetAbove;
        var topmostVisible = scollingPos[1] + shuffle.margin;
        if( topmost >= topmostVisible )
        {
            
            position[1] -= (popup.offsetHeight + offsetAbove);
        }
        else {
            
            position[1] = topmostVisible;
        }
    }
    else {
        
        position[1] += offsetBelow;
    }

    return position;
}


function hide_popup_help(associatedId)
{
    clearPopupTimer(associatedId); // this function can be a timer callback, so clear any timer

    var popupId = getPopupId(associatedId);
    var popup = document.getElementById(popupId);

    if( popup != null )
    {
        removeIframeLayer(popup);
        popup.style.left = '-999px';
        popup.style.top = '-999px';
        popup.savedCursorPosition = null;
    }
}


function createIframeLayer(popup)
{
    
    var layer = popup.iframeLayer;

    if(layer==null)
    {
        
        layer = document.createElement('iframe');
        layer.className = "hiddenFrameLayer"; 
        layer.tabIndex = '-1';
        layer.src = 'javascript:false;';
        popup.parentNode.appendChild(layer);

        
        popup.iframeLayer = layer;
    }

    
    layer.style.left = popup.offsetLeft + 'px';
    layer.style.top = popup.offsetTop + 'px';
    layer.style.width = popup.offsetWidth + 'px';
    layer.style.height = popup.offsetHeight + 'px';
}


function removeIframeLayer(popup)
{
    var layer = popup.iframeLayer;

    if(layer != null )
    {
        layer.parentNode.removeChild(layer);
        popup.iframeLayer = null;
    }
}



function setPopupWanted(associatedId, timer, wanted)
{
    associated = document.getElementById(associatedId);
    associated.popupWanted = wanted;
    
    clearPopupTimer(associatedId);

    
    associated.popupTimer = timer;
}

function isPopupWanted(associatedId)
{
    associated = document.getElementById(associatedId);
    return associated.popupWanted;
}

function clearPopupTimer(associatedId)
{
    associated = document.getElementById(associatedId);
    if(associated.popupTimer != null)
    {
        window.clearTimeout(associated.popupTimer);
        associated.popupTimer = null;
    }
}

function setShowingPopup(associatedId, showing) {
    associated = document.getElementById(associatedId);
    associated.showingPopup = showing;
}

function isShowingPopup(associatedId) {
    associated = document.getElementById(associatedId);
    return associated.showingPopup;
}


function setup_inline_help(eltId)
{
    var associated = document.getElementById(eltId);

    associated.hasPopup = true;

    associated.onmouseover=function()
    {
        wi_popup_show_delayed(eltId);
    }

    associated.onmouseout=function()
    {
        wi_popup_hide_delayed(eltId);
    }

    attachEventHandler(associated, "mousemove", record_cursor_position, false);

    associated.onclick=function()
    {
        wi_popup_show(eltId);

        return false; 
    }

    associated.onblur=function()    
    {
        wi_popup_hide_delayed(eltId);
    }

    var popup = document.getElementById(getPopupId(eltId));
    if(popup) {
        
        popup.onmouseover = popup.onclick = function() { setPopupWanted(eltId, null, true); }
        popup.onmouseout = function() { wi_popup_hide_delayed(eltId); }

        
        var horizonTop = document.getElementById('horizonTop');
        if (horizonTop) {
            horizonTop.appendChild(popup);
        }
    }
}


function setup_drop_down_menu(eltId)
{
    var associated = document.getElementById(eltId);
    var popupId = getPopupId(eltId);
    var popup = document.getElementById(popupId);

    associated.hasPopup = true;

    // reduce the delay to 100ms from the default of 500ms
    var delay = 100;
    popup.onmouseover=function()
    {
        wi_popup_show_delayed(eltId, delay);
    }

    popup.onmouseout=function()
    {
        wi_popup_hide_delayed(eltId, delay);
    }

    associated.onmouseover=function()
    {
        wi_popup_show_delayed(eltId, delay);
    }

    associated.onmouseout=function()
    {
        wi_popup_hide_delayed(eltId, delay);
    }

    var show = function() { wi_popup_show(eltId); };
    var hide = function() { wi_popup_hide(eltId); };

    // ensure keyboard navigation opens the menu
    var popupLinks = popup.getElementsByTagName("a");
    for(var i=0;i<popupLinks.length;i++) {
        popupLinks[i].onfocus = show;
        popupLinks[i].onblur = hide;
    };
}

function setup_custom_menu(eltId)
{
    var associated = document.getElementById(eltId);
    var popupId = getPopupId(eltId);
    var popup = document.getElementById(popupId);

    associated.hasPopup = true;

    associated.onclick = function(e) { 
        associated.popupWanted ? wi_popup_hide(eltId) : setShowingPopup(eltId, true); wi_popup_show(eltId);
        return false;
    };

    // attach an event handler to the document to dismiss the menu
    attachEventHandler(document, 'click', function() { wi_popup_doc_handler(eltId); }, false);

    // ensure keyboard navigation opens the menu
    var popupLinks = popup.getElementsByTagName("a");
    for(var i = 0; i < popupLinks.length; i++) {
        popupLinks[i].onfocus = function() { wi_popup_show(eltId); };
        popupLinks[i].onblur = function() { wi_popup_hide(eltId); };
    };
}


function record_cursor_position(event)
{
    var target = getEventTarget(event);

    
    while(target)
    {
        if(target.hasPopup)
        {
            break;
        }

        target = target.parentNode;
    }

    if(target)
    {
        var popup = document.getElementById(getPopupId(target.id));
        popup.savedCursorPosition = getFrameCursorPosition(event);
    }

    return true;
}


function setup_behaviour_helper(elementClass, behaviour)
{
    var pageContent = document.getElementById("pageContent");
    if (pageContent)
    {
        
        apply_behaviour(elementClass, behaviour, pageContent.getElementsByTagName("a"));
        apply_behaviour(elementClass, behaviour, pageContent.getElementsByTagName("li"));
    }
}

function apply_behaviour(elementClass, behaviour, elements)
{
        for (var i = 0; i < elements.length; i++)
        {
            if(isMatchedAttribute(elements[i], "class", elementClass))
            {
                behaviour(elements[i].id);
            }
        }
}


function wi_popup_show(associatedId)
{
    wi_popup_show_delayed(associatedId, 0);
}


function wi_popup_show_delayed(associatedId, delay)
{
    if(delay==null)
    {
        delay = getDefaultPopupShowDelay();
    }

    if( delay > 0 )
    {
        setPopupWanted(
            associatedId,
            window.setTimeout("show_popup_helper('" + associatedId + "');", delay),
            true
            );
    }
    else
    {
        setPopupWanted(associatedId, null, true);
        show_popup_helper(associatedId);
    }
}


function wi_popup_hide(associatedId)
{
    wi_popup_hide_delayed(associatedId, 0);
}


function wi_popup_hide_delayed(associatedId, delay)
{
    if(delay==null)
    {
        delay = getDefaultPopupHideDelay();
    }

    if( delay > 0 )
    {
        setPopupWanted(
            associatedId,
            window.setTimeout("hide_popup_help('" + associatedId + "');", delay),
            false
            );
    }
    else
    {
        setPopupWanted(associatedId, null, false);
        hide_popup_help(associatedId);
    }
}


function wi_popup_doc_handler(associatedId) {
  // The onclick handler for a button menu displays the corresponding popup menu. However, after that function runs,
  // this onclick handler registered on the document (to hide the popup) also runs, due to event propagation.
  // Therefore, when intially showing the menu, the showingPopup field is set on the button element to indicate that
  // its menu should not be hidden at this point, to prevent it from disappearing as soon as it is shown.
  if (!isShowingPopup(associatedId)) {
    wi_popup_hide(associatedId);
  } else {
    setShowingPopup(associatedId, false);
  }
}


function setup_popup_behaviour()
{

    setup_behaviour_helper("inlineHelpLink", setup_inline_help); 
    setup_behaviour_helper("DropDownMenu", setup_drop_down_menu); 
    setup_behaviour_helper("CustomMenu", setup_custom_menu); 
}

function wizard_setup_popup_behaviour()
{
    setup_behaviour_helper("inlineHelpLink", setup_inline_help); 
}

function updateLayout() {

     if (document.getElementById) {
        var viewportSize = getFrameViewportSize();
        positionFooter(viewportSize[1]);

        if (document.getElementById('lightbox')) {
            configureLightbox();
        }

        
    }
 
}


function positionFooter(viewportHeight) {
     if (viewportHeight > 0) {
        var totalHeight = 0;

        var contentElement = document.getElementById("pageContent");
        if (contentElement) {
            totalHeight += contentElement.offsetHeight;
        }

        var footerElement = document.getElementById("footer");
        var footerHeight = 0;
        if (footerElement) {
            footerHeight = footerElement.offsetHeight;
            totalHeight += footerHeight;
        }

        var space = viewportHeight - totalHeight;

        if (space > 0) {
            var heightFillerElement = document.getElementById("heightFiller");
            if (heightFillerElement) {
                heightFillerElement.style.height = space + 'px';
            }
        }
    } 
}


function setOverallWrapperSize(viewportWidth) {
    // get width of wrapper, but leave room for borders either side
    var wrapperWidth = viewportWidth;// - 40;

    // ensure it is within limits
    if (wrapperWidth < 780) {
        wrapperWidth = 780;
    }
//    if (wrapperWidth > 1000) {
//        wrapperWidth = 1000;
//    }

    // save as the best guess for next time
    setItemInCookie("wrapperWidth", wrapperWidth);

    var overallWrapper = document.getElementById("overallWrapper");
    if (overallWrapper) {
        overallWrapper.style.width = wrapperWidth + 'px';
    }
}

window.onresize = updateLayout;


function configureLightbox() {
    var mask = document.getElementById('lightboxMask');
    var viewportSize = getFrameViewportSize();

    // The lightbox overlay mask is resized to cover the viewport and the entire
    // document (whichever is larger). This prevents the underlying browser contents
    // from being revealed when scrolling in IE6 (which does not support 'position:fixed').
    var maskWidth = Math.max(viewportSize[0], document.body.clientWidth);
    var maskHeight = Math.max(viewportSize[1], document.body.clientHeight);

    mask.style.width = maskWidth + 'px';
    mask.style.height = maskHeight + 'px';

    // Calculate the position for the lightbox itself.
    var dialogTop = (viewportSize[1] / 6);

    // IE6 uses 'position:absolute', so the scroll position needs to be added on.


    var lightbox = document.getElementById('lightbox');
    lightbox.style.top = parseInt(dialogTop) + 'px';
}

function showLightbox(func) {
    document.getElementById('lightboxMask').style.display = 'block';
    document.getElementById('lightbox').style.display = 'block';
    lightboxCommitFunction = func;


}

function displayLightbox(anchor) {
    showLightbox(function() {redirectToMainFrame(anchor.href);});
}

// Dynamically pass in the top/bottom messages, and desktopId to the light box.
// If we get a valid desktopId in this method, we know that a delayed launch is already
// happening for that particular desktopId.
function showLightboxWithMessage(anchor, title, message, desktopId) {
    setLightboxTitle(title);
    setLightboxMessage(message);
    
    // This desktopId will get set only if the user clicks on the restart button while a
    // delayed launch is already happening, when the applist page was rendered.
    if (desktopId != null) {
        window.parent.parent.desktopShowingLightbox = desktopId;
        var desktopIndex = -1;
        if (window.parent.parent.delayedLaunchDesktops != null && window.parent.parent.delayedLaunchDesktops != ""){
           // Check if the delayed launch is still happening and if not update the lightbox text.
           desktopIndex = indexOfElement(window.parent.parent.delayedLaunchDesktops, desktopId);
        }
    }

    displayLightbox(anchor);
}

function hideLightbox(okPressed) {
    document.getElementById('lightboxMask').style.display = 'none';
    document.getElementById('lightbox').style.display = 'none';

    if (okPressed && (typeof lightboxCommitFunction == "function")) {
        lightboxCommitFunction();
    }
}

function handleLightboxKeys(e) {
    var keyCode = window.event ? window.event.keyCode : e.keyCode;

    if (keyCode == 27) { // Escape
        hideLightbox();
    }
}

function setLightboxString(id, message) {
    var elt = document.getElementById(id);

    if (elt != null) {
        elt.innerHTML = message;
        if (!message) {
            elt.style.display = 'none';
        } else {
            elt.style.display = 'block';
        }
    }
}

function setLightboxTitle(title) {
    setLightboxString('lightboxHeading', title);
}

function setLightboxMessage(message) {
    setLightboxString('lightboxMessage', message);
}

document.onkeypress = handleLightboxKeys;

function setItemInCookie(name, value) {
    if (value == null) {
        value = "";
    }
    if ((name == null) || (name == "")) {
        return;
    }

    var newCookie = "";
    var oldCookie = getCookie("WIClientInfo");
    if (oldCookie != "") {
        var cookieItems = oldCookie.split("~");
        for (i=0; i < cookieItems.length; i++) {
            // The name of the item will be escaped so we need to make sure
            // that we search for the escaped version.
            if (cookieItems[i].indexOf(escape(name) + "#") != 0) {
                newCookie += cookieItems[i] + "~";
            }
        }
    }

    newCookie += escape(name) + "#" + escape(value);
    storeCookie("WIClientInfo", newCookie);
}


function getItemFromCookie(name) {
    return unescape(getValueFromString(escape(name), getCookie("WIClientInfo"), "#", "~"));
}


function storeCookie(name, value) {
    if (value) { // non-null, non-empty
        value = "\"" + value + "\"";
    } else {
        value = "";
    }

    if (window.location.protocol.toLowerCase() == "https:") {
        value += "; secure";
    }

    var cookie = name + "=" + value;

    cookie = cookie + "; path=/Citrix/External/auth/";

    document.cookie = cookie;
}


function getCookie(name) {
    var cookie = getValueFromString(name, document.cookie, "=", ";");
    if ( (cookie.charAt(0) == "\"") && (cookie.charAt(cookie.length-1) == "\"") ) {
        cookie = cookie.substring(1, cookie.length-1);
    }
    return cookie;
}

function getValueFromString(name, str, sep1, sep2) {
    var result = "";

    if (str != null) {
        var itemStart = str.indexOf(name + sep1);
        if (itemStart != -1) {
            var valueStart = itemStart + name.length + 1;
            var valueEnd = str.indexOf(sep2, valueStart);
            if (valueEnd == -1) {
                valueEnd = str.length;
            }
            result = str.substring(valueStart, valueEnd);
        }
    }

    return result;
}
