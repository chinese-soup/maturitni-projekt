SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

CREATE SCHEMA IF NOT EXISTS `mydb` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci ;
USE `mydb` ;

-- -----------------------------------------------------
-- Table `mydb`.`Registred_users`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `mydb`.`Registred_users` ;

CREATE  TABLE IF NOT EXISTS `mydb`.`Registred_users` (
  `userID` INT NOT NULL AUTO_INCREMENT ,
  `email` VARCHAR(24) NOT NULL ,
  `password` VARCHAR(4096) NOT NULL ,
  `isActivated` TINYINT(1) NOT NULL ,
  `registredDate` TIME NOT NULL ,
  PRIMARY KEY (`userID`, `registredDate`) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`User_settings`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `mydb`.`User_settings` ;

CREATE  TABLE IF NOT EXISTS `mydb`.`User_settings` (
  `show_previews` TINYINT(1) NULL ,
  `higlight_words` VARCHAR(1024) NULL ,
  `whois_username` VARCHAR(45) NULL DEFAULT 'user' ,
  `whois_realname` VARCHAR(45) NULL DEFAULT 'realname' ,
  `global_nickname` VARCHAR(45) NULL ,
  `Registred_users_userID` INT NOT NULL ,
  `autohide_channels` TINYINT(1) NULL ,
  `hide_joinpartquit_messages` TINYINT(1) NULL ,
  `show_seconds` TINYINT(1) NULL ,
  INDEX `fk_User_settings_Registred_users_idx` (`Registred_users_userID` ASC) ,
  PRIMARY KEY (`Registred_users_userID`) ,
  CONSTRAINT `fk_User_settings_Registred_users`
    FOREIGN KEY (`Registred_users_userID` )
    REFERENCES `mydb`.`Registred_users` (`userID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`Activation_keys`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `mydb`.`Activation_keys` ;

CREATE  TABLE IF NOT EXISTS `mydb`.`Activation_keys` (
  `signup_time` DATETIME NOT NULL ,
  `type` TINYINT(1) NOT NULL ,
  `key` VARCHAR(45) NOT NULL ,
  `expired` TINYINT(1) NOT NULL DEFAULT 0 ,
  `ID` INT NOT NULL AUTO_INCREMENT ,
  `Registred_users_userID` INT NOT NULL ,
  PRIMARY KEY (`ID`) ,
  INDEX `fk_Activation_keys_Registred_users1_idx` (`Registred_users_userID` ASC) ,
  CONSTRAINT `fk_Activation_keys_Registred_users1`
    FOREIGN KEY (`Registred_users_userID` )
    REFERENCES `mydb`.`Registred_users` (`userID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`IRC_servers`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `mydb`.`IRC_servers` ;

CREATE  TABLE IF NOT EXISTS `mydb`.`IRC_servers` (
  `serverID` INT NOT NULL AUTO_INCREMENT ,
  `serverSessionID` INT NOT NULL ,
  `nickname` VARCHAR(45) NULL COMMENT 'Custom server nickname in case the user doesn\'t want to use the global one.' ,
  `isAway` TINYINT(1) NULL ,
  `isConnected` TINYINT(1) NOT NULL ,
  `Registred_users_userID` INT NOT NULL ,
  PRIMARY KEY (`serverID`, `Registred_users_userID`) ,
  INDEX `fk_IRC_servers_Registred_users1_idx` (`Registred_users_userID` ASC) ,
  CONSTRAINT `fk_IRC_servers_Registred_users1`
    FOREIGN KEY (`Registred_users_userID` )
    REFERENCES `mydb`.`Registred_users` (`userID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`IRC_channels`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `mydb`.`IRC_channels` ;

CREATE  TABLE IF NOT EXISTS `mydb`.`IRC_channels` (
  `channelID` INT NOT NULL ,
  `channelName` VARCHAR(45) NOT NULL ,
  `isJoined` TINYINT(1) NOT NULL ,
  `lastOpened` DATETIME NOT NULL ,
  `IRC_servers_serverID` INT NOT NULL ,
  PRIMARY KEY (`channelID`) ,
  INDEX `fk_IRC_channels_IRC_servers1_idx` (`IRC_servers_serverID` ASC) ,
  CONSTRAINT `fk_IRC_channels_IRC_servers1`
    FOREIGN KEY (`IRC_servers_serverID` )
    REFERENCES `mydb`.`IRC_servers` (`serverID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`User_data`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `mydb`.`User_data` ;

CREATE  TABLE IF NOT EXISTS `mydb`.`User_data` (
  `lastLogin` DATETIME NULL ,
  `lastLogoff` DATETIME NULL ,
  `isSocketOn` TINYINT(1) NOT NULL ,
  `Registred_users_userID` INT NOT NULL ,
  PRIMARY KEY (`Registred_users_userID`) ,
  CONSTRAINT `fk_User_data_Registred_users1`
    FOREIGN KEY (`Registred_users_userID` )
    REFERENCES `mydb`.`Registred_users` (`userID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`IRC_other_messages`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `mydb`.`IRC_other_messages` ;

CREATE  TABLE IF NOT EXISTS `mydb`.`IRC_other_messages` (
  `messageID` VARCHAR(255) NOT NULL ,
  `fromHostmask` VARCHAR(45) NOT NULL ,
  `messageBody` VARCHAR(4096) NOT NULL ,
  `commandType` VARCHAR(45) NOT NULL ,
  `timeReceived` DATETIME NOT NULL ,
  `seen` DATETIME NULL ,
  `IRC_servers_serverID` INT NOT NULL ,
  `attachmentID` INT NULL ,
  PRIMARY KEY (`messageID`) ,
  INDEX `fk_IRC_other_messages_IRC_servers1_idx` (`IRC_servers_serverID` ASC) ,
  CONSTRAINT `fk_IRC_other_messages_IRC_servers1`
    FOREIGN KEY (`IRC_servers_serverID` )
    REFERENCES `mydb`.`IRC_servers` (`serverID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`IRC_channel_messages`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `mydb`.`IRC_channel_messages` ;

CREATE  TABLE IF NOT EXISTS `mydb`.`IRC_channel_messages` (
  `messageID` INT NOT NULL ,
  `fromHostmask` VARCHAR(45) NOT NULL ,
  `messageBody` VARCHAR(4096) NOT NULL ,
  `commandType` VARCHAR(45) NOT NULL ,
  `timeReceived` DATETIME NOT NULL ,
  `seen` DATETIME NULL ,
  `IRC_channels_channelID` INT NOT NULL ,
  `IRC_channels_IRC_servers_serverID` INT NOT NULL ,
  `attachmentID` INT NULL ,
  PRIMARY KEY (`messageID`) ,
  INDEX `fk_IRC_channel_messages_IRC_channels1_idx` (`IRC_channels_channelID` ASC, `IRC_channels_IRC_servers_serverID` ASC) ,
  CONSTRAINT `fk_IRC_channel_messages_IRC_channels1`
    FOREIGN KEY (`IRC_channels_channelID` , `IRC_channels_IRC_servers_serverID` )
    REFERENCES `mydb`.`IRC_channels` (`channelID` , `IRC_servers_serverID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`Messages_attachments`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `mydb`.`Messages_attachments` ;

CREATE  TABLE IF NOT EXISTS `mydb`.`Messages_attachments` (
  `attachmentID` INT NOT NULL AUTO_INCREMENT ,
  `attachmentType` VARCHAR(45) NULL ,
  `attachmentURI` VARCHAR(1024) NULL ,
  `attachmentPreviewURI` VARCHAR(1024) NULL ,
  `attachmentTitle` VARCHAR(256) NULL ,
  PRIMARY KEY (`attachmentID`) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`IRC_queries`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `mydb`.`IRC_queries` ;

CREATE  TABLE IF NOT EXISTS `mydb`.`IRC_queries` (
  `fromHostmask` VARCHAR(45) NOT NULL ,
  `fromNickname` VARCHAR(45) NULL COMMENT 'possily redundant' ,
  `lastOpened` DATETIME NULL ,
  `IRC_servers_serverID` INT NOT NULL ,
  PRIMARY KEY (`fromHostmask`, `IRC_servers_serverID`) ,
  INDEX `fk_IRC_queries_IRC_servers1_idx` (`IRC_servers_serverID` ASC) ,
  CONSTRAINT `fk_IRC_queries_IRC_servers1`
    FOREIGN KEY (`IRC_servers_serverID` )
    REFERENCES `mydb`.`IRC_servers` (`serverID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`IRC_query_messages`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `mydb`.`IRC_query_messages` ;

CREATE  TABLE IF NOT EXISTS `mydb`.`IRC_query_messages` (
  `messageID` INT NOT NULL AUTO_INCREMENT ,
  `fromHostmask` VARCHAR(45) NOT NULL ,
  `messageBody` VARCHAR(4096) NOT NULL ,
  `commandType` VARCHAR(45) NOT NULL ,
  `timeReceived` DATETIME NOT NULL ,
  `seen` DATETIME NULL ,
  `IRC_queries_fromHostmask` INT NOT NULL ,
  `IRC_queries_IRC_servers_serverID` INT NOT NULL ,
  PRIMARY KEY (`messageID`) ,
  INDEX `fk_IRC_query_messages_IRC_queries1_idx` (`IRC_queries_fromHostmask` ASC, `IRC_queries_IRC_servers_serverID` ASC) ,
  CONSTRAINT `fk_IRC_query_messages_IRC_queries1`
    FOREIGN KEY (`IRC_queries_fromHostmask` , `IRC_queries_IRC_servers_serverID` )
    REFERENCES `mydb`.`IRC_queries` (`fromHostmask` , `IRC_servers_serverID` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

USE `mydb` ;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
