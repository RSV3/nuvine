/* @license
 * MyFonts Webfont Build ID 2349197, 2012-08-23T21:18:09-0400
 * 
 * The fonts listed in this notice are subject to the End User License
 * Agreement(s) entered into by the website owner. All other parties are 
 * explicitly restricted from using the Licensed Webfonts(s).
 * 
 * You may obtain a valid license at the URLs below.
 * 
 * Webfont: Museo Sans 700 by exljbris
 * URL: http://www.myfonts.com/fonts/exljbris/museo-sans/700/
 * Licensed pageviews: 10,000
 * 
 * Webfont: Museo Sans 300 by exljbris
 * URL: http://www.myfonts.com/fonts/exljbris/museo-sans/300/
 * Licensed pageviews: unspecified
 * 
 * Webfont: Museo Sans 900 Italic by exljbris
 * URL: http://www.myfonts.com/fonts/exljbris/museo-sans/900-italic/
 * Licensed pageviews: unspecified
 * 
 * Webfont: Museo Sans 500 by exljbris
 * URL: http://www.myfonts.com/fonts/exljbris/museo-sans/500/
 * Licensed pageviews: unspecified
 * 
 * Webfont: Museo Sans 100 by exljbris
 * URL: http://www.myfonts.com/fonts/exljbris/museo-sans/100/
 * Licensed pageviews: unspecified
 * 
 * Webfont: Museo Sans 700 Italic by exljbris
 * URL: http://www.myfonts.com/fonts/exljbris/museo-sans/700-italic/
 * Licensed pageviews: unspecified
 * 
 * Webfont: Museo Sans 300 Italic by exljbris
 * URL: http://www.myfonts.com/fonts/exljbris/museo-sans/300-italic/
 * Licensed pageviews: unspecified
 * 
 * Webfont: Museo Sans 100 Italic by exljbris
 * URL: http://www.myfonts.com/fonts/exljbris/museo-sans/100-italic/
 * Licensed pageviews: unspecified
 * 
 * Webfont: Museo Sans 500 Italic by exljbris
 * URL: http://www.myfonts.com/fonts/exljbris/museo-sans/500-italic/
 * Licensed pageviews: unspecified
 * 
 * Webfont: Museo Sans 900 by exljbris
 * URL: http://www.myfonts.com/fonts/exljbris/museo-sans/900/
 * Licensed pageviews: unspecified
 * 
 * 
 * License: http://www.myfonts.com/viewlicense?type=web&buildid=2349197
 * Webfonts copyright: Copyright (c) 2008 by Jos Buivenga. All rights reserved.
 * 
 * © 2012 Bitstream Inc
*/


// safari 3.1: ttf
// safari 5.1: woff
// firefox 3.6+: woff
// firefox 3.5+: ttf
// chrome 4+: ttf
// chrome 6+: woff
// IE 5+: eot
// IE 9: woff
// opera 10.1+: ttf
// mobile safari 4.2+: ttf
// mobile safari: svg
// android: ttf

var browserName, browserVersion, webfontType;
 
if (typeof(customPath) == 'undefined')
	var customPath = false;


if (typeof(woffEnabled) == 'undefined')
	var woffEnabled = true;


if (/myfonts_test=on/.test(window.location.search))
	var myfonts_webfont_test = true;

else if (typeof(myfonts_webfont_test) == 'undefined')
	var myfonts_webfont_test = false;


if (customPath)
	var path = customPath;

else
{
	var scripts = document.getElementsByTagName("SCRIPT");
	var script = scripts[scripts.length-1].src;

	if (!script.match("://") && script.charAt(0) != '/')
		script = "./"+script;
		
	var path = script.replace(/\\/g,'/').replace(/\/[^\/]*\/?$/, '');
}


var wfpath = path + "/webfonts/";


if (myfonts_webfont_test)
	document.write('<script type="text/javascript" src="' + path + '/MyFontsWebfontsOrderM3985193_test.js"></script>');


var haveWOFF = 1;
var haveTTF = 1;

if (/(Macintosh|Android)/.test(navigator.userAgent))
	var suffix = "_unhinted";
		
else
	var suffix = "";


if (/webfont=(woff|ttf|eot)/.test(window.location.search))
	webfontType = RegExp.$1;

else if (/MSIE (\d+\.\d+)/.test(navigator.userAgent))
{
	browserName = 'MSIE';
	browserVersion = new Number(RegExp.$1);
	if (haveWOFF && browserVersion >= 9.0 && woffEnabled)
		webfontType = 'woff';
	else if (browserVersion >= 5.0)
		webfontType = 'eot';
}
else if (/Firefox[\/\s](\d+\.\d+)/.test(navigator.userAgent))
{
	browserName = 'Firefox';
	browserVersion = new Number(RegExp.$1);
	if (haveWOFF && browserVersion >= 3.6 && woffEnabled)
		webfontType = 'woff';
	else if (browserVersion >= 3.5)
		webfontType = 'ttf';
}
else if (/Chrome\/(\d+\.\d+)/.test(navigator.userAgent)) // must check before safari
{
	browserName = 'Chrome';
	browserVersion = new Number(RegExp.$1);

	if (haveWOFF && browserVersion >= 6.0 && woffEnabled)
		webfontType = 'woff';

	else if (browserVersion >= 4.0)
		webfontType = 'ttf';
		
}
else if (/Mozilla.*(iPhone|iPad).* OS (\d+)_(\d+).* AppleWebKit.*Safari/.test(navigator.userAgent))
{
	browserName = 'MobileSafari';
	browserVersion = new Number(RegExp.$2) + (new Number(RegExp.$3) / 10)
	suffix = "_unhinted";
	
	if(browserVersion >= 4.2 && (haveTTF || haveData))
		webfontType = 'ttf';

	else
		webfontType = 'svg';
}
else if (/Mozilla.*(iPhone|iPad|BlackBerry).*AppleWebKit.*Safari/.test(navigator.userAgent))
{
	browserName = 'MobileSafari';
	webfontType = 'svg';
}
else if (/Safari\/(\d+\.\d+)/.test(navigator.userAgent))
{
	browserName = 'Safari';
	if (/Version\/(\d+\.\d+)/.test(navigator.userAgent))
	{
		browserVersion = new Number(RegExp.$1);
		if (browserVersion >= 5.1 && haveWOFF)
			webfontType = 'woff';
		else if (browserVersion >= 3.1)
			webfontType = 'ttf';
	}
}
else if (/Opera\/(\d+\.\d+)/.test(navigator.userAgent))
{
	browserName = 'Opera';
	if (/Version\/(\d+\.\d+)/.test(navigator.userAgent))
	{
		browserVersion = new Number(RegExp.$1);
		
		if (haveWOFF && browserVersion >= 11.1 && woffEnabled)
			webfontType = 'woff';
		else if (browserVersion >= 10.1)
			webfontType = 'ttf';
	}
}

switch (webfontType)
{
		case 'eot':
				document.write("<style>\n");
							document.write("@font-face{font-family: 'MuseoSans-700';src:url(\"" + wfpath + "84f4accde16a9b43b393430c0969d582_0.eot\");font-weight:'normal';font-style:'normal';}\n");
									document.write("@font-face{font-family: 'MuseoSans-300';src:url(\"" + wfpath + "f718fc4be517f6d730d161a18b818a7c_0.eot\");font-weight:'normal';font-style:'normal';}\n");
									document.write("@font-face{font-family: 'MuseoSans-900Italic';src:url(\"" + wfpath + "fe5423314a7bdf7b9969db9f51498ecc_0.eot\");font-weight:'normal';font-style:'normal';}\n");
									document.write("@font-face{font-family: 'MuseoSans-500';src:url(\"" + wfpath + "a5b490f9656ece5eb14310d119d82506_0.eot\");font-weight:'normal';font-style:'normal';}\n");
									document.write("@font-face{font-family: 'MuseoSans-100';src:url(\"" + wfpath + "ba54c38c1151aaec1f220f1ffbab562e_0.eot\");font-weight:'normal';font-style:'normal';}\n");
									document.write("@font-face{font-family: 'MuseoSans-700Italic';src:url(\"" + wfpath + "17731ee6c73c6528f6fe1d1ba76bc65c_0.eot\");font-weight:'normal';font-style:'normal';}\n");
									document.write("@font-face{font-family: 'MuseoSans-300Italic';src:url(\"" + wfpath + "14b2b66f68d2c5b0fc7ff95d82761a0a_0.eot\");font-weight:'normal';font-style:'normal';}\n");
									document.write("@font-face{font-family: 'MuseoSans-100Italic';src:url(\"" + wfpath + "3dd8b405fc8d6ef66c1e59953998cfe4_0.eot\");font-weight:'normal';font-style:'normal';}\n");
									document.write("@font-face{font-family: 'MuseoSans-500Italic';src:url(\"" + wfpath + "53d8cb2065b41de82faf78ac5b6d87a2_0.eot\");font-weight:'normal';font-style:'normal';}\n");
									document.write("@font-face{font-family: 'MuseoSans-900';src:url(\"" + wfpath + "9a2da39252f62962c7ad4a5b6ccc3166_0.eot\");font-weight:'normal';font-style:'normal';}\n");
						document.write("</style>");
		break;
		
		case 'woff':
				document.write("<style>\n");
							document.write("@font-face{font-family: 'MuseoSans-700';src:url(\"" + wfpath + "84f4accde16a9b43b393430c0969d582" + suffix + "_0.woff\") format(\"woff\");font-weight:'normal';font-style:'normal';}\n");
									document.write("@font-face{font-family: 'MuseoSans-300';src:url(\"" + wfpath + "f718fc4be517f6d730d161a18b818a7c" + suffix + "_0.woff\") format(\"woff\");font-weight:'normal';font-style:'normal';}\n");
									document.write("@font-face{font-family: 'MuseoSans-900Italic';src:url(\"" + wfpath + "fe5423314a7bdf7b9969db9f51498ecc" + suffix + "_0.woff\") format(\"woff\");font-weight:'normal';font-style:'normal';}\n");
									document.write("@font-face{font-family: 'MuseoSans-500';src:url(\"" + wfpath + "a5b490f9656ece5eb14310d119d82506" + suffix + "_0.woff\") format(\"woff\");font-weight:'normal';font-style:'normal';}\n");
									document.write("@font-face{font-family: 'MuseoSans-100';src:url(\"" + wfpath + "ba54c38c1151aaec1f220f1ffbab562e" + suffix + "_0.woff\") format(\"woff\");font-weight:'normal';font-style:'normal';}\n");
									document.write("@font-face{font-family: 'MuseoSans-700Italic';src:url(\"" + wfpath + "17731ee6c73c6528f6fe1d1ba76bc65c" + suffix + "_0.woff\") format(\"woff\");font-weight:'normal';font-style:'normal';}\n");
									document.write("@font-face{font-family: 'MuseoSans-300Italic';src:url(\"" + wfpath + "14b2b66f68d2c5b0fc7ff95d82761a0a" + suffix + "_0.woff\") format(\"woff\");font-weight:'normal';font-style:'normal';}\n");
									document.write("@font-face{font-family: 'MuseoSans-100Italic';src:url(\"" + wfpath + "3dd8b405fc8d6ef66c1e59953998cfe4" + suffix + "_0.woff\") format(\"woff\");font-weight:'normal';font-style:'normal';}\n");
									document.write("@font-face{font-family: 'MuseoSans-500Italic';src:url(\"" + wfpath + "53d8cb2065b41de82faf78ac5b6d87a2" + suffix + "_0.woff\") format(\"woff\");font-weight:'normal';font-style:'normal';}\n");
									document.write("@font-face{font-family: 'MuseoSans-900';src:url(\"" + wfpath + "9a2da39252f62962c7ad4a5b6ccc3166" + suffix + "_0.woff\") format(\"woff\");font-weight:'normal';font-style:'normal';}\n");
						document.write("</style>");
		break;
	
		case 'ttf':
				document.write("<style>\n");
							document.write("@font-face{font-family: 'MuseoSans-700';src:url(\"" + wfpath + "84f4accde16a9b43b393430c0969d582" + suffix + "_0.ttf\");font-weight:'normal';font-style:'normal';}\n");
									document.write("@font-face{font-family: 'MuseoSans-300';src:url(\"" + wfpath + "f718fc4be517f6d730d161a18b818a7c" + suffix + "_0.ttf\");font-weight:'normal';font-style:'normal';}\n");
									document.write("@font-face{font-family: 'MuseoSans-900Italic';src:url(\"" + wfpath + "fe5423314a7bdf7b9969db9f51498ecc" + suffix + "_0.ttf\");font-weight:'normal';font-style:'normal';}\n");
									document.write("@font-face{font-family: 'MuseoSans-500';src:url(\"" + wfpath + "a5b490f9656ece5eb14310d119d82506" + suffix + "_0.ttf\");font-weight:'normal';font-style:'normal';}\n");
									document.write("@font-face{font-family: 'MuseoSans-100';src:url(\"" + wfpath + "ba54c38c1151aaec1f220f1ffbab562e" + suffix + "_0.ttf\");font-weight:'normal';font-style:'normal';}\n");
									document.write("@font-face{font-family: 'MuseoSans-700Italic';src:url(\"" + wfpath + "17731ee6c73c6528f6fe1d1ba76bc65c" + suffix + "_0.ttf\");font-weight:'normal';font-style:'normal';}\n");
									document.write("@font-face{font-family: 'MuseoSans-300Italic';src:url(\"" + wfpath + "14b2b66f68d2c5b0fc7ff95d82761a0a" + suffix + "_0.ttf\");font-weight:'normal';font-style:'normal';}\n");
									document.write("@font-face{font-family: 'MuseoSans-100Italic';src:url(\"" + wfpath + "3dd8b405fc8d6ef66c1e59953998cfe4" + suffix + "_0.ttf\");font-weight:'normal';font-style:'normal';}\n");
									document.write("@font-face{font-family: 'MuseoSans-500Italic';src:url(\"" + wfpath + "53d8cb2065b41de82faf78ac5b6d87a2" + suffix + "_0.ttf\");font-weight:'normal';font-style:'normal';}\n");
									document.write("@font-face{font-family: 'MuseoSans-900';src:url(\"" + wfpath + "9a2da39252f62962c7ad4a5b6ccc3166" + suffix + "_0.ttf\");font-weight:'normal';font-style:'normal';}\n");
						document.write("</style>");
		break;
		

		
	default:
		break;
}