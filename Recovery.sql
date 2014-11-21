DROP DATABASE IF EXISTS dbProjectRecovery;

CREATE DATABASE dbProjectRecovery;
USE dbProjectRecovery;

CREATE TABLE `Follow` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `follower` varchar(255) NOT NULL,
  `followee` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY USING HASH (`follower`),
  KEY USING HASH (`followee`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `Forum` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET utf8 NOT NULL,
  `short_name` varchar(255) NOT NULL,
  `user` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY USING HASH (`name`),
  UNIQUE KEY USING HASH (`short_name`),
  KEY USING HASH (`user`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;

CREATE TABLE `Post` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` datetime NOT NULL,
  `likes` int(11) NOT NULL DEFAULT '0',
  `dislikes` int(11) NOT NULL DEFAULT '0',
  `forum` varchar(255) NOT NULL,
  `path` varchar(255) NOT NULL DEFAULT '',
  `isApproved` tinyint(1) NOT NULL DEFAULT '0',
  `isDeleted` tinyint(1) NOT NULL DEFAULT '0',
  `isEdited` tinyint(1) NOT NULL DEFAULT '0',
  `isHighlighted` tinyint(1) NOT NULL DEFAULT '0',
  `isSpam` tinyint(1) NOT NULL DEFAULT '0',
  `message` text NOT NULL,
  `user` varchar(255) NOT NULL,
  `parent` int(11) DEFAULT NULL,
  `points` int(11) NOT NULL DEFAULT '0',
  `thread` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY USING HASH (`forum`),
  KEY USING HASH (`user`),
  KEY USING HASH (`date`),
  KEY (`thread`)
  
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;

CREATE TABLE `Thread` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` datetime NOT NULL,
  `dislikes` int(11) NOT NULL DEFAULT '0',
  `likes` int(11) NOT NULL DEFAULT '0',
  `isClosed` tinyint(1) NOT NULL DEFAULT '0',
  `isDeleted` tinyint(1) NOT NULL DEFAULT '0',
  `points` int(11) NOT NULL DEFAULT '0',
  `posts` int(11) NOT NULL DEFAULT '0',
  `slug` varchar(255) NOT NULL,
  `title` varchar(255) CHARACTER SET utf8 NOT NULL,
  `user` varchar(255) NOT NULL,
  `message` text NOT NULL,
  `forum` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY USING HASH(`forum`),
  KEY USING HASH(`slug`),
  KEY USING HASH(`user`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;

CREATE TABLE `Subscribe` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user` varchar(255) NOT NULL,
  `thread` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY (`thread`),
  KEY USING HASH(`user`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;


CREATE TABLE `User` (
  `about` text NOT NULL,
  `email` varchar(255) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `isAnonymous` tinyint(1) NOT NULL DEFAULT '0',
  `name` varchar(255) CHARACTER SET utf8 NOT NULL,
  `username` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY USING HASH (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;


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
