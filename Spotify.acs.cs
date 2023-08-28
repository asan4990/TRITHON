$move = 0;

function SpotifyHUD::GameBinds::Init() after GameBinds::Init
{
	$GameBinds::CurrentMapHandle = GameBinds::GetActionMap2( "actionMap.sae");
	$GameBinds::CurrentMap = "actionMap.sae";
	GameBinds::addBindCommand( "SpotifyHUD Toggle", "SpotifyHUD::Toggle();");
}

function SpotifyHUD::Toggle() 
{
	$SpotifyHUD::Toggle = !$SpotifyHUD::Toggle;

	%id = Control::getId("Spotify::Container");
	
	if(!$SpotifyHUD::Toggle) {
		%id.visible = false;
		PopActionMap("Spotify.sae");
	} else {
		%id.visible = true;
		SpotifyHUD::Load();
		SpotifyHUD::Keybind();
	}
}

function SpotifyHUD::Init()
{
	if($SpotifyHUD::Loaded)
		return;
	
	$SpotifyHUD::Loaded = true;
	
	HUD::New("Spotify::Container", 20, 20, 400, 169, SpotifyHUD::Wake, SpotifyHUD::Sleep);

	$Spotify::PC = newObject("Spotify::BG", SimGui::Control, 0, 0, 400, 169);
	
	// Image containers
	$BG = newObject("Spotify::BGContainer", FearGuiFormattedText, 0, 0, 864, 512);
	
	newObject("Spotify::Cover", FearGuiFormattedText, 0, 30, 84, 84);
	
	newObject("Spotify::Block", FearGuiFormattedText, 84, 30, 22, 84);
	
	newObject("Spotify::Artists", FearGuiFormattedText, 112, 64, 462, 22);
	newObject("Spotify::Artists2", FearGuiFormattedText, 401, 64, 462, 22);
	
	newObject("Spotify::Title", FearGuiFormattedText, 112, 38, 262, 22);

	newObject("Spotify::CurrentPos", FearGuiFormattedText, 110, 88, 50, 22);
	
	newObject("Spotify::Duration", FearGuiFormattedText, 358, 88, 50, 22);	

	newObject("Spotify::ProgressBarBG", FearGuiFormattedText, 142, 95, 50, 22);
	newObject("Spotify::ProgressBar", FearGuiFormattedText, 142, 95, 50, 22);

	addToSet("Spotify::Container", $Spotify::PC);
	addToSet($Spotify::PC, "Spotify::BGContainer");
	addToSet($Spotify::PC, "Spotify::Artists");
	addToSet($Spotify::PC, "Spotify::Artists2");
	addToSet($Spotify::PC, "Spotify::Cover");
	addToSet($Spotify::PC, "Spotify::Block");
	addToSet($Spotify::PC, "Spotify::Title");
	addToSet($Spotify::PC, "Spotify::CurrentPos");
	addToSet($Spotify::PC, "Spotify::Duration");
	addToSet($Spotify::PC, "Spotify::ProgressBarBG");
	addToSet($Spotify::PC, "Spotify::ProgressBar");
	
	Control::SetValue("Spotify::BGContainer", "<b0,0:Modules/Spotify/spotify_test.png>");
	Control::SetValue("Spotify::Cover", "<b0,0:Modules/Spotify/temp/album1.png>");
	Control::SetValue("Spotify::Block", "<b0,0:Modules/Spotify/spotify_block.png>");
	Control::SetValue("Spotify::ProgressBarBG", "<b0,0:Modules/Spotify/Tribify-bg-skinny.png>");
	Control::SetValue("Spotify::ProgressBar", "<b0,0:Modules/Spotify/Tribify-bar-skinny.png>");
	
	%ProgressBar = Control::getId("Spotify::ProgressBar");
	%ProgressBar.extent = "0 22";
	
	Control::SetValue("Spotify::Duration", "");
	Control::SetValue("Spotify::CurrentPos", "");
	
	Control::SetVisible("Spotify::Container", false);
}

function SpotifyHUD::Wake() { return; }
function SpotifyHUD::Sleep() { return; }

function SpotifyHUD::Load()
{		
	Control::SetValue("Spotify::Duration", "");
	Control::SetValue("Spotify::CurrentPos", "");
	
	Bov::setTextFormatFont(Spotify::Duration, 3, "if_w_8.pft");
	Control::SetValue("Spotify::Duration", "<f3>-:--");

	Bov::setTextFormatFont(Spotify::CurrentPos, 3, "if_w_8.pft");
	Control::SetValue("Spotify::CurrentPos", "<f3>-:--");
	
	Trithon::Function("spotifyGrab");
	
	
	Schedule::Cancel("Scroll");
	SpotifyHUD::UpdateTitle();
	SpotifyHUD::Cover();
	
	//SpotifyHUD::LoopData();
}

function SpotifyHUD::LoopData() {
	Schedule::Add("Trithon::Function(\"spotifyGrab\");", 5.0, "SpotifyDataLoop");
}

// TRITHON Function
function GetCurrentPos(%time)
{
	if(Control::GetVisible("Spotify::Container"))
	{
		%cur_pos = %time;
		%duration = $pref::SongDur;
		
		%get_mins = getWord(String::Replace(%cur_pos, ":", " "), 0);
		%get_secs = getWord(String::Replace(%cur_pos, ":", " "), 1);
		%a_curpos = ( (%get_mins * 60) + %get_secs );
		
		%a_count = floor( ( (%a_curpos / $pref::SongProSecs) * 200) );
			
		if( (%a_count == 200) || (%a_count == 199) )
			$pref::NewSong = true;
		
		if($pref::NewSong)
		{
			%a_count = -1;
			$pref::NewSong = false;
			SpotifyHUD::Cleanup();
			Trithon::Function("spotifyGrab");
		}
		
			
		Bov::setTextFormatFont(Spotify::CurrentPos, 3, "if_w_8.pft"); // sf_white_10
		Control::SetValue("Spotify::CurrentPos", "<f3>" @ %cur_pos);
		
		Bov::setTextFormatFont(Spotify::Duration, 3, "if_w_8.pft"); // sf_white_10
		Control::SetValue("Spotify::Duration", "<f3>" @ %duration);
	
		Bov::setTextFormatFont(Spotify::ProgressBar, 3, "if_w_8.pft");
		Control::SetExtent("Spotify::ProgressBar", %a_count, 22);
	}
}

// TRITHON Function
function GetSongData(%artists, %song, %duration, %state)
{
	$pref::SongArtists = %artists;
	$pref::SongName = %song;
	$pref::SongDur = %duration;
	$pref::SongState = %state;
}

function SpotifyHUD::Cleanup()
{
	deleteVariables("$pref::Song*");
	
	%ProgressBar = Control::getId("Spotify::ProgressBar");
	%ProgressBar.extent = "0 22";
	
	if($pref::SongState == "Playing")
		$prog_bar = "";
}

function SpotifyHUD::UpdateTitle()
{	
	// Grab for progress bar (KEEP THIS!)
	%get_mins = getWord(String::Replace($pref::SongDur, ":", " "), 0);
	%get_secs = getWord(String::Replace($pref::SongDur, ":", " "), 1);
	$pref::SongProSecs = ( (%get_mins * 60) + %get_secs );

	%title = $pref::SongName;
	%artists = $pref::SongArtists;
	
	if(String::Length(%title) > 25)
		%title = String::Left(%title, 25) @ "...";
	
	if(String::Length(%artists) > 45)
	{
		%artists = String::Left(%artists, 45) @ "...";
		SpotifyHUD::ScrollText();
	}
	
	Control::SetValue("Spotify::Artists", "");
	Control::SetValue("Spotify::Title", "");

	Bov::setTextFormatFont(Spotify::Artists, 3, "sf_white_9.pft");
	Control::SetValue("Spotify::Artists", "<f3>" @ %artists);

	Bov::setTextFormatFont(Spotify::Title, 3, "sf_white_12.pft");
	Control::SetValue("Spotify::Title", "<f3>" @ %title);
}

function SpotifyHUD::Cover()
{
	//if(Control::GetVisible("Spotify::Container"))
	//{
		if(isObject("playGui\\Spotify::Container\\Spotify::BG\\Spotify::Cover"))
		{
			removeFromSet("Spotify::Container\\Spotify::BG\\Spotify::Cover");
			deleteObject("playGui\\Spotify::Container\\Spotify::BG\\Spotify::Cover");
		}
		
		purgeResources(true);
		purgeResources(true);
		
		%obj = newObject("Spotify::Cover", FearGuiFormattedText, 0, 30, 84, 84);
		
		addToSet("playGui\\Spotify::Container\\Spotify::BG", "Spotify::Cover");
		
		Control::SetValue("Spotify::Cover", "<b0,0:Modules/Spotify/temp/album1.png>");
	//}
}

function SpotifyHUD::ScrollText()
{
	%text = Control::getId("Spotify::Artists");
	%text2 = Control::getId("Spotify::Artists2");
	
	%text.x = getWord(%text.position, 0);
	%text.y = getWord(%text.position, 1);
	
	%text2.x = getWord(%text2.position, 0);
	%text2.y = getWord(%text2.position, 1);
	
	%text.w = getWord(%text.extent, 0);
	
	%text.position = (%text.x - 1) @ " " @ %text.y;
	//%text2.position = (%text2.x - 1) @ " " @ %text2.y;
	
	//echoc(3, %text2.x);
	
	if(%text.x <= -300) {
		%text.position = 401 @ " " @ %text.y;
	}
	//} else if(%text2.x <= -200) {
	//	%text2.position = 662 @ " " @ %text2.y;
	//}
	
	Bov::setTextFormatFont(Spotify::Artists, 3, "sf_white_9.pft");
	Control::SetValue("Spotify::Artists", "<f3>" @ $pref::SongArtists);
		
	//Bov::setTextFormatFont(Spotify::Artists2, 2, "sf_yellow_9.pft");
	Control::SetValue("Spotify::Artists2", "");
	
	Schedule::Add("SpotifyHUD::ScrollText();", 0.075, "Scroll");
}

function SpotifyHUD::Keybind()
{
	NewActionMap("Spotify.sae");
	PushActionMap("Spotify.sae");
	
	// Play / Pause
	bindCommand( keyboard, make, "control", space, TO, "Trithon::Function(\"spotifyPlay\");" );
	bindCommand( keyboard, break, "control", space, TO, "" );
	
	// Next track
	bindCommand( keyboard, make, "right", TO, "Trithon::Function(\"spotifyNext\");" );
	bindCommand( keyboard, break, "right", TO, "" );
	
	// Prev track
	bindCommand( keyboard, make, "left", TO, "Trithon::Function(\"spotifyPrev\");" );
	bindCommand( keyboard, break, "left", TO, "" );
	
	// Prev track
	bindCommand( keyboard, make, "up", TO, "Trithon::Function(\"spotifyVolUp\");" );
	bindCommand( keyboard, break, "up", TO, "" );
	
}

function String::repeat(%chr, %count)
{
	%tchar = "";
	for(%i = 0; %i <= %count; %i++)
		%tchar = %tchar @ %chr;
	return %tchar;
}

SpotifyHUD::Init();