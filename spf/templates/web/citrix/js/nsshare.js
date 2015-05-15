function CreateMainTable()
{
	document.writeln("<table class=\"full_width_height\" cellspacing=\"0\" cellpadding=\"0\" border=\"0\">");
}

function CreateBannerI()
{
	document.writeln("<tr>");
	document.writeln("<td valign=\"top\" class=\"full_width\">");
	document.writeln("<table class=\"full_width\" cellspacing=\"0\" cellpadding=\"0\">");
	document.writeln("<tr>");
}

function CreateBannerII()
{
	document.writeln("<td class=\"header_middle\">&nbsp;</td>");
	document.writeln("</tr>");
	document.writeln("<tr>");
	document.writeln("<td colspan=2 class=\"navbar\">&nbsp;</td>");
	document.writeln("</tr>");
	document.writeln("</table></td></tr>");
}

function AddHeaderAndBar()
{
	CreateBannerI();
	document.writeln("<td class=\"header_left\">&nbsp;</td>");
	CreateBannerII();	
}

function AddHeaderAndBarForTM()
{
	CreateBannerI();
	document.writeln("<td class=\"header_left_for_tm\">&nbsp;</td>");
	CreateBannerII();	
}

function AddHeaderAndBarForCitrix()
{
	CreateBannerI();
	document.writeln("<td class=\"header_ctx\">&nbsp;</td>");
	CreateBannerII();	
}

function AddFooter()
{
    document.writeln('<tr class="full_width_height">');
	document.writeln('<td valign="bottom">');
	document.writeln('<table class="full_width" cellspacing="0" cellpadding="0">');
	document.writeln('<tr>');
	document.writeln('<td class="watermark">');
	document.writeln('</td>');
	document.writeln('</tr>');
	document.writeln('</table>');
	document.writeln('</td>');
	document.writeln('</tr>');	
}

function AddBanner()
{
	document.writeln("<TABLE  cellSpacing=0 cellPadding=0 width=\"100%\" border=0>");
    document.writeln("<TBODY>");
    document.writeln("<TR height=94>");
    document.writeln("<TD style=\"BACKGROUND-IMAGE: url(../img/ctxBanner01.gif); BACKGROUND-REPEAT: no-repeat\" width=701></TD>");
    document.writeln("<TD style=\"BACKGROUND-IMAGE: url(../img/ctxBanner02.gif); BACKGROUND-REPEAT: repeat-x\">&nbsp;</TD>");
    document.writeln("</TR>");
    document.writeln("<TR>");
    document.writeln("<TD style=\"FONT-SIZE: 1px; HEIGHT: 8px; BACKGROUND-COLOR: white\" vAlign=bottom></TD>");
    document.writeln("</TR></TBODY></TABLE>");
}

var suitable_browser_to_use_png = false;
    
function canShowPNGWell()
{
	//As all morden browsers support PNG alfa transperancy by default this function will return true
	//except for IE 6 and lower, as IE 7 was first browser of IE series to support it
    var usrAgt = navigator.userAgent.toLowerCase();
	var msieOld = /(msie) [1-6]\.+/;
	if(msieOld.test(usrAgt)) {
		return false;
	}
	return true;
}

suitable_browser_to_use_png = canShowPNGWell();

function documentWriteGlowBoxUpper()
{
    if (suitable_browser_to_use_png == true)
        {
            document.write('<table class="CTXMSAM_LogonFont" cellpadding="0" cellspacing="0" align="center" border="0">\r\n');
            document.write('<tr>\r\n');
            document.write('<td class="glowBoxTop glowBoxLeft glowBoxTopLeftPng"></td>\r\n');
            document.write('<td class="glowBoxTop glowBoxTopMidPng"></td>\r\n');
            document.write('<td class="glowBoxTop glowBoxRight glowBoxTopRightPng"></td>\r\n');
            document.write('</tr>\r\n');
            document.write('<tr>\r\n');
            document.write('<td class="glowBoxLeft glowBoxMidLeftPng"></td>\r\n');
            document.write('<td class="glowBoxMidPng loginTableMidWidth">\r\n');
        }
        else
        {
            document.write('<table class="CTXMSAM_LogonFont" cellpadding="0" cellspacing="0" align="center" border="0">\r\n');
            document.write('<tr>\r\n');
            document.write('<td class="glowBoxTop glowBoxLeft glowBoxTopLeft"></td>\r\n');
            document.write('<td class="glowBoxTop glowBoxTopMid"></td>\r\n');
            document.write('<td class="glowBoxTop glowBoxRight glowBoxTopRight"></td>\r\n');
            document.write('</tr>\r\n');
            document.write('<tr>\r\n');
            document.write('<td class="glowBoxLeft glowBoxMidLeft"></td>\r\n');
            document.write('<td class="glowBoxMid loginTableMidWidth">\r\n');
        }
}

function documentWriteGlowBoxLower()
{
    if (suitable_browser_to_use_png == true)
        {
        	document.write('</td>');
            document.write('<td class="glowBoxRight glowBoxMidRightPng"></td>\r\n');
            document.write('</tr>\r\n');
            document.write('<tr>\r\n');
            document.write('<td class="glowBoxFooter glowBoxLeft glowBoxFooterLeftPng"></td>\r\n');
            document.write('<td class="glowBoxFooter glowBoxFooterMidPng"></td>\r\n');
            document.write('<td class="glowBoxFooter glowBoxRight glowBoxFooterRightPng"></td>\r\n');
			document.write('</tr>\r\n');
			document.write('</table>\r\n');
        }
        else
        {
        	document.write('</td>');
            document.write('<td class="glowBoxRight glowBoxMidRight"></td>\r\n');
            document.write('</tr>\r\n');
            document.write('<tr>\r\n');
            document.write('<td class="glowBoxFooter glowBoxLeft glowBoxFooterLeft"></td>\r\n');
            document.write('<td class="glowBoxFooter glowBoxFooterMid"></td>\r\n');
            document.write('<td class="glowBoxFooter glowBoxRight glowBoxFooterRight"></td>\r\n');
			document.write('</tr>\r\n');
			document.write('</table>\r\n');
        }
}

function documentWriteActionPane()
{
	if (suitable_browser_to_use_png == true)
		{
			document.write('<div class="actionPanePng">\r\n');
		}
		else
		{
			document.write('<div class="actionPane">\r\n');
		}
}

function DialogueBodyTop()
{
	CreateMainTable();
	AddHeaderAndBarForCitrix();
	document.writeln('<tr class="mainPane">');
	document.writeln('<td class="carbonBoxBottom" valign="bottom">');
	documentWriteGlowBoxUpper();
	document.writeln('<table cellspacing="4" cellpadding="0" border="0" width=100%>');
	document.writeln('<tr><td class="CTX_ContentTitleHeader"><div id="dialogueHeader"></div></td></tr>');
	document.writeln('<tr><td class="CTXMSAM_LogonFont"><div id="dialogueInfo"></div></td></tr>');
	document.writeln('<tr><td valign="top"><div id=content>');
}

function DialogueBodyBottom()
{
	document.writeln('</div></td></tr></table>');
	documentWriteGlowBoxLower();
	document.writeln('</td></tr>');
	AddFooter();
	document.writeln('</table>');

	//change maxLength for new password field to 127, to be compatible with LDAP
	var dlgStr = document.getElementById("dialogueStr").innerHTML;
	dlgStr = dlgStr.toLowerCase();
	if ((dlgStr.indexOf("password expired") > -1) && (dlgStr.indexOf("new password") > -1)) {
		document.getElementById("response").maxLength = 127;
		var localizedStr = _("DIALOGUE_HTML::dialoguePasswordChange");
		if (localizedStr && localizedStr.length > 0) {
			document.getElementById("dialogueStr").innerHTML = localizedStr;
		}
	}

	if (dlgStr.indexOf("confirm password") > -1) {
		document.getElementById("response").maxLength = 127;
		var localizedStr = _("DIALOGUE_HTML::dialogueConfirmPassword");
		if (localizedStr && localizedStr.length > 0) {
			document.getElementById("dialogueStr").innerHTML = localizedStr;
		}
	}

}

function DialogInclude()
{
	document.writeln('<LINK href="/vpn/images/caxtonstyle.css" rel="stylesheet" type="text/css"');
}

function DialogueBodyI()
{
	CreateMainTable();
	AddHeaderAndBarForCitrix();
	document.writeln('<tr class="mainPane">');
	document.writeln('<td class="carbonBoxBottom" valign="bottom">');
	documentWriteGlowBoxUpper();
	document.writeln('<table cellspacing="4" cellpadding="0" border="0" width=100%>');
	document.writeln('<tr><td class="CTX_ContentTitleHeader" style="float:left"><div id="dialogueHeader"></div></td></tr>');
	document.writeln('<tr><td class="CTXMSAM_LogonFont"><div id="dialogueInfo" style="float:left"></div></td></tr>');
	document.writeln('<tr><td valign="top"><div id=content>');
	
	document.writeln('<FORM class="dialogueForm" METHOD=POST ACTION="/cgi/dlge" NAME="dlgform">');
	document.writeln('<table id="dialogueTable" class="CTXMSAM_LogonFont">');
	document.writeln('<tr><td colspan=2>&nbsp;</td></tr>');
	document.writeln('<tr><td class="dialogueChallengeCell">');
}

function DialogueBodyII()
{
	document.writeln('</td>');
	document.writeln('<td class="dialogueResponseCell"><input size="35" maxlength="256" id="response" NAME=response TYPE=password tabindex="1"/></td></tr>');
	document.writeln('<tr><td colspan=2></td></tr>');
	document.writeln('<tr><td colspan=2 class="dialogueSubmitCell">');
	document.writeln('<input id="SubmitButton" type="SUBMIT" value="Submit" tabindex="2" class="CTX_BlackButton" onMouseOver="this.className=\'CTX_BlackButton_Hover\';" onMouseOut="this.className=\'CTX_BlackButton\';"/>');
	document.writeln('</td></tr></table>');
	document.writeln('</FORM>');
	document.writeln('</div></td></tr></table>');
	documentWriteGlowBoxLower();
	document.writeln('</td></tr>');
	AddFooter();
	document.writeln('</table>');

	//change maxLength for new password field to 127, to be compatible with LDAP
	var dlgStr = document.getElementById("dialogueStr").innerHTML;
	dlgStr = dlgStr.toLowerCase();
	if ((dlgStr.indexOf("password expired") > -1) && (dlgStr.indexOf("new password") > -1)) {
		document.getElementById("response").maxLength = 127;
		var localizedStr = _("DIALOGUE_HTML::dialoguePasswordChange");
		if (localizedStr && localizedStr.length > 0) {
			document.getElementById("dialogueStr").innerHTML = localizedStr;
		}
	}

	if (dlgStr.indexOf("confirm password") > -1) {
		document.getElementById("response").maxLength = 127;
		var localizedStr = _("DIALOGUE_HTML::dialogueConfirmPassword");
		if (localizedStr && localizedStr.length > 0) {
			document.getElementById("dialogueStr").innerHTML = localizedStr;
		}
	}

}
 function TransferInclude()
{
document.writeln('<LINK href="/vpn/images/caxtonstyle.css" rel="stylesheet" type="text/css"');
}

function TransferOnesessBodyI()
{

document.writeln('<table class="full_width_height" cellspacing=0 cellpadding=0>');
document.writeln('<div id="header">');
document.writeln('<tr><td class="full_width">');
document.writeln('<table class="full_width" cellspacing=0 cellpadding=0><tr>');
document.writeln('<td class="header_left">&nbsp;</td>');
document.writeln('<td class="header_middle">&nbsp;</td>');
document.writeln('</tr><tr>');
document.writeln('<td colspan=2 class="navbar">&nbsp;</td>');
document.writeln('</tr></table></td></tr></div>');
document.writeln('<div id="contents">');
document.writeln('<tr class="full_width_height"><td><table class="mainpane full_width_height"><tr><td align="center">');
document.writeln('<table class="CTXMSAM_LogonFont" ><tr id="errorMessageRow"> <td class="glowBoxLeft">&nbsp;</td>');
document.writeln('<td class="loginTableMidWidth"><div id="content" class="feedbackStyleWarning ">');
document.writeln('<div id="heading" class="CTX_ContentTitleHeader">Transfer Logon</div>');
document.writeln('<div id="description" class="messageStyle">');
document.writeln('<BR><span id="You are currently logged on to the Access Gateway on another device."></span>');
document.writeln('<BR><span id="Would you like to end that session?"></span><BR></div>');
document.writeln('<form class="dialogueForm" action="/cgi/tlogin" method="POST">');
document.writeln('<table>');
}

function TransferMultsessBodyI()
{
document.writeln('<table class="full_width_height" cellspacing=0 cellpadding=0>');
document.writeln('<div id="header">');
document.writeln('<tr><td valign="top" class="full_width">');
document.writeln('<table class="full_width" cellspacing=0 cellpadding=0>');
document.writeln('<tr><td class="header_left">&nbsp;</td>');
document.writeln('<tr><td class="header_left">&nbsp;</td>');
document.writeln('<td class="header_middle">&nbsp;</td>');
document.writeln('</tr><tr><td colspan=2 class="navbar">&nbsp;</td></tr></table>');
document.writeln('</td></tr></div>');
document.writeln('<div id="contents">');
document.writeln('<tr class="full_width_height">');
document.writeln('<td><table class="mainpane full_width_height">');
document.writeln('<tr><td align="center">');
document.writeln('<table class="CTXMSAM_LogonFont" >');
document.writeln('<tr id="errorMessageRow">');
document.writeln('<td class="glowBoxLeft">&nbsp;</td>');
document.writeln('<td class="loginTableMidWidth">');
document.writeln('<div id="content" class="feedbackStyleWarning ">');
document.writeln('<div id="heading" class="CTX_ContentTitleHeader">Transfer Logon</div>');
document.writeln('<div id="description" class="messageStyle">');
document.writeln('<BR><span id="You have reached the limit of the allowed Access Gateway sessions."></span>');
document.writeln('<BR><span id="Please select which session to release in order to continue with this session."></span><BR><BR></div>');
document.writeln('<form class="dialogueForm" action="/cgi/tlogin" method="POST">');
document.writeln('<table class="CTXMSAM_LogonFont">');
document.writeln('<tr><th></th><th><span id="Intranet IP Address"></span>&nbsp;&nbsp;</th><tab><th><span id="Idle Time"></span></th></tr>');
}


function TransferBodyII()
{

document.writeln('<tr><td colspan=3><BR></td></tr></table>');
document.writeln('<div class="transferLogonButtonRow">');
document.writeln('<input type="submit" id="TransferButton" value="Transfer" name="cm" class="CTX_BlackButton" onMouseOver="this.className=\'CTX_BlackButton_Hover\';" onMouseOut="this.className=\'CTX_BlackButton\';"/>');
document.writeln('<input type="submit" id="CancelButton" value="Cancel" name="cm"class="CTX_BlackButton" onMouseOver="this.className=\'CTX_BlackButton_Hover\';" onMouseOut="this.className=\'CTX_BlackButton\';"/>');
document.writeln('</div></form></div></td>');                           
document.writeln('<td class="glowBoxRight">&nbsp;</td>');
document.writeln('</tr></table></td></tr></table></td></tr></div>');
document.writeln('<div id="footer">');
document.writeln('<tr><td class="watermark"></td></tr>');
document.writeln('</div></table>');
}

/* --------------  Helper functions start -------------------- */

var util = { }		//Generic Util namespace

util.win = {}		// This namespace should be used for all Windows only util functions


//use this function instead IE check
//Even if ActiveXObject is defined, IE 11 reports "typeof ActiveXObject" as undefined. So, don't use typeof operator for this check
util.win.ACTIVEX_SUPPORTED = ("ActiveXObject" in window);		


/* --------------  Helper functions end -------------------- */
