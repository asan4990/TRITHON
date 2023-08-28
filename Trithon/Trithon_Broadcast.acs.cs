// Trithon (TRIBES & Python) Hybrid Scripts

// PLEASE DO NOT EDIT ANYTHING BELOW!
// Failure to adhere to these instructions could result in the program not functioning properly and TRIBES Hud's not updating.
// Disclaimer: I will not help you fix anything that is broken. Please, just don't do it.

$Trithon::Enabled = true;
$Trithon::ConnectionCreated = false;

function Trithon::Create(%port)
{
	if(!$Trithon::Enabled)
		Trithon::Echo("Please enable Trithon first.", "Error");
  
	if($Trithon::ConnectionCreated && $Trithon::Enabled)
		Trithon::Echo("Connection already created.", "Info");
	
	if(%port != "" && !$Trithon::ConnectionCreated)
	{
		if(Bov::createConnection(%port))
		{
		  $Trithon::ConnectionCreated = true;
		  Trithon::Echo("Created Connection on port: " @ %port, "Info");
		  Bov::broadcast("alive");
		}
	}
}

function Trithon::Function(%msg)
{
	if(!$Trithon::Enabled)
		Trithon::Echo("Please enable Trithon first.", "Error");
  
	if($Trithon::ConnectionCreated && %msg != "")
		Bov::broadcast(%msg);
}

function Trithon::Echo(%msg, %level)
{
	if(%level == "Error")
		%color = 2;
	else if(%level == "Info")
		%color = 3;
	
	if(%msg != "")
		echoc( %color, sprintf("[TRITHON]: %1", %msg) );
}

function Trithon::Toggle()
{
	$Trithon::Enabled = !$Trithon::Enabled;
	
	if(isObject(playGui))
		remoteBP( 2048, "[TRITHON] Scripts have been " @ ($Trithon::Enabled ? "enabled." : "disabled." ) );
	else
		Trithon::Echo( "Scripts have been " @ ($Trithon::Enabled ? "enabled." : "disabled." ) );
}

function Trithon::HeartBeat(%ping)
{
	$pref::HeartBeat = "pong";
}