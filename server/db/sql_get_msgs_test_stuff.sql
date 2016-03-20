show processlist;
use `cloudchatdb`;
#select * from `IRC_servers`;
#select * from `Registered_users`;
#delete from `IRC_channels` where `IRC_servers_serverID` = 3;
#delete from `IRC_servers` where serverID = 3;
#ALTER TABLE `IRC_channels` ADD UNIQUE KEY `channelNameOnlyOncePerServer` (`channelName`, `IRC_servers_serverID`);
#select * from `IRC_channel_messages`;
select DATE_FORMAT(FROM_UNIXTIME('1458491199000'), '%e %b %Y');
(SELECT * FROM `IRC_channel_messages`
                    WHERE `IRC_channels_channelID` = 2
					AND `timeReceived` >= DATE_FORMAT(FROM_UNIXTIME('1458491199'), '%Y-%m-%d %H:%M:%S')
                    ORDER BY `messageID` DESC LIMIT 20)
                    ORDER BY `messageID` ASC;

SELECT CONVERT_TZ(FROM_UNIXTIME(1277942400), @@session.time_zone,'UTC');                 


(SELECT * FROM `IRC_channel_messages`
                    WHERE `IRC_channels_channelID` = 1
                    ORDER BY `messageID` DESC LIMIT 10)
                    ORDER BY `messageID` ASC;

