#create database `cloudchatdb`
#	DEFAULT CHARACTER SET utf8
#    DEFAULT COLLATE utf8_general_ci;
select * from `IRC_channels`;
#delete from `IRC_channels` where  `channelID` = 3;
select * from `IRC_channel_messages` where `IRC_channels_channelID` = 3;
