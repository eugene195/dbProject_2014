DROP DATABASE IF EXISTS dbISAM;

CREATE DATABASE dbISAM;
USE dbISAM;

CREATE TABLE `Follow` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `follower` CHAR(25) NOT NULL,
  `followee` CHAR(25) NOT NULL,
  PRIMARY KEY (`id`),
  KEY USING HASH (`follower`),
  KEY USING HASH (`followee`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE TABLE `Forum` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` CHAR(35) NOT NULL,
  `short_name` CHAR(35) NOT NULL,
  `user` CHAR(25) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY USING HASH (`name`),
  UNIQUE KEY USING HASH (`short_name`),
  KEY USING HASH (`user`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;

CREATE TABLE `Post` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `date` DATETIME NOT NULL,
  `likes` SMALLINT NOT NULL DEFAULT '0',
  `dislikes` SMALLINT NOT NULL DEFAULT '0',
  `forum` CHAR(35) NOT NULL,
  `path` CHAR(40) NOT NULL DEFAULT '',
  `isApproved` tinyint(1) NOT NULL DEFAULT '0',
  `isDeleted` tinyint(1) NOT NULL DEFAULT '0',
  `isEdited` tinyint(1) NOT NULL DEFAULT '0',
  `isHighlighted` tinyint(1) NOT NULL DEFAULT '0',
  `isSpam` tinyint(1) NOT NULL DEFAULT '0',
  `message` TEXT NOT NULL,
  `user` CHAR(25) NOT NULL,
  `parent` INT(11) DEFAULT NULL,
  `points` SMALLINT NOT NULL DEFAULT '0',
  `thread` INT(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY (`parent`),
  KEY USING HASH (`forum`),
  KEY (`user`, `date`),
  KEY (`forum`, `date`),
  KEY (`forum`, `user`),
  KEY (`thread`, `date`)
  
) ENGINE=MyISAM AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;

CREATE TABLE `Thread` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `date` DATETIME NOT NULL,
  `dislikes` SMALLINT NOT NULL DEFAULT '0',
  `likes` SMALLINT NOT NULL DEFAULT '0',
  `isClosed` tinyint(1) NOT NULL DEFAULT '0',
  `isDeleted` tinyint(1) NOT NULL DEFAULT '0',
  `points` SMALLINT NOT NULL DEFAULT '0',
  `posts` SMALLINT NOT NULL DEFAULT '0',
  `slug` CHAR(40) NOT NULL,
  `title` CHAR(40) CHARACTER SET utf8 NOT NULL,
  `user` CHAR(25) NOT NULL,
  `message` TEXT NOT NULL,
  `forum` CHAR(35) NOT NULL,
  `removedPosts` SMALLINT NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY USING HASH(`slug`),
  KEY (`user`, `date`),
  KEY USING HASH (`forum`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;

CREATE TABLE `Subscribe` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `user` CHAR(25) NOT NULL,
  `thread` INT(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY (`thread`),
  KEY USING HASH(`user`)
) ENGINE=MyISAM AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;


CREATE TABLE `User` (
  `about` text NOT NULL,
  `email` char(25) NOT NULL,
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `isAnonymous` tinyint(1) NOT NULL DEFAULT '0',
  `name` CHAR(25) NOT NULL,
  `username` CHAR(25) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY USING HASH (`email`),
  KEY USING HASH (`name`)
) ENGINE=MyISAM AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;


DROP TRIGGER IF EXISTS ins_post;
CREATE TRIGGER ins_post
BEFORE INSERT ON `Post`
FOR EACH ROW
UPDATE `Thread` SET `posts` = `posts` + 1 WHERE `id` = NEW.`thread`;

ALTER TABLE Follow
ADD FOREIGN KEY (`follower`)
REFERENCES User (`email`);

ALTER TABLE Follow
ADD FOREIGN KEY (`followee`)
REFERENCES User (`email`);

ALTER TABLE Forum
ADD FOREIGN KEY (`user`)
REFERENCES User (`email`);

ALTER TABLE Post
ADD FOREIGN KEY (`forum`)
REFERENCES Forum (`short_name`);

ALTER TABLE Post
ADD FOREIGN KEY (`user`)
REFERENCES User (`email`);

ALTER TABLE Post
ADD FOREIGN KEY (`thread`)
REFERENCES Thread (`id`);

ALTER TABLE Thread
ADD FOREIGN KEY (`forum`)
REFERENCES Forum (`short_name`);

ALTER TABLE Thread
ADD FOREIGN KEY (`user`)
REFERENCES User (`email`);

ALTER TABLE Subscribe
ADD FOREIGN KEY (`thread`)
REFERENCES Thread (`id`);

ALTER TABLE Subscribe
ADD FOREIGN KEY (`user`)
REFERENCES User (`email`);
