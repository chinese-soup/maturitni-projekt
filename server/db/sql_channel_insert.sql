show databases;
use `cloudchatdb`;
select * from `IRC_channels`;
insert into `IRC_channels` (channelName, channelPassword, isJoined, lastOpened, IRC_servers_serverID)
values("#test.cz", "", 1, CURRENT_TIMESTAMP, 1);