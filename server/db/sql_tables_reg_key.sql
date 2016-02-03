use mydb;
show columns in `Activation_keys`;
insert into `Activation_keys` (`signup_time`, `type`, `key`, `expired`, `ID`, `Registred_users_userID`) 
values(CURRENT_TIMESTAMP, 1, "asdfasdfasdfasdf", 1, 1, 1) ;
