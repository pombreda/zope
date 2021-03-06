﻿/*
 *  FlashvarManager.as
 *
 *  Manager for flashvars, use this instead of _level0.xxx to access a flashvar.
 *  Call collectFlashVars at the beginning of your application, the manager collects
 *  all variables on _level0, copies them to a object, decodes strings ('+' and '=')
 *  and parses numbers correctly...
 *
 *  @author <gerold.boehler@lovelysystems.com>
 *
 */
 
class z3c.reference.imagetool.core.FlashvarManager extends z3c.reference.imagetool.core.EventBroadcaster
{
	private static var _instance:z3c.reference.imagetool.core.FlashvarManager;
	private var flashVars:Object;
	
	
	function FlashvarManager()
	{
		flashVars = new Object();
	}
	
	public static function collectFlashVars():Void
	{
	    for (var flashvar in _level0)
	    {
	        if (flashvar.indexOf("$") == 0)
	            continue;

	        getInstance().setVar(flashvar, decodeForFlash(_level0[flashvar]));
	        delete _level0[flashvar];
	    }
	}
	
	private static function decodeForFlash(str:String)
	{
	    if (!isNaN(parseFloat(str)))
	        return parseFloat(str);
	        
	    if (typeof(str) == "boolean")
	        return str;

        if (str.toLowerCase() == "true" || str.toLowerCase() == "false")
            return str.toLowerCase() == "true";

		str = str.split("[p]").join("+");
		str = str.split("[e]").join("=");

		return str;
    }
	
	private function getVar(name:String):String
	{
		if (flashVars[name] != undefined)
			return flashVars[name];
			
		return undefined;
	}
	
	private function setVar(name:String, value:String):Void
	{
	    flashVars[name] = value;
	}

	public static function set(name:String, value)
	{
        getInstance().setVar(name, value);
	}
	
	public static function get(name:String)
	{
	    //if (!getInstance().getVar(name))
	    //    getInstance().log("!ERROR! Flashvar " + name + " not found!");

	    return getInstance().getVar(name);
	}
	
	public static function exists(name:String)
	{
	    return get(name) != undefined;
	}
	
	public static function getInstance():FlashvarManager
	{
		if (!_instance) 
			_instance = new FlashvarManager();
			
		return _instance;
	}	
}