show databases;
use `cloudchatdb`;
select * from `IRC_servers`;
/*insert into `IRC_servers` (serverSessionID, nickname, isAway, isConnected, serverName, serverIP, serverPort, useSSL, Registred_users_userID)
values (-1, "testicek", 0, 0, "Rizon", "irc.rizon.net", "6667", 0, 1);*/

#delete from `IRC_servers` where `serverID` = 1;