show databases;
use `cloudchatdb`;
#select * from `IRC_servers` INNER JOIN `IRC_channels` ON `Registred_users_userID`;
#select * from `IRC_channels` where `IRC_servers_serverID` = 1;
select * from `IRC_channel_messages` where `IRC_channels_channelID` = 1;
#select * from `IRC_servers`;

#insert into `IRC_servers` (serverSessionID, nickname, isAway, isConnected, serverName, serverIP, serverPort, useSSL, serverPassword, Registred_users_userID)
#values (-1, "rizonak", 0, 0, "Rizon", "irc.rizon.net", "6667", 0, NULL, 1);

#delete from `IRC_servers` where `serverID` = 1;

#UPDATE `IRC_servers` SET serverName="asdf", nickname="", serverPassword="", serverIP="irc.freenode.org", serverPort=6997, useSSL=true
#WHERE `serverID` = 3;

	

#INSERT INTO `IRC_channels` (channelName, channelPassword, isJoined, lastOpened, IRC_servers_serverID) values ("#test.cz", "", 0, CURRENT_TIMESTAMP, 15);

SET SQL_SAFE_UPDATES=0;
#delete from `IRC_servers`;
#select * from `IRC_servers`;

select * from `IRC_channels` where `IRC_servers_serverID` = 15;
select * from `IRC_channel_messages`;
SELECT * FROM `IRC_channels` WHERE `channelID` = -1;
#delete from `User_settings` where `Registred_users_userID` = 1;
#INSERT INTO `User_settings` (show_previews, highlight_words, whois_username, whois_realname, global_nickname, autohide_channels, hide_joinpartquit_messages) VALUES(1, "A", 19)
#ON DUPLICATE KEY UPDATE show_previews="A", highlight_words=19, whois_username, whois_realname

#select * from INFORMATION_SCHEMA.COLUMNS where table_name = 'User_settings';
#delete from `IRC_servers` where `serverID` = 1;

/*insert into `IRC_servers` (serverSessionID, nickname, isAway, isConnected, serverName, serverIP, serverPort, useSSL, Registred_users_userID)
values (-1, "testicek", 0, 0, "Rizon", "irc.rizon.net", "6667", 0, 1);*/

#highlight_words, whois_username, whois_realname, global_nickname, hide_joinpartquit_messages, show_second, show_video_previews, show_image_previews, Registred_users_userID



