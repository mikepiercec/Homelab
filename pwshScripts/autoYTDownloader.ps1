#!/usr/lib/powershell/pwsh

<#
        First version of my yt-dlp automation. Probably should be rewritten in Python but I know PowerShell better and wanted to slap something together quickly
        No error handling or recovery here. I imagine it will break when downloading lots of videos from YouTube or a long period of time.
        Channels are specified by directory names on my share drive.
#>
$folders = Get-ChildItem -Path \mnt\S_Drive\yt-dlp | Where-Object -Property Mode -Like 'd-*' | Select-Object -ExpandProperty Name

$channels = foreach ($folder in $folders)
        {
                [PSCustomObject]@{
                    Channel = $folder
                    Results = yt-dlp --skip-download --get-id --get-title --flat-playlist "https://www.youtube.com/@$folder"
                }
        }
$videolist = foreach ($channel in $channels)
{
        $count = 1
        $extensions = foreach ($video in $channel.Results)
        {
	            $math = $count / 2
	            if ($math -is [int32])
	            {
		                Write-Output -InputObject $video	
	            }
	            ++$count
        }
        $count = 1
        $titles = foreach ($video in $channel.Results)
        {
	            $math = $count / 2
                if ($math -is [System.Double])
                {
                        Write-Output -InputObject $video        
                }
                ++$count
        }
        for ($i = 0; $i -le ($titles.Count - 1); $i++)
        {
                [PSCustomObject]@{
                        Title = $titles[$i]
                        Extension = $extensions[$i]
                        Channel = $channel.Channel
                }
        }
}
# Write-Output -InputObject ($videolist | Format-Table)
$videos = Get-ChildItem -Path \mnt\S_Drive\yt-dlp -Recurse | Where-Object -Property Mode -NotLike 'd-*' | Select-Object -ExpandProperty BaseName
foreach ($video in $videolist)
{
        if ($videos -notcontains $video)
        {
                yt-dlp -o "/mnt/S_Drive/yt-dlp/$($video.Channel)/%($($video.Title))s.%(ext)s" "https://www.youtube.com/watch?v=$($video.Extension)"
        }
}