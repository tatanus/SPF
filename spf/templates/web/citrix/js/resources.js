// ResourceManager Class
function ResourceManager(Resource_Base, Partition)
{
  //------------------------------
  // Constants
  //------------------------------

  // Extension for XML files
  this.XML_ext = '.xml';
  
  // Base name for Configuration file
  this.Config_base = 'config';
  
  //------------------------------
  // Member Variables
  //------------------------------

  // Configuration XML Document
  // Format of Configuration XML: <ResourceManager><SupportedLanguageList><Language>en</Language><Language>de</Language>...</SupportedLanguageList></ResourceManager>
  this.ConfigXML = null;

  // List of Supported Languages (Countries) for localization in lowercase letters
  // The first-matched language in [1] .. [length - 1] is selected.
  // Otherwise, the first language, i.e., [0] is selected as the default one.
  this.SupportedLanguageList = null;

  this.PreferredLanguage = null;

  // Base Path for resource files
  // {lang} is replaced with a language code or a language code with a country code
  // .xml is appended to the base path
  // Example: "./resources_{lang}" is translated to "./resources_ja.xml" in Japanese environment
  this.Resource_Base = Resource_Base;

  // Resource XML Document
  this.ResourceXML = null;

  // Target Partition Name
  // Partition Names are specified by <Resources><Partition id="PartitionName"><String>...</Partition><Partition id="...">...</Resources>
  this.Partition = Partition;
  
  //------------------------------
  // Methods  
  //------------------------------

  // Configure()
  // Set up the SupportedLanguageList
  // this.ConfigXML must be loaded beforehand
  this.Configure = function()
  {
    if (this.ConfigXML != null)
    {
      // load from the ConfigXML
      var i, j;
      var languages = null;
      var nodes = null;
      var xpath = "//ResourceManager/SupportedLanguageList[@id = '']"; // to avoid the CVPN url rewriting
      xpath = xpath.replace("[@id = '']", "");
      if (navigator.appName != "Netscape")
      {
        // Internet Explorer
        languages = this.ConfigXML.selectSingleNode(xpath);
        if (languages != null)
        {
          nodes = languages.childNodes;
        }
      }
      else
      {
        try 
        {
          // Firefox
          var result = this.ConfigXML.evaluate(xpath, this.ConfigXML, null, XPathResult.ANY_TYPE, null);
          if (result != null && result.resultType == 4)
          {
            languages = result.iterateNext();
            nodes = languages.childNodes;
          }
        } 
        catch (ex) 
        {
          // Android 2.x without XPath
          var result = this.ConfigXML.getElementsByTagName("SupportedLanguageList");
          if (result != null && result.length >= 1)
          {
            languages = result[0];
            nodes = languages.childNodes;
          }
        }
      }
      this.SupportedLanguageList = []; 
      if (nodes == null)
        this.SupportedLanguageList = ["en"];
      else
      for (i = 0; i < nodes.length; i++)
      {
        if (nodes[i].nodeName == "#text")
        {
          continue; // skip whitespaces between nodes
        }
        var _Type, _LangId;
        _Type = nodes[i].nodeName;
        _LangId = null;
        if (navigator.appName != "Netscape")
        {
          _LangId = nodes[i].text; // Internet Explorer
        }
        else
        {
          _LangId = nodes[i].firstChild.nodeValue; // Firefox
        }
        switch (_Type)
        {
        case "Language":
          this.SupportedLanguageList.push(_LangId);
          break;
        default:
          break;
        }
      }
    }
    else
    {
      this.SupportedLanguageList = ["en"];
    }
  }

  // Language(isDefault)  
  // Figure out the target language for localization
  this.Language = function(isDefault)
  {
    var _LANG;
    var LANG_Found = false;
    var i;

    if (isDefault)
    {
      return this.SupportedLanguageList[0];
    }

    if (this.PreferredLanguage != null)
    {
      _LANG = this.PreferredLanguage;
      for (i = 1; i < this.SupportedLanguageList.length; i++)
      {
        if (_LANG.toLowerCase().indexOf(this.SupportedLanguageList[i]) == 0)
        {
          LANG_Found = true;
          _LANG = this.SupportedLanguageList[i];
          break;
        }
      }
      if (!LANG_Found)
      {
        if (_LANG.toLowerCase().indexOf(this.SupportedLanguageList[0]) == 0)
        {
          LANG_Found = true;
          _LANG = this.SupportedLanguageList[0];
        }
      }
    }

    if (!LANG_Found)
    {
      if (navigator.appName == 'Netscape')
      {
        _LANG = navigator.language;
        if (navigator.userAgent.indexOf("Android") > 0)
        {
          var androidUA = /^Mozilla.*Android [.0-9]*; ([a-zA-Z-]*);.*$/;
          var result = navigator.userAgent.match(androidUA);
          if (result != null && result.length > 1)
          {
            _LANG = result[1];
          } 
        }
      }
      else
      {
        if (navigator.browserLanguage.toLowerCase().indexOf(this.SupportedLanguageList[0]) == 0)
        {
          _LANG = navigator.userLanguage;
        }
        else
        {
          _LANG = navigator.browserLanguage;
        }
      }

      for (i = 1; i < this.SupportedLanguageList.length; i++)
      {
        if (_LANG.toLowerCase().indexOf(this.SupportedLanguageList[i]) == 0)
        {
          LANG_Found = true;
          _LANG = this.SupportedLanguageList[i];
          break;
        }
      }
    }

    if (!LANG_Found)
    {
      _LANG = this.SupportedLanguageList[0];
    }

    return _LANG;
  }

  // ConfigURL()
  // Figure out the URL for the Configuration file
  this.ConfigURL = function()
  {
    var url = new String(this.Resource_Base + this.XML_ext);
    return url.replace(/{lang}/, this.Config_base);
  }

  // ResourceURL()
  // Figure out the URL for the XML resource file of the selected language
  this.ResourceURL = function(isDefault)
  {
    var url = new String(this.Resource_Base + this.XML_ext);
    return url.replace(/{lang}/, this.Language(isDefault));
  }
  
  // GetXMLHttpRequest()
  // Get an XMLHttpRequest object
  this.GetXMLHttpRequest = function()
  {
    if (navigator.appName == 'Netscape' && window.XMLHttpRequest) {
      return new XMLHttpRequest();
    } else if (window.ActiveXObject) {
      try {
        return new ActiveXObject("Msxml2.XMLHTTP");
      } catch (ex1) {
        try {
          return new ActiveXObject("Microsoft.XMLHTTP");
        } catch (ex2) {
          return null;
        }
      }
    } else {
      return null;
    }
  }

  // ImportXML(url, isConfig)
  // Obtain resource XML or Configuration XML
  this.ImportXML = function(url, isConfig)
  {
    var request = this.GetXMLHttpRequest();
    if (request == null)
    {
      return false;
    }
    request.open("GET", url, false);
    request.send("");
    if (request.status == 200)
    {
      if (isConfig)
      {
        this.ConfigXML = request.responseXML;
        try
        {
          this.ConfigXML.setProperty("SelectionLanguage", "XPath"); // Internet Explorer
        }
        catch (e) { }
      }
      else
      {
        this.ResourceXML = request.responseXML;
        try
        {
          this.ResourceXML.setProperty("SelectionLanguage", "XPath"); // Internet Explorer
        }
        catch (e) { }
      }
      return true;
    }
    return false;
  }

  // Load()
  // Obtain and Load language-specific resources from XML
  this.Load = function()
  {
    var starttime = new Date();
    if (this.ConfigXML == null)
    {
      this.ImportXML(this.ConfigURL(), true); // configuration
      this.Configure();
    }
    if (this.ResourceXML == null)
    {
      this.ImportXML(this.ResourceURL(false), false); // localized resources
    }
    if (this.ResourceXML == null)
    {
      this.ImportXML(this.ResourceURL(true), false); // default resources
    }
    if (this.ResourceXML != null)
    {
      this.Hide();
      var i, j;
      var xml = this.ResourceXML;
      var partition;
      var nodes = null;
      var xpath = "//Resources/Partition[@id = '" + this.Partition + "']";
      if (navigator.appName != "Netscape")
      {
        // Internet Explorer
        partition = this.ResourceXML.selectSingleNode(xpath);
        if (partition != null)
        {
          nodes = partition.childNodes;
        }
      }
      else
      {
        try
        {
          // Firefox
          var result = this.ResourceXML.evaluate(xpath, this.ResourceXML, null, XPathResult.ANY_TYPE, null);
          if (result != null && result.resultType == 4)
          {
            partition = result.iterateNext();
            nodes = partition.childNodes;
          }
        }
        catch (ex)
        {
          // Android 2.x without XPath
          var result = this.ResourceXML.getElementsByTagName("Partition");
          if (result != null && result.length >= 1)
          {
            for (i = 0; i < result.length; i++)
            {
              if (result[i].getAttribute("id") == this.Partition)
              {
                partition = result[i];
                nodes = partition.childNodes;
                break;
              } 
            }
          }
        }
      }
      for (i = 0; i < nodes.length; i++)
      {
        if (nodes[i].nodeName == "#text")
        {
          continue; // skip whitespaces between nodes
        }
        var attr = nodes[i].attributes;
        var _Type, _Id, _Property, _Tag, _Value, _Url;
        _Type = nodes[i].nodeName;
        _Id = _Property = _Tag = _Value = _Url = null;
        for (j = 0; j < attr.length; j++)
        {
          switch (attr[j].nodeName)
          {
          case "id":
            _Id = attr[j].nodeValue;
            break;
          case "property":
            _Property = attr[j].nodeValue;
            break;
          case "tag":
            _Tag = attr[j].nodeValue;
            break;
          case "url":
            _Url = attr[j].nodeValue;
            break;
          default:
            break;
          } 
        }
        if (navigator.appName != "Netscape")
        {
          _Value = nodes[i].text; // Internet Explorer
        }
        else
        {
          _Value = nodes[i].firstChild.nodeValue; // Firefox
        }
        switch (_Type)
        {
        case "Property":
          this.LoadProperty(_Id, _Property, _Value);
          break;
        case "String":
          this.LoadString(_Id, _Value);
          break;
        case "Style":
          this.LoadStyle(_Id, _Property, _Value);
          break;
        case "ClassStyle":
          this.LoadClassStyle(_Id, _Property, _Value);
          break;
        case "TagProperty":
          this.LoadTagProperty(_Tag, _Property, _Value);
          break;
        case "Title":
          this.LoadTitle(_Value, _Url);
          break;
        default:
          break;
        }
      }
      var endtime = new Date();
      this.Show();
    }
  }

  // GetRuleByClass(Id)
  this.GetRuleByClass = function(Id)
  {
    var i, j;
    var ss = document.styleSheets;
    var rules;
    for (i = 0; i < ss.length; i++)
    {
      rules = ss[0].rules ? ss[i].rules : ss[i].cssRules; 
      for (j = 0; j < rules.length; j++)
      {
        if (rules[j].selectorText.toLowerCase() == Id.toLowerCase())
        {
          return rules[j];
        }
      }
    }
    return null;
  }

  // LoadProperty(Id, Property, Val)
  this.LoadProperty = function(Id, Property, Val)
  {
    var element = document.getElementById(Id);
    if (element)
    {
      if (Val.indexOf('function') == 0)
      {
        eval("element[Property] = " + Val);
      }
      else
      {
        element[Property] = Val;
      }
    }
  }
  
  // LoadString(Id, Val)
  this.LoadString = function(Id, Val)
  {
    var element = document.getElementById(Id);
    if (element)
    {
      element["innerHTML"] = Val;
    }
  }

  // LoadStyle(Id, Style, Val)
  this.LoadStyle = function(Id, Property, Val)
  {
    var element = document.getElementById(Id);
    if (element)
    {
      element.style[Property] = Val;
    }
  }

  // LoadClassStyle(Id, Style, Val)
  this.LoadClassStyle = function(Id, Property, Val)
  {
    var rule = this.GetRuleByClass(Id);
    if (rule)
    {
      rule.style[Property] = Val;
    }
  }

  // LoadTagProperty(Tag, Property, Val)
  this.LoadTagProperty = function(Tag, Property, Val)
  {
    var elements = document.getElementsByTagName(Tag);
    if (elements && elements[0])
    {
      elements[0][Property] = Val;
    }
  }
  
  // LoadTitle(Val)
  // LoadTitle(Val, Url)
  this.LoadTitle = function(Val, Url)
  {
    if (Url == null || Url.length == 0 || document.location.href.match(Url))
    {
      this.LoadTagProperty("title", "text", Val);
      document.title = Val;
    }
  }

  // GetString(id)
  // Get resource string with the specified id
  // id = "Id" or "Partition::Id"
  this.GetString = function(id)
  {
    var partition = this.Partition;
    var delimiter = id.indexOf("::");
    if (delimiter > 0)
    {
      partition = id.substring(0, delimiter);
      id = id.substring(delimiter + 2);
    }
    return this.GetPartitionString(id, partition);
  }
  
  // GetPartitionString(id, partition)
  // Get resource string with the specified id in the specified partition
  this.GetPartitionString = function(id, partition)
  {
    var _Value = "";
    if (this.ConfigXML == null)
    {
      this.ImportXML(this.ConfigURL(), true); // configuration
      this.Configure();
    }
    if (this.ResourceXML == null)
    {
      this.ImportXML(this.ResourceURL(false), false); // localized resources
    }
    if (this.ResourceXML == null)
    {
      this.ImportXML(this.ResourceURL(true), false);  // default resources
    }
    if (this.ResourceXML != null)
    {
      var xpath = "//Resources/Partition[@id = '" + partition + "']/String[@id = '" + id + "']";
      if (navigator.appName != "Netscape")
      {
        // Internet Explorer
        var node = this.ResourceXML.selectSingleNode(xpath);
        if (node != null)
        {
          _Value = node.text;
        }
      }
      else
      {
        try
        {
          // Firefox
          var result = this.ResourceXML.evaluate(xpath, this.ResourceXML, null, XPathResult.STRING_TYPE, null);
          if (result != null && result.stringValue != null)
          {
            _Value = result.stringValue;
          }
        }
        catch (ex)
        {
          // Android 2.x without XPath
          var result = this.ResourceXML.getElementsByTagName("Partition");
          if (result != null && result.length >= 1)
          {
            for (i = 0; i < result.length; i++)
            {
              if (result[i].getAttribute("id") == this.Partition)
              {
                partition = result[i];
                nodes = partition.childNodes;
                break;
              } 
            }
          }
          if (partition != null)
          {
            nodes = partition.childNodes;
            if (nodes != null && nodes.length >= 1)
            {
              for (i = 0; i < nodes.length; i++)
              {
                if (nodes[i].nodeName == "#text")
                {
                  continue; // skip whitespaces between nodes
                }
                if (nodes[i].getAttribute("id") == id)
                {
                  _Value = nodes[i].firstChild.data;
                  break;
                } 
              }
            } 
          }
        }
      }
    }
    return _Value;
  }
  
  // FormatShortDate(year, month, day)
  // Get the localized short date string
  this.FormatShortDate = function(year, month, day)
  {
    var yyyy = "" + year;
    var M = "" + month;
    var MM = "0" + month; MM = MM.substring(MM.length - 2);
    var d = "" + day;
    var dd = "0" + day; dd = dd.substring(dd.length - 2);
    var format = this.GetString('locale::ShortDateFormat');
    format = format.replace("yyyy", yyyy);
    format = format.replace("MM", MM);
    format = format.replace("M", M);
    format = format.replace("dd", dd);
    format = format.replace("d", d);
    return format;
  }

  // FormatShortTime(hour, minute)
  // Get the localized short time string
  this.FormatShortTime = function(hour, minute)
  {
    var H = "" + hour;
    var HH = "0" + hour; HH = HH.substring(HH.length - 2);
    var m = "" + minute;
    var mm = "0" + minute; mm = mm.substring(mm.length - 2);
    var format = this.GetString('locale::ShortTimeFormat');
    format = format.replace("HH", HH);
    format = format.replace("H", H);
    format = format.replace("mm", mm);
    format = format.replace("m", m);
    return format;
  }

  // Show()
  // Show the localized document body
  this.Show = function()
  {
    try
    {
      document.getElementsByTagName("body")[0].style["visibility"] = "visible";
    } 
    catch (e) {}
  }

  // Hide()
  // Hide the document body
  this.Hide = function()
  {
    try
    {
      document.getElementsByTagName("body")[0].style["visibility"] = "hidden";
    } 
    catch (e) {}
  }
}

// _(id)
// Shortcut function for String resources
// This funtion assumes that the instance name of the ResourceManager object is "Resources"
function _(id)
{
  return Resources.GetString(id);
}
